# pgxs/serendb/Makefile


MODULE_big = serendb_rmgr
OBJS = \
	$(WIN32RES) \
	serendb_rmgr.o \
	serendb_rmgr_decode.o \
	serendb_rmgr_desc.o


EXTENSION = serendb_rmgr
DATA = 
PGFILEDESC = "SerenDB WAL Resource Manager - custom WAL records used to make SerenDB work (since PG 16)"


PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
