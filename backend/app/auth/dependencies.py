from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.cookies import (
    ACCESS_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SAFE_METHODS,
    is_valid_csrf,
)
from app.auth.jwt_handler import verify_access_token
from app.models.user import User


# auto_error is disabled so the session cookie can be used when no
# Authorization header is sent. A missing credential still returns 401.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def extract_access_token(
    request: Request,
    header_token: str | None,
) -> tuple[str | None, bool]:
    """
    Return (token, came_from_cookie).

    An Authorization header takes precedence over the session cookie.
    """

    if header_token:
        return header_token, False

    cookie_token = request.cookies.get(ACCESS_COOKIE_NAME)

    if cookie_token:
        return cookie_token, True

    return None, False


def get_current_user(
    request: Request,
    header_token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Resolve the authenticated user from a JWT access token.

    The token may arrive in an Authorization: Bearer header or in the
    httpOnly session cookie. Cookie-authenticated requests that change state
    (anything other than GET/HEAD/OPTIONS) must also carry a valid
    X-CSRF-Token header; otherwise 403 is returned.

    Authentication failures intentionally return 401 and do
    not expose authorization or organizational information.
    """

    token, came_from_cookie = extract_access_token(request, header_token)

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if (
        came_from_cookie
        and request.method.upper() not in SAFE_METHODS
        and not is_valid_csrf(
            token,
            request.headers.get(CSRF_HEADER_NAME),
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed.",
        )

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    subject = payload.get("sub")

    if not subject or not isinstance(subject, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    user = (
        db.query(User)
        .filter(User.email == subject)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user