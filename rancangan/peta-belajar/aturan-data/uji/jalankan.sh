#!/usr/bin/env bash
# Menjalankan uji aturan di database Postgres sementara.
# Pakai: PGHOST=/tmp PGPORT=54329 PGUSER=postgres bash uji/jalankan.sh
set -euo pipefail
cd "$(dirname "$0")"
DB=uji_aturan_$$
createdb "$DB"
trap 'dropdb --if-exists "$DB"' EXIT
psql -X -q -v ON_ERROR_STOP=1 -d "$DB" -f 00_tiruan_supabase.sql
psql -X -q -v ON_ERROR_STOP=1 -d "$DB" -f ../supabase/migrations/20261016000001_aturan_data.sql
psql -X -q -v ON_ERROR_STOP=1 -d "$DB" -f uji_aturan.sql
