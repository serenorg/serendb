# pgxs/serendb_walredo/Makefile

MODULE_big = serendb_walredo
OBJS = \
	$(WIN32RES) \
	inmem_smgr.o \
	walredoproc.o \

# This really should be guarded by $(with_libseccomp), but I couldn't
# make that work with pgxs. So we always compile it, but its contents
# are wrapped in #ifdef HAVE_LIBSECCOMP instead.
OBJS += seccomp.o

PGFILEDESC = "serendb_walredo - helper process that runs in SerenDB pageserver"

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

ifeq ($(with_libseccomp),yes)
SHLIB_LINK += -lseccomp
endif
