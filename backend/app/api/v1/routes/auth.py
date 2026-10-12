from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user import (
    ChangePasswordRequest,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
)
from app.auth.auth_service import create_user, login_user
from app.auth.cookies import (
    CSRF_HEADER_NAME,
    clear_access_cookie,
    csrf_token_for,
    is_valid_csrf,
    set_access_cookie,
)
from app.auth.dependencies import extract_access_token, get_current_user, oauth2_scheme
from app.auth.emails import normalize_email
from app.auth.jwt_handler import create_access_token, verify_access_token
from app.auth.login_guard import (
    LoginBlocked,
    check_login_allowed,
    record_login_attempt,
)
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User
from app.services.account_service import change_own_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    """
    Create a user inside the signed-in administrator's organization.

    Self-registration is closed. The organization is always the
    administrator's own and is never taken from the request.
    """
    try:
        return create_user(
            db,
            user,
            organization_id=current_user.organization_id,
            role=user.role.value,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post(
    "/login",
    response_model=Token
)
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        result = login_user(
            db,
            form_data.username,
            form_data.password,
            ip_address=_client_ip(request),
        )

    except LoginBlocked as blocked:
        raise HTTPException(
            status_code=429,
            detail=(
                "Too many failed sign-in attempts. "
                "Try again later."
            ),
            headers={
                "Retry-After": str(blocked.retry_after_seconds),
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

    # The browser app relies on this httpOnly cookie. The token is still
    # returned in the body for API clients that send an Authorization header.
    set_access_cookie(response, result["access_token"])

    return result


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    header_token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    End the session.

    The cookie is always cleared. When the request carries a valid session
    (and, for cookie sessions, a valid CSRF token) the user's token version
    is raised as well, so the token stops working even if someone copied it.
    This signs the user out on every device.
    """
    token, came_from_cookie = extract_access_token(request, header_token)

    if token:
        payload = verify_access_token(token)

        csrf_ok = not came_from_cookie or is_valid_csrf(
            token,
            request.headers.get(CSRF_HEADER_NAME),
        )

        subject = payload.get("sub") if payload else None

        if csrf_ok and isinstance(subject, str):
            user = (
                db.query(User)
                .filter(func.lower(User.email) == normalize_email(subject))
                .first()
            )

            if user is not None and payload.get("ver", 0) == user.token_version:
                user.token_version = (user.token_version or 0) + 1
                db.commit()

    clear_access_cookie(response)

    return {"detail": "Logged out."}


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change the signed-in user's own password.

    Every other session is signed out; this one continues with a fresh
    token. Wrong current passwords count towards the sign-in limits, so a
    stolen session cannot be used to guess the password.
    """
    ip_address = _client_ip(request)
    email = normalize_email(current_user.email)

    try:
        check_login_allowed(db, email, ip_address)
    except LoginBlocked as blocked:
        raise HTTPException(
            status_code=429,
            detail="Too many failed attempts. Try again later.",
            headers={
                "Retry-After": str(blocked.retry_after_seconds),
            },
        )

    try:
        user = change_own_password(
            db,
            current_user,
            data.current_password,
            data.new_password,
        )

    except ValueError as e:
        if str(e) == "Current password is incorrect.":
            record_login_attempt(
                db,
                email,
                ip_address,
                success=False,
                reason="wrong_current_password",
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "ver": user.token_version,
        }
    )

    set_access_cookie(response, access_token)

    return {
        "detail": "Password changed.",
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/csrf")
def get_csrf_token(
    request: Request,
    header_token: str | None = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
):
    """
    Return the CSRF token for the current session.

    The browser app sends it back in the X-CSRF-Token header on every
    state-changing request.
    """
    token, _ = extract_access_token(request, header_token)

    return {"csrf_token": csrf_token_for(token)}

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get the currently logged-in user's details.
    """
    return current_user

@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    return {
        "message": f"Welcome Admin {current_user.full_name}",
        "role": current_user.role
    }

@router.get("/management")
def management_dashboard(
    current_user: User = Depends(
    require_roles(UserRole.ADMIN, UserRole.GRC_MANAGER)
    )
):
    return {
        "message": f"Welcome {current_user.full_name}",
        "role": current_user.role,
        "access": "Management Dashboard"
    }