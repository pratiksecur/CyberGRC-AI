from pathlib import Path
import runpy

import pytest


CONFIG_PATH = Path(__file__).resolve().parents[1] / "app" / "core" / "config.py"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_config(monkeypatch, **values):
    keys = [
        "ENVIRONMENT", "PROJECT_NAME", "PROJECT_VERSION", "DATABASE_URL",
        "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
        "MAX_REQUEST_BODY_BYTES", "MAX_UPLOAD_SIZE_BYTES", "CORS_ORIGINS",
        "AI_PROVIDER", "OLLAMA_BASE_URL", "OLLAMA_MODEL", "OLLAMA_TIMEOUT",
        "DB_POOL_SIZE", "DB_MAX_OVERFLOW", "DB_POOL_RECYCLE_SECONDS",
        "DB_POOL_TIMEOUT_SECONDS", "ALLOWED_HOSTS", "TRUSTED_HOSTS_ENABLED",
        "PROXY_HEADERS_ENABLED", "FORWARDED_ALLOW_IPS", "API_DOCS_ENABLED",
        "METRICS_ENABLED", "METRICS_AUTH_TOKEN", "ENABLE_HSTS",
        "SCHEDULER_ENABLED", "SCHEDULER_INTERVAL_SECONDS", "SCHEDULER_BATCH_SIZE",
        "SCHEDULER_LOCK_KEY",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return runpy.run_path(str(CONFIG_PATH))


def test_production_defaults_disable_docs(monkeypatch):
    config = _load_config(
        monkeypatch,
        ENVIRONMENT="production",
        DATABASE_URL="postgresql://postgres:password@localhost:5432/cybergrc",
        SECRET_KEY="a" * 64,
        CORS_ORIGINS="https://app.example.com",
        ALLOWED_HOSTS="api.example.com",
        FORWARDED_ALLOW_IPS="10.0.0.10",
    )
    assert config["API_DOCS_ENABLED"] is False
    assert config["TRUSTED_HOSTS_ENABLED"] is True
    assert config["ENABLE_HSTS"] is True


def test_production_metrics_require_authentication(monkeypatch):
    with pytest.raises(RuntimeError, match="METRICS_AUTH_TOKEN"):
        _load_config(
            monkeypatch,
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://postgres:password@localhost:5432/cybergrc",
            SECRET_KEY="a" * 64,
            CORS_ORIGINS="https://app.example.com",
            ALLOWED_HOSTS="api.example.com",
            FORWARDED_ALLOW_IPS="10.0.0.10",
            METRICS_ENABLED="true",
        )


def test_wildcard_cors_is_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="Wildcard CORS"):
        _load_config(monkeypatch, CORS_ORIGINS="*")


def test_invalid_cors_origin_is_rejected(monkeypatch):
    with pytest.raises(RuntimeError, match="Invalid CORS origin"):
        _load_config(monkeypatch, CORS_ORIGINS="not-an-origin")


def test_scheduler_settings_are_environment_driven(monkeypatch):
    config = _load_config(
        monkeypatch,
        SCHEDULER_INTERVAL_SECONDS="600",
        SCHEDULER_BATCH_SIZE="100",
        SCHEDULER_LOCK_KEY="123456",
    )
    assert config["SCHEDULER_INTERVAL_SECONDS"] == 600
    assert config["SCHEDULER_BATCH_SIZE"] == 100
    assert config["SCHEDULER_LOCK_KEY"] == 123456


def test_database_pool_settings_are_environment_driven(monkeypatch):
    config = _load_config(
        monkeypatch,
        DB_POOL_SIZE="5",
        DB_MAX_OVERFLOW="7",
        DB_POOL_RECYCLE_SECONDS="900",
        DB_POOL_TIMEOUT_SECONDS="12",
    )
    assert config["DB_POOL_SIZE"] == 5
    assert config["DB_MAX_OVERFLOW"] == 7
    assert config["DB_POOL_RECYCLE_SECONDS"] == 900
    assert config["DB_POOL_TIMEOUT_SECONDS"] == 12



def test_production_requires_explicit_cors_and_hosts(monkeypatch):
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        _load_config(
            monkeypatch,
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://postgres:password@localhost:5432/cybergrc",
            SECRET_KEY="a" * 64,
            ALLOWED_HOSTS="api.example.com",
            FORWARDED_ALLOW_IPS="10.0.0.10",
        )

    with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
        _load_config(
            monkeypatch,
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://postgres:password@localhost:5432/cybergrc",
            SECRET_KEY="a" * 64,
            CORS_ORIGINS="https://app.example.com",
            FORWARDED_ALLOW_IPS="10.0.0.10",
        )


def test_production_requires_explicit_forwarded_allow_ips_when_proxy_headers_enabled(monkeypatch):
    with pytest.raises(RuntimeError, match="FORWARDED_ALLOW_IPS"):
        _load_config(
            monkeypatch,
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://postgres:password@localhost:5432/cybergrc",
            SECRET_KEY="a" * 64,
            CORS_ORIGINS="https://app.example.com",
            ALLOWED_HOSTS="api.example.com",
        )

def test_production_runbook_exists():
    assert (PROJECT_ROOT / "docs" / "PRODUCTION_DEPLOYMENT.md").exists()
    assert (PROJECT_ROOT / "docs" / "DISASTER_RECOVERY.md").exists()
    assert (PROJECT_ROOT / "docs" / "SECURITY_RUNBOOK.md").exists()


def test_backup_scripts_exist():
    assert (PROJECT_ROOT / "ops" / "backup.sh").exists()
    assert (PROJECT_ROOT / "ops" / "restore.sh").exists()
    assert (PROJECT_ROOT / "ops" / "load_test.py").exists()


def test_backend_dockerfile_does_not_run_migrations_on_every_start():
    content = (PROJECT_ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
    assert "alembic upgrade head && uvicorn" not in content
    assert "uvicorn app.main:app" in content


def test_compose_has_one_shot_migration_service():
    content = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "migrate:" in content
    assert "profiles: [\"migrate\"]" in content
    assert "alembic" in content
    assert "upgrade" in content
    assert "head" in content
