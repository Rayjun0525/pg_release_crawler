#include "postgres.h"
#include "fmgr.h"
#include <stdlib.h>

#ifdef PG_MODULE_MAGIC
PG_MODULE_MAGIC;
#endif

PG_FUNCTION_INFO_V1(pg_fetch_postgresql_releases);

Datum
pg_fetch_postgresql_releases(PG_FUNCTION_ARGS)
{
    int start_major = PG_GETARG_INT32(0);
    bool has_end = !PG_ARGISNULL(1);
    int end_major = has_end ? PG_GETARG_INT32(1) : -1;

    char cmd[512];
    if (has_end)
        snprintf(cmd, sizeof(cmd),
                 "python3 /usr/share/pg_release/pg_release_crawler.py %d %d",
                 start_major, end_major);
    else
        snprintf(cmd, sizeof(cmd),
                 "python3 /usr/share/pg_release/pg_release_crawler.py %d",
                 start_major);

    int ret = system(cmd);
    if (ret != 0)
        ereport(ERROR, (errmsg("pg_release_crawler.py failed with code %d", ret)));

    PG_RETURN_TEXT_P(cstring_to_text("✅ PostgreSQL release data fetched and loaded successfully"));
}
