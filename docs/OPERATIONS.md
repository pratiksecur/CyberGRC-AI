CyberGRC-AI Operations Runbook

1. Architecture

CyberGRC-AI uses:

FastAPI backend

PostgreSQL 17

React frontend served through Nginx

Docker Compose

Persistent PostgreSQL volume

Persistent evidence-upload volume

PostgreSQL data is stored in the Docker volume:

postgres_data

Evidence files are stored separately in:

uploads_data

2. Starting the Application

From the project root:

cd D:\CyberGRC-AI
docker compose up -d

Check service status:

docker compose ps

The expected services are:

cybergrc-postgres

cybergrc-backend

cybergrc-frontend

The backend should become healthy only after both the application and PostgreSQL are ready.

3. Health Checks

Liveness

The liveness endpoint confirms that the FastAPI application is running:

curl http://localhost:8000/api/v1/health

Expected response:

{
  "status": "healthy",
  "application": "CyberGRC AI",
  "version": "1.0.0"
}

Readiness

The readiness endpoint confirms that the application can communicate with PostgreSQL and that persistent upload storage is available:

curl http://localhost:8000/api/v1/ready

Expected response:

{
  "status": "ready",
  "application": "CyberGRC AI",
  "version": "1.0.0"
}

If PostgreSQL or persistent upload storage is unavailable, the readiness endpoint returns HTTP 503.

4. PostgreSQL Database Backup

Create a backup directory on the host:

mkdir backups

Create a PostgreSQL custom-format backup:

docker compose exec -T postgres pg_dump -U postgres -d cybergrc -Fc > backups\cybergrc_backup.dump

The resulting file is:

backups\cybergrc_backup.dump

The backup should have a non-zero file size.

A zero-byte backup must be treated as a failed backup.

5. Verify Backup

Check the backup directory:

dir backups

The backup file should be present and have a non-zero size.

The PostgreSQL backup archive can also be inspected with:

docker compose exec -T postgres pg_restore --list < backups\cybergrc_backup.dump

A valid backup should return a PostgreSQL archive listing instead of an archive-format error.

6. Database Restore Test

A database backup is not considered fully reliable until it has been restored successfully.

For a controlled local restore test, create a separate database:

docker compose exec postgres createdb -U postgres cybergrc_restore_test

Restore the backup:

docker compose exec -T postgres pg_restore -U postgres -d cybergrc_restore_test < backups\cybergrc_backup.dump

Inspect the restored database:

docker compose exec postgres psql -U postgres -d cybergrc_restore_test -c "\dt"

The restored database should contain the application's tables.

After verification, remove the temporary database:

docker compose exec postgres dropdb -U postgres cybergrc_restore_test

A production environment should periodically perform restore tests using an isolated recovery environment.

7. Backup Integrity

A successful pg_dump command alone is not sufficient proof of recoverability.

Periodic recovery testing should verify:

The backup file exists.

The backup file is non-zero in size.

PostgreSQL can read the backup archive.

The backup can be restored into an isolated database.

Application tables are present after restoration.

Representative data can be queried.

The temporary recovery database can be removed safely.

8. Evidence Files

Evidence files are stored separately from PostgreSQL.

The Docker volume is:

uploads_data

A PostgreSQL database backup does not contain the evidence files stored in this volume.

Therefore a complete CyberGRC-AI backup strategy must protect both:

PostgreSQL database backups

Evidence-upload storage

A database-only backup is not a complete CyberGRC-AI backup.

Evidence storage should therefore be included in the organisation's broader backup and disaster-recovery plan.

9. Backup Retention

For a production deployment, backups should not be kept indefinitely on the same application host.

A production backup policy should consider:

Daily backups

Short-term retention

Longer-term retention where required

At least one copy stored separately from the application host

Periodic restore testing

Protection against accidental deletion or corruption

The exact retention period should be determined according to organisational, contractual, business, and regulatory requirements.

10. Secrets and Environment Configuration

Sensitive configuration must not be committed to Git.

