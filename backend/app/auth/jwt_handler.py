from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


def create_access_token(data: dict):
    """
    Generate a signed JWT access token.

    Security claims:
    - sub: supplied subject, normally the user's email
    - iat: token issuance timestamp
    - exp: token expiration timestamp
    """

    to_encode = data.copy()

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "iat": now,
            "exp": expire,
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def verify_access_token(token: str):
    """
    Verify and decode a JWT access token.

    The accepted signing algorithm is explicitly restricted
    to the configured algorithm.

    Invalid, expired, malformed, or incorrectly signed tokens
    return None.
    """

    if not token or not isinstance(token, str):
        return None

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:
        return None