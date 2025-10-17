/*-------------------------------------------------------------------------
 *
 * walsender_hooks.c
 *
 * Implements XLogReaderRoutine in terms of SerenDBWALReader. Allows for
 * fetching WAL from safekeepers, which normal xlogreader can't do.
 *
 *-------------------------------------------------------------------------
 */
#include "walsender_hooks.h"
#include "postgres.h"
#include "fmgr.h"
#include "access/xlogdefs.h"
#include "replication/walsender.h"
#include "access/xlog.h"
#include "access/xlog_internal.h"
#include "access/xlogreader.h"
#include "miscadmin.h"
#include "utils/wait_event.h"
#include "utils/guc.h"
#include "postmaster/interrupt.h"

#include "serendb.h"
#include "serendb_walreader.h"
#include "walproposer.h"

static SerenDBWALReader *wal_reader = NULL;

struct WalSnd;
extern struct WalSnd *MyWalSnd;
extern XLogRecPtr WalSndWaitForWal(XLogRecPtr loc);
extern bool GetDonorShmem(XLogRecPtr *donor_lsn);
extern XLogRecPtr GetXLogReplayRecPtr(TimeLineID *replayTLI);

bool disable_wal_prev_lsn_checks = false;

static XLogRecPtr
SerenDBWALReadWaitForWAL(XLogRecPtr loc)
{
	while (!SerenDBWALReaderUpdateDonor(wal_reader))
	{
		pg_usleep(1000);
		CHECK_FOR_INTERRUPTS();
	}

	// Walsender sends keepalives and stuff, so better use its normal wait
	if (MyWalSnd != NULL)
		return WalSndWaitForWal(loc);

	for (;;)
	{
		XLogRecPtr flush_ptr;
		if (!RecoveryInProgress())
#if PG_VERSION_NUM >= 150000
			flush_ptr = GetFlushRecPtr(NULL);
#else
			flush_ptr = GetFlushRecPtr();
#endif
		else
			flush_ptr = GetXLogReplayRecPtr(NULL);

		if (loc <= flush_ptr)
			return flush_ptr;

		CHECK_FOR_INTERRUPTS();
		pg_usleep(1000);
	}
}

static int
SerenDBWALPageRead(
				XLogReaderState *xlogreader,
				XLogRecPtr targetPagePtr,
				int reqLen,
				XLogRecPtr targetRecPtr,
				char *readBuf)
{
	XLogRecPtr	rem_lsn;

	/* Wait for flush pointer to advance past our request */
	XLogRecPtr	flushptr = SerenDBWALReadWaitForWAL(targetPagePtr + reqLen);
	int			count;

	if (flushptr < targetPagePtr + reqLen)
		return -1;

	xlogreader->skip_lsn_checks = disable_wal_prev_lsn_checks;

	/* Read at most XLOG_BLCKSZ bytes */
	if (targetPagePtr + XLOG_BLCKSZ <= flushptr)
		count = XLOG_BLCKSZ;
	else
		count = flushptr - targetPagePtr;

	/*
	 * Sometimes walsender requests non-monotonic sequences of WAL. If that's
	 * the case, we have to reset streaming from remote at the correct
	 * position. For example, walsender may try to verify the segment header
	 * when trying to read in the middle of it.
	 */
	rem_lsn = SerenDBWALReaderGetRemLsn(wal_reader);
	if (rem_lsn != InvalidXLogRecPtr && targetPagePtr != rem_lsn)
	{
		SerenDBWALReaderResetRemote(wal_reader);
	}

	for (;;)
	{
		SerenDBWALReadResult res = SerenDBWALRead(
											wal_reader,
											readBuf,
											targetPagePtr,
											count,
											SerenDBWALReaderLocalActiveTimeLineID(wal_reader));

		if (res == SERENDB_WALREAD_SUCCESS)
		{
			/*
			 * Setting ws_tli is required by the XLogReaderRoutine, it is used
			 * for segment name generation in error reports.
			 *
			 * ReadPageInternal updates ws_segno after calling cb on its own
			 * and XLogReaderRoutine description doesn't require it, but
			 * WALRead sets, let's follow it.
			 */
			xlogreader->seg.ws_tli = SerenDBWALReaderGetSegment(wal_reader)->ws_tli;
			xlogreader->seg.ws_segno = SerenDBWALReaderGetSegment(wal_reader)->ws_segno;

			/*
			 * ws_file doesn't exist in case of remote read, and isn't used by
			 * xlogreader except by WALRead on which we don't rely anyway.
			 */
			return count;
		}
		if (res == SERENDB_WALREAD_ERROR)
		{
			elog(ERROR, "[walsender] Failed to read WAL (req_lsn=%X/%X, len=%d): %s",
				 LSN_FORMAT_ARGS(targetPagePtr),
				 reqLen,
				 SerenDBWALReaderErrMsg(wal_reader));
			return -1;
		}

		/*
		 * Res is WOULDBLOCK, so we wait on the socket, recreating event set
		 * if necessary
		 */
		{

			pgsocket	sock = SerenDBWALReaderSocket(wal_reader);
			uint32_t	reader_events = SerenDBWALReaderEvents(wal_reader);
			long		timeout_ms = 1000;

			ResetLatch(MyLatch);
			CHECK_FOR_INTERRUPTS();
			if (ConfigReloadPending)
			{
				ConfigReloadPending = false;
				ProcessConfigFile(PGC_SIGHUP);
			}

			WaitLatchOrSocket(
							  MyLatch,
							  WL_LATCH_SET | WL_EXIT_ON_PM_DEATH | reader_events,
							  sock,
							  timeout_ms,
							  WAIT_EVENT_SERENDB_WAL_DL);
		}
	}
}

static void
SerenDBWALReadSegmentOpen(XLogReaderState *xlogreader, XLogSegNo nextSegNo, TimeLineID *tli_p)
{
	serendb_wal_segment_open(wal_reader, nextSegNo, tli_p);
	xlogreader->seg.ws_file = SerenDBWALReaderGetSegment(wal_reader)->ws_file;
}

static void
SerenDBWALReadSegmentClose(XLogReaderState *xlogreader)
{
	serendb_wal_segment_close(wal_reader);
	xlogreader->seg.ws_file = SerenDBWALReaderGetSegment(wal_reader)->ws_file;
}

void
SerenDBOnDemandXLogReaderRoutines(XLogReaderRoutine *xlr)
{
	/*
	 * If safekeepers are not configured, assume we don't need serendb_walreader,
	 * i.e. running SerenDB fork locally.
	 */
	if (wal_acceptors_list[0] == '\0')
		return;

	if (!wal_reader)
	{
		XLogRecPtr	basebackupLsn = GetRedoStartLsn();

		/* should never happen */
		if (basebackupLsn == 0)
		{
			elog(ERROR, "unable to start walsender when basebackupLsn is 0");
		}
		wal_reader = SerenDBWALReaderAllocate(wal_segment_size, basebackupLsn, "[walsender] ", 1);
	}
	xlr->page_read = SerenDBWALPageRead;
	xlr->segment_open = SerenDBWALReadSegmentOpen;
	xlr->segment_close = SerenDBWALReadSegmentClose;
}
