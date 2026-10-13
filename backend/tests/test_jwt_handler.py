"""The JWT layer: tokens round-trip, and forged or malformed tokens are refused."""

from datetime import datetime, timedelta, timezone

import jwt

from app.auth.jwt_handler import create_access_token, verify_access_token
from app.core.config import ALGORITHM, SECRET_KEY


def test_token_round_trips_with_standard_claims():
    token = create_access_token({"sub": "admin@example.com", "ver": 3})

    payload = verify_access_token(token)

    assert payload["sub"] == "admin@example.com"
    assert payload["ver"] == 3
    assert payload["iat"] <= payload["exp"]


def test_token_signed_with_another_key_is_rejected():
    forged = jwt.encode(
        {
            "sub": "admin@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "x" * 48,
        algorithm=ALGORITHM,
    )

    assert verify_access_token(forged) is None


def test_unsigned_token_is_rejected():
    unsigned = jwt.encode(
        {
            "sub": "admin@example.com",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        None,
        algorithm="none",
    )

    assert verify_access_token(unsigned) is None


def test_empty_and_malformed_tokens_are_rejected():
    assert verify_access_token("") is None
    assert verify_access_token(None) is None
    assert verify_access_token("not.a.token") is None
    assert verify_access_token("a.b") is None
    assert verify_access_token(12345) is None


def test_token_without_expiry_still_has_one_added_by_the_server():
    token = create_access_token({"sub": "admin@example.com"})

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert "exp" in decoded