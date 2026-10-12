"""Session cookie and CSRF helpers.

The JWT is stored in an httpOnly cookie so JavaScript (and therefore any
injected script) cannot read it. Because browsers attach cookies
automatically, state-changing requests that authenticate with the cookie must
also send a CSRF token in the X-CSRF-Token header.

The CSRF token is derived from the session token with an HMAC, so the server
needs no extra storage: it simply recomputes the expected value.

Requests that authenticate with an Authorization: Bearer header (API clients,
Swagger UI, the test suite) are not affected, because browsers never attach
that header on their own.

Settings (all optional environment variables):

    COOKIE_SECURE    true/false. Default: true in staging/production, false otherwise.
    COOKIE_SAMESITE  lax (default), strict or none. "none" requires COOKIE_SECURE=true.
    COOKIE_DOMAIN    Set only when the frontend and API are on sibling subdomains,
                     e.g. example.com. Default: host-only cookie.
"""

import hashlib
import hmac
import os

from fastapi import Response

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ENVIRONMENT,
    SECRET_KEY,
)


ACCESS_COOKIE_NAME = "cybergrc_access_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def _cookie_secure() -> bool:
    raw_value = os.getenv("COOKIE_SECURE", "").strip().lower()

    if not raw_value:
        return ENVIRONMENT in {"staging", "production"}

    if raw_value in {"1", "true", "yes", "on"}:
        return True

    if raw_value in {"0", "false", "no", "off"}:
        return False

    raise RuntimeError("COOKIE_SECURE must be a boolean value.")


def _cookie_samesite() -> str:
    value = os.getenv("COOKIE_SAMESITE", "lax").strip().lower()

    if value not in {"lax", "strict", "none"}:
        raise RuntimeError("COOKIE_SAMESITE must be one of: lax, strict, none.")

    return value


COOKIE_SECURE = _cookie_secure()
COOKIE_SAMESITE = _cookie_samesite()
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "").strip() or None

if COOKIE_SAMESITE == "none" and not COOKIE_SECURE:
    raise RuntimeError("COOKIE_SAMESITE=none requires COOKIE_SECURE=true.")

if ENVIRONMENT in {"staging", "production"} and not COOKIE_SECURE:
    raise RuntimeError(
        "COOKIE_SECURE must be true in staging and production."
    )


def csrf_token_for(access_token: str) -> str:
    """Return the CSRF token that belongs to this session token."""

    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        b"csrf-v1:" + access_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def is_valid_csrf(access_token: str, supplied: str | None) -> bool:
    if not supplied:
        return False

    return hmac.compare_digest(
        csrf_token_for(access_token).encode("utf-8"),
        supplied.encode("utf-8"),
    )


def set_access_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=COOKIE_DOMAIN,
        secure=COOKIE_SECURE,
        httponly=True,
        samesite=COOKIE_SAMESITE,
    )


def clear_access_cookie(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path="/",
        domain=COOKIE_DOMAIN,
        secure=COOKIE_SECURE,
        httponly=True,
        samesite=COOKIE_SAMESITE,
    )