# pgxs/serendb_utils/Makefile


MODULE_big = serendb_utils
OBJS = \
	$(WIN32RES) \
	serendb_utils.o

EXTENSION = serendb_utils
DATA = serendb_utils--1.0.sql
PGFILEDESC = "serendb_utils - small useful functions"

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
