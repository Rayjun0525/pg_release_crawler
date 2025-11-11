EXTENSION = pg_release
MODULE_big = pg_release
OBJS = src/pg_release.o
DATA = pg_release--1.0.sql
PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

python_install:
	mkdir -p $(DESTDIR)/usr/share/pg_release
	cp python/pg_release_crawler.py $(DESTDIR)/usr/share/pg_release/

all: $(MODULE_big).so

install-all: all install python_install
