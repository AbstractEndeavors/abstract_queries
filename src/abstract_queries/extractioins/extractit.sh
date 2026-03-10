#!/usr/bin/env bash
# extractit.sh
# -------------
# Usage:
#   ./extractit.sh \
#     "host=solcatcher.io port=2345 dbname=abstract_base user=admin password=tBUP2Q8L2F" \
#     ./my_exports

set -euo pipefail

CONN="$1"
OUTPUT_DIR="${2:-./db_export}"

mkdir -p "$OUTPUT_DIR"

# 1) Get all public tables
TABLES=$(psql --no-password -d "$CONN" -t -c \
  "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public';" \
)

echo "Found tables:"
echo "$TABLES"

# 2) Loop and dump
for tbl in $TABLES; do
  echo "→ Exporting schema for $tbl …"
  pg_dump --no-password -d "$CONN" \
    --schema-only \
    --table="$tbl" \
    -f "$OUTPUT_DIR/schema_${tbl}.sql"

  echo "→ Exporting data for $tbl …"
  # Use a single, correctly quoted -c argument:
  psql --no-password -d "$CONN" -c "\
\copy public.\"$tbl\" TO '$OUTPUT_DIR/data_${tbl}.csv' CSV HEADER\
"
done

echo "✅ All tables dumped into $OUTPUT_DIR"