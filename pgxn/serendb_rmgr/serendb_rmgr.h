#ifndef SERENDB_RMGR_H
#define SERENDB_RMGR_H
#if PG_MAJORVERSION_NUM >= 16
#include "access/xlog_internal.h"
#include "replication/decode.h"
#include "replication/logical.h"

extern void serendb_rm_desc(StringInfo buf, XLogReaderState *record);
extern void serendb_rm_decode(LogicalDecodingContext *ctx, XLogRecordBuffer *buf);
extern const char *serendb_rm_identify(uint8 info);

#endif
#endif //SERENDB_RMGR_H
