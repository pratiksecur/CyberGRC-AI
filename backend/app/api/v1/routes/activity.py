from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.database.database import get_db
from app.models.user import User
from app.schemas.activity import ActivityResponse
from app.services.activity_service import get_recent_activity


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/activity",
    response_model=list[ActivityResponse],
)
def recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("risks", "view")
    ),
):
    """
    Return recent risk activity within the
    authenticated user's risk visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    return get_recent_activity(
        db,
        visible_user_ids,
    )