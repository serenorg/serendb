#ifndef __WALSENDER_HOOKS_H__
#define __WALSENDER_HOOKS_H__

struct XLogReaderRoutine;
void		SerenDBOnDemandXLogReaderRoutines(struct XLogReaderRoutine *xlr);

#endif
