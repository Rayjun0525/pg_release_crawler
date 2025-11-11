EXTENSION = pg_release
MODULES = pg_release
DATA = pg_release--1.0.sql
PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

# Python 파일도 함께 설치
install:
	$(MAKE) -C src install
	mkdir -p $(DESTDIR)/usr/share/pg_release
	cp python/pg_release_crawler.py $(DESTDIR)/usr/share/pg_release/
