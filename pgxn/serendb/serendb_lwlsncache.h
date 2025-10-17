#ifndef SERENDB_LWLSNCACHE_H
#define SERENDB_LWLSNCACHE_H

#include "serendb_pgversioncompat.h"

void init_lwlsncache(void);

/* Hooks */
XLogRecPtr serendb_get_lwlsn(NRelFileInfo rlocator, ForkNumber forknum, BlockNumber blkno);
void serendb_get_lwlsn_v(NRelFileInfo relfilenode, ForkNumber forknum, BlockNumber blkno, int nblocks, XLogRecPtr *lsns);
XLogRecPtr serendb_set_lwlsn_block_range(XLogRecPtr lsn, NRelFileInfo rlocator, ForkNumber forknum, BlockNumber from, BlockNumber n_blocks);
XLogRecPtr serendb_set_lwlsn_block_v(const XLogRecPtr *lsns, NRelFileInfo relfilenode, ForkNumber forknum, BlockNumber blockno, int nblocks);
XLogRecPtr serendb_set_lwlsn_block(XLogRecPtr lsn, NRelFileInfo rlocator, ForkNumber forknum, BlockNumber blkno);
XLogRecPtr serendb_set_lwlsn_relation(XLogRecPtr lsn, NRelFileInfo rlocator, ForkNumber forknum);
XLogRecPtr serendb_set_lwlsn_db(XLogRecPtr lsn);

#endif /* SERENDB_LWLSNCACHE_H */