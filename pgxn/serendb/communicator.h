/*-------------------------------------------------------------------------
 *
 * communicator.h
 *	  internal interface for communicating with remote pageservers
 *
 *
 * Portions Copyright (c) 1996-2021, PostgreSQL Global Development Group
 * Portions Copyright (c) 1994, Regents of the University of California
 *
 *-------------------------------------------------------------------------
 */
#ifndef COMMUNICATOR_h
#define COMMUNICATOR_h

#include "serendb_pgversioncompat.h"

#include "storage/buf_internals.h"

#include "pagestore_client.h"

/* initialization at postmaster startup */
extern void pg_init_communicator(void);

/* initialization at backend startup */
extern void communicator_init(void);

extern bool communicator_exists(NRelFileInfo rinfo, ForkNumber forkNum,
								serendb_request_lsns *request_lsns);
extern BlockNumber communicator_nblocks(NRelFileInfo rinfo, ForkNumber forknum,
										serendb_request_lsns *request_lsns);
extern int64 communicator_dbsize(Oid dbNode, serendb_request_lsns *request_lsns);
extern void communicator_read_at_lsnv(NRelFileInfo rinfo, ForkNumber forkNum,
									  BlockNumber base_blockno, serendb_request_lsns *request_lsns,
									  void **buffers, BlockNumber nblocks, const bits8 *mask);
extern int communicator_prefetch_lookupv(NRelFileInfo rinfo, ForkNumber forknum, BlockNumber blocknum,
										 serendb_request_lsns *lsns,
										 BlockNumber nblocks, void **buffers, bits8 *mask);
extern void communicator_prefetch_register_bufferv(BufferTag tag, serendb_request_lsns *frlsns,
												   BlockNumber nblocks, const bits8 *mask);
extern bool communicator_prefetch_receive(BufferTag tag);

extern int communicator_read_slru_segment(SlruKind kind, int64 segno,
										  serendb_request_lsns *request_lsns,
										  void *buffer);

extern void communicator_reconfigure_timeout_if_needed(void);
extern void communicator_prefetch_pump_state(void);


#endif
