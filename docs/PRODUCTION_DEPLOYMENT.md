# CyberGRC-AI Production Deployment Runbook

## 1. Required production settings

Set at minimum:

- `ENVIRONMENT=production`
- strong `SECRET_KEY` (32+ random characters; 64+ recommended)
- strong `POSTGRES_PASSWORD`
- `CORS_ORIGINS` to the real frontend origin(s)
- `ALLOWED_HOSTS` to the real API host(s)
- `TRUSTED_HOSTS_ENABLED=true`
- `PROXY_HEADERS_ENABLED=true` only when traffic comes through a trusted reverse proxy
- `FORWARDED_ALLOW_IPS` to the proxy address/network actually used
- `API_DOCS_ENABLED=false`
- `ENABLE_HSTS=true` when HTTPS is enforced
- `METRICS_ENABLED=true` only when a protected scrape path is available
- `METRICS_AUTH_TOKEN` when metrics are enabled in production
- `SCHEDULER_ENABLED=true`

Never place secrets in the repository, Dockerfile, image, frontend bundle, or logs.

## 2. Deployment order

Build images:

```bash
docker compose build
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Run migrations once:

```bash
docker compose --profile migrate run --rm migrate
```

Start application services:

```bash
docker compose up -d backend frontend
```

Check:

```bash
docker compose ps
docker compose logs --tail=100 backend
```

Verify readiness:

```bash
curl -f http://localhost:8000/api/v1/ready
```

## 3. Scaling

The notification scheduler uses a PostgreSQL advisory lock. Multiple application workers may therefore start the scheduler loop, but only one worker can execute a scheduler batch at a time. Each run is bounded by `SCHEDULER_BATCH_SIZE` and rotates through active records over successive runs.

For larger deployments, a dedicated worker process is preferable. The current implementation deliberately avoids introducing a second queueing system while preserving duplicate-run protection.

## 4. Migrations

Do not run Alembic automatically in every application worker. Run the migration job once per deployment, then start application containers.

## 5. API documentation

Production should normally expose no `/docs`, `/redoc`, or `/openapi.json` endpoints. The application disables them by default when `ENVIRONMENT=production`. Enable them only temporarily when operationally required.

Do not rely on Docker Compose development defaults for production. Set `CORS_ORIGINS`, `ALLOWED_HOSTS`, and (when applicable) `FORWARDED_ALLOW_IPS` explicitly.

## 6. Observability

The optional `/metrics` endpoint returns Prometheus-compatible text. In production it requires `X-Metrics-Token` when enabled.

Do not expose the metrics endpoint directly to the public internet.

## 7. Backup

Run:

```bash
./ops/backup.sh
```

Store the generated backup directory outside the application host as well. Test restoration regularly.

## 8. Security checks

Before release:

```bash
python -m pip_audit
cd frontend && npm audit --omit=dev
```

Run the complete test suite from `backend`:

```bash
python -m pytest -q
```

Run the HTTP smoke load test:

```bash
python ops/load_test.py --url http://localhost:8000/api/v1/health --requests 250 --concurrency 25
```
