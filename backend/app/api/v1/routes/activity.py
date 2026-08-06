from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.activity import ActivityResponse
from app.services.activity_service import get_recent_activity

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/activity",
    response_model=list[ActivityResponse],
)
def recent_activity(
    db: Session = Depends(get_db),
):
    """
    Get the latest dashboard activity.
    """

    return get_recent_activity(db)