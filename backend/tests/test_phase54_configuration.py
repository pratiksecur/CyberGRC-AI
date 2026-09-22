import os
from pathlib import Path
import runpy

import pytest


CONFIG_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "core"
    / "config.py"
)

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)


def _load_config(monkeypatch, **values):
    """
    Execute config.py in a fresh namespace with controlled
    environment variables.

    This avoids mutating the already-imported application
    configuration used by the rest of the test suite.
    """

    keys = [
        "ENVIRONMENT",
        "PROJECT_NAME",
        "PROJECT_VERSION",
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "MAX_REQUEST_BODY_BYTES",
        "MAX_UPLOAD_SIZE_BYTES",
        "CORS_ORIGINS",
        "AI_PROVIDER",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "OLLAMA_TIMEOUT",
    ]

    for key in keys:
        monkeypatch.delenv(
            key,
            raising=False,
        )

    for key, value in values.items():
        monkeypatch.setenv(
            key,
            value,
        )

    return runpy.run_path(
        str(CONFIG_PATH)
    )


def test_production_rejects_default_secret(monkeypatch):
    with pytest.raises(
        RuntimeError,
        match="SECRET_KEY",
    ):
        _load_config(
            monkeypatch,
            ENVIRONMENT="production",
            DATABASE_URL=(
                "postgresql://postgres:password"
                "@localhost:5432/cybergrc"
            ),
            SECRET_KEY=(
                "change-this-secret-key"
            ),
        )


def test_production_rejects_short_secret(monkeypatch):
    with pytest.raises(
        RuntimeError,
        match="32 characters",
    ):
        _load_config(
            monkeypatch,
            ENVIRONMENT="production",
            DATABASE_URL=(
                "postgresql://postgres:password"
                "@localhost:5432/cybergrc"
            ),
            SECRET_KEY="too-short-secret",
        )


def test_production_accepts_strong_secret_and_postgresql(
    monkeypatch,
):
    config = _load_config(
        monkeypatch,
        ENVIRONMENT="production",
        DATABASE_URL=(
            "postgresql://postgres:password"
            "@localhost:5432/cybergrc"
        ),
        SECRET_KEY=(
            "a" * 64
        ),
        CORS_ORIGINS=(
            "http://localhost:5173, "
            "http://127.0.0.1:5173"
        ),
    )

    assert config["ENVIRONMENT"] == "production"

    assert config["DATABASE_URL"].startswith(
        "postgresql://"
    )

    assert len(
        config["SECRET_KEY"]
    ) == 64

    assert config["CORS_ORIGINS"] == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_production_rejects_sqlite_database(
    monkeypatch,
):
    with pytest.raises(
        RuntimeError,
        match="SQLite",
    ):
        _load_config(
            monkeypatch,
            ENVIRONMENT="production",
            DATABASE_URL=(
                "sqlite:///./cybergrc.db"
            ),
            SECRET_KEY=(
                "a" * 64
            ),
        )


def test_invalid_integer_configuration_fails(
    monkeypatch,
):
    with pytest.raises(
        RuntimeError,
        match="ACCESS_TOKEN_EXPIRE_MINUTES",
    ):
        _load_config(
            monkeypatch,
            ACCESS_TOKEN_EXPIRE_MINUTES="invalid",
        )


def test_env_example_is_safe_and_present():
    env_example = (
        PROJECT_ROOT
        / ".env.example"
    )

    assert env_example.exists()

    content = env_example.read_text(
        encoding="utf-8"
    )

    assert "SECRET_KEY=" in content
    assert "POSTGRES_PASSWORD=" in content
    assert (
        "replace-with-a-random-secret"
        in content
    )

    # The example must not contain the real local
    # database password that exists only in .env.
    assert "pratik20" not in content.lower()


def test_gitignore_protects_environment_files():
    gitignore = (
        PROJECT_ROOT
        / ".gitignore"
    )

    content = gitignore.read_text(
        encoding="utf-8"
    )

    assert ".env" in content
    assert ".env.*" in content
    assert "!.env.example" in content