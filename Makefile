EXTENSION = pg_release
MODULES = pg_release
DATA = pg_release--1.0.sql
PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

SRCDIR = src
OBJS = $(SRCDIR)/pg_release.o

install:
	$(MAKE) -C src install
	mkdir -p $(DESTDIR)/usr/share/pg_release
	cp python/pg_release_crawler.py $(DESTDIR)/usr/share/pg_release/
