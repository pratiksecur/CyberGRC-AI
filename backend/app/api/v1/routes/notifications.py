from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import get_current_user

from app.models.user import User

from app.schemas.notification import (
    NotificationResponse,
    NotificationUnreadCountResponse,
    NotificationMessageResponse,
)

from app.services.notification_service import (
    get_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_notifications_read,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_notifications(
        db,
        current_user.id,
    )


@router.get(
    "/unread-count",
    response_model=NotificationUnreadCountResponse,
)
def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "unread_count": get_unread_count(
            db,
            current_user.id,
        )
    }


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = mark_notification_read(
        db,
        current_user.id,
        notification_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    return notification


@router.patch(
    "/read-all",
    response_model=NotificationMessageResponse,
)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mark_all_notifications_read(
        db,
        current_user.id,
    )

    return {
        "message": "All notifications marked as read.",
    }