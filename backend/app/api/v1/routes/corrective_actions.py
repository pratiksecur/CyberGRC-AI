from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.corrective_action import (
    CorrectiveActionCreate,
    CorrectiveActionUpdate,
    CorrectiveActionResponse,
)

from app.services.corrective_action_service import (
    create_corrective_action,
    get_all_corrective_actions,
    get_corrective_action_by_id,
    update_corrective_action,
    delete_corrective_action,
)

router = APIRouter(
    prefix="/corrective-actions",
    tags=["Corrective Actions"]
)


@router.post(
    "/",
    response_model=CorrectiveActionResponse
)
def create_action(
    action_data: CorrectiveActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    action = create_corrective_action(
        db,
        action_data
    )

    if action == "FINDING_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Audit finding not found."
        )

    if action == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found."
        )

    if action == "INVALID_DATES":
        raise HTTPException(
            status_code=400,
            detail="Completion date cannot be before due date."
        )

    return action


@router.get(
    "/",
    response_model=list[CorrectiveActionResponse]
)
def list_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    return get_all_corrective_actions(db)


@router.get(
    "/{action_id}",
    response_model=CorrectiveActionResponse
)
def get_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    action = get_corrective_action_by_id(
        db,
        action_id
    )

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Corrective action not found."
        )

    return action


@router.patch(
    "/{action_id}",
    response_model=CorrectiveActionResponse
)
def update_action(
    action_id: int,
    action_data: CorrectiveActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    action = update_corrective_action(
        db,
        action_id,
        action_data
    )

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Corrective action not found."
        )

    if action == "INVALID_DATES":
        raise HTTPException(
            status_code=400,
            detail="Completion date cannot be before due date."
        )

    return action


@router.delete(
    "/{action_id}"
)
def delete_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    deleted = delete_corrective_action(
        db,
        action_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Corrective action not found."
        )

    return {
        "message": "Corrective action deleted successfully."
    }