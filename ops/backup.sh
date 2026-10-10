#!/usr/bin/env bash
set -euo pipefail
umask 077

BACKUP_ROOT="${BACKUP_ROOT:-./backups}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-cybergrc-postgres}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-cybergrc-backend}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p "$DEST"

echo "Creating PostgreSQL backup..."
docker exec "$POSTGRES_CONTAINER" pg_dump \
  -U postgres \
  -d cybergrc \
  -Fc \
  > "${DEST}/cybergrc.dump"

echo "Creating evidence/upload backup..."
docker exec "$BACKEND_CONTAINER" \
  tar -czf - -C /app uploads \
  > "${DEST}/uploads.tar.gz"

sha256sum "${DEST}/cybergrc.dump" "${DEST}/uploads.tar.gz" \
  > "${DEST}/SHA256SUMS"

printf 'Backup completed: %s\n' "$DEST"
printf 'Files:\n'
ls -lh "$DEST"
