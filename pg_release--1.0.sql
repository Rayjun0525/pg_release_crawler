-- pg_release--1.0.sql
CREATE TABLE IF NOT EXISTS postgresql_release_notes (
    id SERIAL PRIMARY KEY,
    release_date DATE,
    version VARCHAR(10),
    section VARCHAR(100),
    subsection VARCHAR(100),
    subsubsection VARCHAR(100),
    content TEXT
);

CREATE OR REPLACE FUNCTION fetch_postgresql_releases(
    start_major INTEGER,
    end_major INTEGER DEFAULT NULL
)
RETURNS TEXT
AS 'MODULE_PATHNAME', 'pg_fetch_postgresql_releases'
LANGUAGE C STRICT;
