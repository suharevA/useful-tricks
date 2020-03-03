#!/bin/sh


PGPASSWORD='you pass'
export PGPASSWORD
pathB=/var/lib/pgsql/9.6/archive/
dbUser=add user
database=database name

find $pathB \( -name "*-1[^5].*" -o -name "*-[023]?.*" \) -ctime +30 -delete
pg_dump -U $dbUser $database | gzip > $pathB/add name database_$(date "+%Y-%m-%d").sql.gz

unset PGPASSWORD
