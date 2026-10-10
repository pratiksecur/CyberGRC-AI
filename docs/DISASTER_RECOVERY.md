# CyberGRC-AI Disaster Recovery

## Protected data

1. PostgreSQL database
2. Evidence/upload volume
3. Deployment configuration and secret-management metadata (never the raw secrets themselves)

## Recovery objectives

Set organisation-specific RPO/RTO values before production launch. A sensible initial target is:

- RPO: 24 hours or better
- RTO: 4 hours or better

These are planning targets, not guarantees.

## Backup requirements

- Daily PostgreSQL backup at minimum.
- Daily upload/evidence backup at minimum.
- Keep at least one recent copy off-host/off-region where policy permits.
- Encrypt backups at rest.
- Restrict backup access to authorised operators.
- Record backup checksums.

## Restore procedure

1. Isolate the failed environment.
2. Provision a clean PostgreSQL instance.
3. Restore the database with `ops/restore.sh` or an equivalent controlled procedure.
4. Restore the upload/evidence volume.
5. Run `alembic current` and confirm the expected head.
6. Start the backend and verify `/api/v1/ready`.
7. Verify authentication, tenant isolation, evidence retrieval, reports, and notifications.
8. Run the final regression suite.
9. Reopen traffic only after the smoke checks succeed.

## Restore testing

A backup is not considered reliable until restoration has been tested. Perform a full restore drill at least quarterly and record the result.
