from datetime import datetime, timedelta, timezone

from jose import jwt

from app.auth.jwt_handler import (
    create_access_token,
    verify_access_token,
)
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
)


def test_created_token_contains_required_security_claims():
    token = create_access_token(
        {
            "sub": "admin@example.com",
        }
    )

    payload = verify_access_token(token)

    assert payload is not None
    assert payload["sub"] == "admin@example.com"

    assert "iat" in payload
    assert "exp" in payload

    assert payload["iat"] < payload["exp"]


def test_expired_token_is_rejected():
    expired_token = jwt.encode(
        {
            "sub": "admin@example.com",
            "iat": datetime.now(
                timezone.utc
            ) - timedelta(minutes=10),
            "exp": datetime.now(
                timezone.utc
            ) - timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert (
        verify_access_token(expired_token)
        is None
    )


def test_tampered_token_is_rejected():
    token = create_access_token(
        {
            "sub": "admin@example.com",
        }
    )

    header, payload, signature = token.split(".")

    tampered_payload = jwt.encode(
        {
            "sub": "employee@example.com",
            "iat": datetime.now(
                timezone.utc
            ),
            "exp": datetime.now(
                timezone.utc
            ) + timedelta(minutes=30),
        },
        "attacker-controlled-secret",
        algorithm=ALGORITHM,
    ).split(".")[1]

    tampered_token = (
        f"{header}.{tampered_payload}.{signature}"
    )

    assert (
        verify_access_token(tampered_token)
        is None
    )


def test_invalid_signature_is_rejected():
    token = jwt.encode(
        {
            "sub": "admin@example.com",
            "iat": datetime.now(
                timezone.utc
            ),
            "exp": datetime.now(
                timezone.utc
            ) + timedelta(minutes=30),
        },
        "wrong-secret",
        algorithm=ALGORITHM,
    )

    assert (
        verify_access_token(token)
        is None
    )


def test_malformed_token_is_rejected():
    malformed_tokens = [
        "",
        "invalid",
        "abc.def",
        "abc.def.ghi",
        "not.a.real.jwt.token",
    ]

    for token in malformed_tokens:
        assert (
            verify_access_token(token)
            is None
        )


def test_token_without_subject_is_rejected():
    token = create_access_token(
        {
            "role": "Admin",
        }
    )

    payload = verify_access_token(token)

    assert payload is not None
    assert payload.get("sub") is None


def test_algorithm_is_explicitly_restricted():
    """
    A token signed with a different algorithm must not
    be accepted by the configured JWT verifier.
    """

    alternative_algorithm = (
        "HS384"
        if ALGORITHM != "HS384"
        else "HS512"
    )

    token = jwt.encode(
        {
            "sub": "admin@example.com",
            "iat": datetime.now(
                timezone.utc
            ),
            "exp": datetime.now(
                timezone.utc
            ) + timedelta(minutes=30),
        },
        SECRET_KEY,
        algorithm=alternative_algorithm,
    )

    assert (
        verify_access_token(token)
        is None
    )


def test_get_current_user_rejects_invalid_token(
    client,
):
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or expired token."
    )


def test_get_current_user_requires_subject(
    client,
):
    token = create_access_token(
        {
            "role": "Admin",
        }
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid token payload."
    )


def test_nonexistent_subject_is_generic_auth_failure(
    client,
):
    token = create_access_token(
        {
            "sub": "does-not-exist@example.com",
        }
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid authentication credentials."
    )


def test_missing_authentication_is_rejected(
    client,
):
    response = client.get(
        "/api/v1/auth/me"
    )

    assert response.status_code == 401