The following files must remain local or be provided through the deployment environment:

.env
.env.*

The repository may contain:

.env.example

The example file must contain placeholders only and must not contain production credentials.

Important production configuration includes:

POSTGRES_PASSWORD
SECRET_KEY
DATABASE_URL
CORS_ORIGINS

Production SECRET_KEY must be a strong secret and must not use a development placeholder.

11. Docker Security

The CyberGRC-AI backend container is configured to:

Run as a non-root user

Drop Linux capabilities

Enable no-new-privileges

Avoid exposing PostgreSQL directly to the host

Use persistent PostgreSQL storage

Use persistent evidence storage

Require authentication for protected APIs

Protect evidence files through authenticated API endpoints

The frontend is served through Nginx.

12. PostgreSQL Storage

The PostgreSQL Docker volume is:

postgres_data

This volume contains the PostgreSQL database state.

Do not delete this volume during normal application restarts.

A command such as:

docker compose down

does not remove named volumes.

Destructive volume operations must be treated as database-loss operations unless a verified backup exists.

13. Evidence Storage

The evidence Docker volume is:

uploads_data

This storage contains uploaded evidence files.

Deleting this volume can cause loss of evidence files even if the PostgreSQL database is still available.

Database restoration and evidence-file restoration are therefore separate recovery activities.

14. Incident and Recovery Procedure

When a database or application failure occurs:

Step 1 — Check containers

docker compose ps

Step 2 — Check PostgreSQL logs

docker compose logs postgres

Step 3 — Check backend logs

docker compose logs backend

Step 4 — Check liveness

curl http://localhost:8000/api/v1/health

Step 5 — Check readiness

curl http://localhost:8000/api/v1/ready

Step 6 — Preserve existing data

Before destructive recovery actions, preserve the existing PostgreSQL state and available evidence storage.

Step 7 — Restore if necessary

Restore the database from a verified PostgreSQL backup.

Step 8 — Verify

After recovery:

Check /api/v1/health

Check /api/v1/ready

Verify representative GRC resources

Verify evidence files

Confirm the frontend can communicate with the backend

15. Recovery Objectives

A production deployment should explicitly define:

Recovery Point Objective (RPO)

How much data loss is acceptable after a failure.

Recovery Time Objective (RTO)

How quickly the system should be restored after a failure.

These values are organisation-specific and should be determined according to operational and business requirements.

CyberGRC-AI does not hard-code RPO or RTO values.

16. Production Backup Principle

A production backup strategy should protect:

PostgreSQL database
        +
Evidence file storage
        +
Application configuration and deployment configuration

Backups should be stored separately from the primary application environment where practical.

Regular restore tests should be performed to validate that backups are actually recoverable.

17. Persistent Upload Volume Ownership

The backend stores evidence files in the persistent Docker volume:

uploads_data

The application runs as the non-root user:

appuser

For a newly created Docker volume, the backend image prepares the upload directory with the correct ownership.

An existing volume may retain older ownership or permissions.

If /api/v1/ready returns HTTP 503 and the application logs indicate that persistent upload storage is unavailable, inspect the upload directory before performing destructive actions.

Check the backend container:

docker compose exec backend sh -c "id && ls -ld /app/uploads"

The upload directory should be writable by:

appuser

For a controlled ownership repair, use a temporary root execution with only the required CHOWN capability:

docker compose run --rm --no-deps --user root --cap-add CHOWN backend sh -c "chown appuser:appuser /app/uploads && chmod 750 /app/uploads"

Afterward, verify the directory:

docker compose exec backend sh -c "ls -ld /app/uploads"

Then check application readiness:

curl http://localhost:8000/api/v1/ready

Expected response:

{
  "status": "ready",
  "application": "CyberGRC AI",
  "version": "1.0.0"
}

Do not delete the uploads_data Docker volume as a workaround for an ownership problem.

Deleting the volume can permanently remove uploaded evidence files.

The volume should only be removed after confirming that all evidence has been backed up and that the operation is intentional.