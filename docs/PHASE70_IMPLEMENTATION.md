# Phase 70 — Production Hardening & Enterprise Readiness

## 70.1 Production Security Baseline

- Environment validation and explicit production configuration.
- Strong production secret validation.
- Configurable trusted hosts.
- Configurable proxy-header trust.
- Production API documentation disabled by default.
- HSTS support.
- Strict CORS origin validation.
- Stronger browser security headers.

## 70.2 API Hardening

- Request-size enforcement retained.
- Trusted Host middleware available for staging/production.
- Metrics endpoint is opt-in and token-protected when enabled in production.
- Request IDs remain attached to responses.
- Sensitive query values are excluded from logs.

## 70.3 Database Optimisation

- PostgreSQL pool sizing is environment-driven.
- Pool pre-ping and recycle remain enabled.
- Production operational indexes added for scheduler and notification workloads.
- Production operational indexes are used by notification workloads.
- The scheduler uses bounded `LIMIT` queries with rotating keyset cursors rather than unrestricted table scans.

## 70.4 Performance / Load Testing

`ops/load_test.py` provides a dependency-free concurrency smoke test. Use it against a non-production environment first and establish a baseline for p50, maximum latency, throughput, and error rate.

## 70.5 Background Job Reliability

- Scheduler interval and batch size are configurable.
- PostgreSQL advisory locking prevents duplicate scheduler execution across workers.
- Each scheduler run processes at most one configured batch per resource and rotates through active records over successive runs.
- Per-item failures use nested transactions so one bad notification does not abort the entire scan.
- Scheduler remains communication-only and does not execute governed GRC decisions.

## 70.6 Observability

- Request counters, 5xx counters, and cumulative request duration are exposed in Prometheus text format.
- Request IDs and safe operational metadata remain in application logs.
- `/health` is liveness; `/api/v1/ready` is readiness.

## 70.7 Backup / Disaster Recovery

- `ops/backup.sh` backs up PostgreSQL and uploads/evidence.
- `ops/restore.sh` verifies checksums and requires explicit confirmation before destructive restore.
- Disaster-recovery procedures are documented in `docs/DISASTER_RECOVERY.md`.

## 70.8 Production Configuration

- Docker application startup no longer runs Alembic migrations automatically.
- Migrations run through a one-shot Compose `migrate` profile.
- Development remains permissive, while staging/production require explicit CORS origins, allowed hosts, and trusted proxy configuration.
- Compose no longer overrides application production-safe configuration defaults with development-oriented values.
- Frontend uses `npm ci` for reproducible dependency installation.
- API origin is build-configurable for frontend CSP.

## 70.9 Dependency / Security Auditing

Use `ops/security_audit.sh`, `pip-audit`, and `npm audit --omit=dev` as release gates. Any accepted vulnerability exception must be documented and time-bounded.

## 70.10 Security Testing

The existing authorization, tenant-isolation, AI-governance, upload-security, and production-hardening tests remain part of the final regression. Phase 70 adds configuration and deployment-hardening tests.

## 70.11 Deployment Documentation

`docs/PRODUCTION_DEPLOYMENT.md` defines the deployment order, configuration requirements, migration workflow, observability, scaling, and release checks.

## 70.12 Final Regression

From `backend`:

```cmd
python -m pytest -q
```

Then:

```cmd
docker compose build
docker compose up -d postgres
docker compose --profile migrate run --rm migrate
docker compose up -d backend frontend
docker compose ps
docker compose exec backend alembic current
```

Finally run a smoke check and load test.
