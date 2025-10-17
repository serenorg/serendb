#ifndef __SERENDB_WALREADER_H__
#define __SERENDB_WALREADER_H__

#include "access/xlogdefs.h"

/* forward declare so we don't have to expose the struct to the public */
struct SerenDBWALReader;
typedef struct SerenDBWALReader SerenDBWALReader;

/* avoid including walproposer.h as it includes us */
struct WalProposer;
typedef struct WalProposer WalProposer;

/* SerenDBWALRead return value */
typedef enum
{
	SERENDB_WALREAD_SUCCESS,
	SERENDB_WALREAD_WOULDBLOCK,
	SERENDB_WALREAD_ERROR,
} SerenDBWALReadResult;

extern SerenDBWALReader *SerenDBWALReaderAllocate(int wal_segment_size, XLogRecPtr available_lsn, char *log_prefix, TimeLineID tlid);
extern void SerenDBWALReaderFree(SerenDBWALReader *state);
extern void SerenDBWALReaderResetRemote(SerenDBWALReader *state);
extern TimeLineID SerenDBWALReaderLocalActiveTimeLineID(SerenDBWALReader *state);
extern SerenDBWALReadResult SerenDBWALRead(SerenDBWALReader *state, char *buf, XLogRecPtr startptr, Size count, TimeLineID tli);
extern pgsocket SerenDBWALReaderSocket(SerenDBWALReader *state);
extern uint32 SerenDBWALReaderEvents(SerenDBWALReader *state);
extern bool SerenDBWALReaderIsRemConnEstablished(SerenDBWALReader *state);
extern char *SerenDBWALReaderErrMsg(SerenDBWALReader *state);
extern XLogRecPtr SerenDBWALReaderGetRemLsn(SerenDBWALReader *state);
extern const WALOpenSegment *SerenDBWALReaderGetSegment(SerenDBWALReader *state);
extern bool serendb_wal_segment_open(SerenDBWALReader *state, XLogSegNo nextSegNo, TimeLineID *tli_p);
extern void serendb_wal_segment_close(SerenDBWALReader *state);
extern bool SerenDBWALReaderUpdateDonor(SerenDBWALReader *state);


#endif							/* __SERENDB_WALREADER_H__ */
