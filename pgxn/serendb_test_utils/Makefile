# pgxs/serendb_test_utils/Makefile


MODULE_big = serendb_test_utils
OBJS = \
	$(WIN32RES) \
	serendbtest.o

EXTENSION = serendb_test_utils
DATA = serendb_test_utils--1.3.sql
PGFILEDESC = "serendb_test_utils - helpers for SerenDB testing and debugging"

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
