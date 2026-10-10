import os
from urllib.parse import urlparse


# ==========================================================
# HELPERS
# ==========================================================


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value.strip()


def _env_int(name: str, default: int) -> int:
    raw_value = _env(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a valid integer.") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero.")
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw_value = _env(name, "true" if default else "false").lower()
    if raw_value in {"1", "true", "yes", "on"}:
        return True
    if raw_value in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be a boolean value.")


def _env_list(name: str, default: str) -> list[str]:
    return [item.strip() for item in _env(name, default).split(",") if item.strip()]


# ==========================================================
# ENVIRONMENT / APPLICATION
# ==========================================================

ENVIRONMENT = _env("ENVIRONMENT", "development").lower()

if ENVIRONMENT not in {"development", "test", "staging", "production"}:
    raise RuntimeError(
        "ENVIRONMENT must be one of: development, test, staging, production."
    )

PROJECT_NAME = _env("PROJECT_NAME", "CyberGRC AI")
PROJECT_VERSION = _env("PROJECT_VERSION", "1.0.0")


# ==========================================================
# DATABASE
# ==========================================================

DATABASE_URL = _env("DATABASE_URL", "sqlite:///./cybergrc.db")

if ENVIRONMENT == "production":
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL must be configured in production.")
    if DATABASE_URL.lower().startswith("sqlite://"):
        raise RuntimeError(
            "SQLite is not permitted in production. Configure DATABASE_URL for PostgreSQL."
        )

DB_POOL_SIZE = _env_int("DB_POOL_SIZE", 10)
DB_MAX_OVERFLOW = _env_int("DB_MAX_OVERFLOW", 20)
DB_POOL_RECYCLE_SECONDS = _env_int("DB_POOL_RECYCLE_SECONDS", 1800)
DB_POOL_TIMEOUT_SECONDS = _env_int("DB_POOL_TIMEOUT_SECONDS", 30)


# ==========================================================
# AUTHENTICATION
# ==========================================================

SECRET_KEY = _env("SECRET_KEY", "change-this-secret-key")
ALGORITHM = _env("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = _env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

_INSECURE_SECRET_VALUES = {
    "",
    "change-this-secret-key",
    "changeme",
    "change-me",
    "secret",
    "secret-key",
    "your-secret-key",
}

if ENVIRONMENT in {"staging", "production"}:
    if SECRET_KEY.lower() in _INSECURE_SECRET_VALUES:
        raise RuntimeError("SECRET_KEY must be replaced with a strong secret in non-development environments.")
    if len(SECRET_KEY) < 32:
        raise RuntimeError("SECRET_KEY must contain at least 32 characters in non-development environments.")


# ==========================================================
# API / REQUEST SECURITY
# ==========================================================

MAX_REQUEST_BODY_BYTES = _env_int("MAX_REQUEST_BODY_BYTES", 12 * 1024 * 1024)
MAX_UPLOAD_SIZE_BYTES = _env_int("MAX_UPLOAD_SIZE_BYTES", 10 * 1024 * 1024)

ALLOWED_HOSTS = _env_list(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1",
)

if ENVIRONMENT in {"staging", "production"} and not os.getenv("ALLOWED_HOSTS", "").strip():
    raise RuntimeError(
        "ALLOWED_HOSTS must be explicitly configured in staging and production."
    )

TRUSTED_HOSTS_ENABLED = _env_bool(
    "TRUSTED_HOSTS_ENABLED",
    ENVIRONMENT in {"staging", "production"},
)

PROXY_HEADERS_ENABLED = _env_bool(
    "PROXY_HEADERS_ENABLED",
    ENVIRONMENT in {"staging", "production"},
)

FORWARDED_ALLOW_IPS = _env("FORWARDED_ALLOW_IPS", "127.0.0.1")

if (
    ENVIRONMENT in {"staging", "production"}
    and PROXY_HEADERS_ENABLED
    and not os.getenv("FORWARDED_ALLOW_IPS", "").strip()
):
    raise RuntimeError(
        "FORWARDED_ALLOW_IPS must be explicitly configured when proxy headers are enabled in staging or production."
    )

API_DOCS_ENABLED = _env_bool(
    "API_DOCS_ENABLED",
    ENVIRONMENT not in {"staging", "production"},
)

METRICS_ENABLED = _env_bool(
    "METRICS_ENABLED",
    ENVIRONMENT not in {"production"},
)

METRICS_AUTH_TOKEN = _env("METRICS_AUTH_TOKEN", "")

if ENVIRONMENT == "production" and METRICS_ENABLED and not METRICS_AUTH_TOKEN:
    raise RuntimeError(
        "METRICS_AUTH_TOKEN must be configured when metrics are enabled in production."
    )

ENABLE_HSTS = _env_bool(
    "ENABLE_HSTS",
    ENVIRONMENT == "production",
)


# ==========================================================
# FILE UPLOAD SECURITY
# ==========================================================

ALLOWED_UPLOAD_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".txt", ".csv",
    ".doc", ".docx", ".xls", ".xlsx", ".zip",
}

ALLOWED_UPLOAD_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/plain",
    "text/csv",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/zip",
    "application/x-zip-compressed",
}

ALLOWED_UPLOAD_MIME_TYPES = ALLOWED_UPLOAD_CONTENT_TYPES


# ==========================================================
# CORS
# ==========================================================

CORS_ORIGINS = _env_list(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

if ENVIRONMENT in {"staging", "production"} and not os.getenv("CORS_ORIGINS", "").strip():
    raise RuntimeError(
        "CORS_ORIGINS must be explicitly configured in staging and production."
    )

if not CORS_ORIGINS:
    raise RuntimeError("At least one CORS origin must be configured.")

if "*" in CORS_ORIGINS:
    raise RuntimeError(
        "Wildcard CORS origins are not permitted because authenticated requests use credentials."
    )

for origin in CORS_ORIGINS:
    parsed = urlparse(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(f"Invalid CORS origin: {origin}")


# ==========================================================
# BACKGROUND JOBS
# ==========================================================

SCHEDULER_ENABLED = _env_bool(
    "SCHEDULER_ENABLED",
    True,
)

SCHEDULER_INTERVAL_SECONDS = _env_int(
    "SCHEDULER_INTERVAL_SECONDS",
    15 * 60,
)

SCHEDULER_BATCH_SIZE = _env_int(
    "SCHEDULER_BATCH_SIZE",
    250,
)

SCHEDULER_LOCK_KEY = _env_int(
    "SCHEDULER_LOCK_KEY",
    704001,
)


# ==========================================================
# AI CONFIGURATION
# ==========================================================

AI_PROVIDER = _env("AI_PROVIDER", "ollama").lower()
OLLAMA_BASE_URL = _env("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = _env_int("OLLAMA_TIMEOUT", 120)
