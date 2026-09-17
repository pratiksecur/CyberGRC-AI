import os


# ==========================================================
# APPLICATION
# ==========================================================

PROJECT_NAME = os.getenv(
    "PROJECT_NAME",
    "CyberGRC AI",
)

PROJECT_VERSION = os.getenv(
    "PROJECT_VERSION",
    "1.0.0",
)


# ==========================================================
# DATABASE
# ==========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./cybergrc.db",
)


# ==========================================================
# AUTHENTICATION
# ==========================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key",
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30",
    )
)


# ==========================================================
# API / REQUEST SECURITY
# ==========================================================

MAX_REQUEST_BODY_BYTES = int(
    os.getenv(
        "MAX_REQUEST_BODY_BYTES",
        str(12 * 1024 * 1024),
    )
)


# ==========================================================
# FILE UPLOAD SECURITY
# ==========================================================

MAX_UPLOAD_SIZE_BYTES = int(
    os.getenv(
        "MAX_UPLOAD_SIZE_BYTES",
        str(10 * 1024 * 1024),
    )
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


# Backward-compatible alias for code/tests that use the
# MIME naming convention.
ALLOWED_UPLOAD_MIME_TYPES = ALLOWED_UPLOAD_CONTENT_TYPES


# ==========================================================
# CORS
# ==========================================================

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]


# ==========================================================
# AI CONFIGURATION
# ==========================================================

AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "ollama",
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434/api/generate",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "mistral",
)

OLLAMA_TIMEOUT = int(
    os.getenv(
        "OLLAMA_TIMEOUT",
        "120",
    )
)