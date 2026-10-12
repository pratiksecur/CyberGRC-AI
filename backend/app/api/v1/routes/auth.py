from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.auth.auth_service import create_user, login_user
from app.auth.cookies import clear_access_cookie, csrf_token_for, set_access_cookie
from app.auth.dependencies import extract_access_token, get_current_user, oauth2_scheme
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    try:
        return create_user(db, user)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=Token
)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        result = login_user(
            db,
            form_data.username,
            form_data.password
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
def logout(response: Response):
    """
    End the browser session by clearing the session cookie.
    """
    clear_access_cookie(response)

    return {"detail": "Logged out."}


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