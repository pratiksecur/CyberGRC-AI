import os


# ==========================================================
# HELPERS
# ==========================================================


def _env(
    name: str,
    default: str,
) -> str:
    """
    Read an environment variable and remove surrounding
    whitespace.
    """

    value = os.getenv(name, default)

    return value.strip()


def _env_int(
    name: str,
    default: int,
) -> int:
    """
    Read a positive integer environment variable.
    """

    raw_value = _env(
        name,
        str(default),
    )

    try:
        value = int(raw_value)

    except ValueError as exc:
        raise RuntimeError(
            f"{name} must be a valid integer."
        ) from exc

    if value <= 0:
        raise RuntimeError(
            f"{name} must be greater than zero."
        )

    return value


# ==========================================================
# ENVIRONMENT
# ==========================================================


ENVIRONMENT = _env(
    "ENVIRONMENT",
    "development",
).lower()


# ==========================================================
# APPLICATION
# ==========================================================


PROJECT_NAME = _env(
    "PROJECT_NAME",
    "CyberGRC AI",
)

PROJECT_VERSION = _env(
    "PROJECT_VERSION",
    "1.0.0",
)


# ==========================================================
# DATABASE
# ==========================================================


DATABASE_URL = _env(
    "DATABASE_URL",
    "sqlite:///./cybergrc.db",
)

if ENVIRONMENT == "production":

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL must be configured "
            "in production."
        )

    if DATABASE_URL.lower().startswith(
        "sqlite://"
    ):
        raise RuntimeError(
            "SQLite is not permitted in production. "
            "Configure DATABASE_URL for PostgreSQL."
        )


# ==========================================================
# AUTHENTICATION
# ==========================================================


SECRET_KEY = _env(
    "SECRET_KEY",
    "change-this-secret-key",
)

ALGORITHM = _env(
    "ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = _env_int(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    30,
)


# ----------------------------------------------------------
# Production secret validation
# ----------------------------------------------------------


_INSECURE_SECRET_VALUES = {
    "",
    "change-this-secret-key",
    "changeme",
    "change-me",
    "secret",
    "secret-key",
    "your-secret-key",
}


if ENVIRONMENT == "production":

    if (
        SECRET_KEY.lower()
        in _INSECURE_SECRET_VALUES
    ):
        raise RuntimeError(
            "SECRET_KEY must be replaced with "
            "a strong secret in production."
        )

    if len(SECRET_KEY) < 32:
        raise RuntimeError(
            "SECRET_KEY must contain at least "
            "32 characters in production."
        )


# ==========================================================
# API / REQUEST SECURITY
# ==========================================================


MAX_REQUEST_BODY_BYTES = _env_int(
    "MAX_REQUEST_BODY_BYTES",
    12 * 1024 * 1024,
)


# ==========================================================
# FILE UPLOAD SECURITY
# ==========================================================


MAX_UPLOAD_SIZE_BYTES = _env_int(
    "MAX_UPLOAD_SIZE_BYTES",
    10 * 1024 * 1024,
)


ALLOWED_UPLOAD_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".txt",
    ".csv",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".zip",
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


# Backward-compatible alias for existing code/tests.
ALLOWED_UPLOAD_MIME_TYPES = (
    ALLOWED_UPLOAD_CONTENT_TYPES
)


# ==========================================================
# CORS
# ==========================================================


CORS_ORIGINS = [
    origin.strip()
    for origin in _env(
        "CORS_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173"
        ),
    ).split(",")
    if origin.strip()
]


if not CORS_ORIGINS:
    raise RuntimeError(
        "At least one CORS origin must be configured."
    )


# ==========================================================
# AI CONFIGURATION
# ==========================================================


AI_PROVIDER = _env(
    "AI_PROVIDER",
    "ollama",
).lower()


OLLAMA_BASE_URL = _env(
    "OLLAMA_BASE_URL",
    "http://localhost:11434/api/generate",
)


OLLAMA_MODEL = _env(
    "OLLAMA_MODEL",
    "mistral",
)


OLLAMA_TIMEOUT = int(
    _env(
        "OLLAMA_TIMEOUT",
        "120",
    )
)


if OLLAMA_TIMEOUT <= 0:
    raise RuntimeError(
        "OLLAMA_TIMEOUT must be greater than zero."
    )