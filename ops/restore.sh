#!/usr/bin/env bash
set -euo pipefail
umask 077

BACKUP_DIR="${1:?Usage: ./ops/restore.sh <backup-directory> }"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-cybergrc-postgres}"
BACKEND_CONTAINER="${BACKEND_CONTAINER:-cybergrc-backend}"

if [[ ! -f "${BACKUP_DIR}/cybergrc.dump" || ! -f "${BACKUP_DIR}/uploads.tar.gz" ]]; then
  echo "Backup directory must contain cybergrc.dump and uploads.tar.gz" >&2
  exit 1
fi

if [[ -f "${BACKUP_DIR}/SHA256SUMS" ]]; then
  sha256sum -c "${BACKUP_DIR}/SHA256SUMS"
fi

echo "WARNING: PostgreSQL restore replaces database contents."
echo "Stop application traffic before restoring to avoid concurrent writes."
read -r -p "Type RESTORE to continue: " confirmation
[[ "$confirmation" == "RESTORE" ]]

cat "${BACKUP_DIR}/cybergrc.dump" | docker exec -i "$POSTGRES_CONTAINER" \
  pg_restore -U postgres -d cybergrc --clean --if-exists --no-owner

echo "Restoring uploads..."
cat "${BACKUP_DIR}/uploads.tar.gz" | docker exec -i "$BACKEND_CONTAINER" \
  tar -xzf - -C /app

echo "Restore completed. Run the readiness and smoke tests before reopening traffic."
