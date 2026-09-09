from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import (
    require_permission,
)

from app.auth.visibility import (
    get_visible_user_ids,
)

from app.auth.access import (
    ensure_resource_owner_in_scope,
)

from app.models.control import Control
from app.models.user import User

from app.schemas.control import (
    ControlCreate,
    ControlUpdate,
    ControlResponse,
)

from app.services.control_service import (
    create_control,
    get_all_controls,
    get_control_by_id,
    update_control,
    delete_control,
)


router = APIRouter(
    prefix="/controls",
    tags=["Controls Management"]
)


@router.post(
    "/",
    response_model=ControlResponse
)
def create_new_control(
    control_data: ControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "controls",
            "create"
        )
    )
):
    """
    Create a new control.

    The creator is always derived from the
    authenticated user. The owner must be within
    the creator's organizational visibility scope.
    """

    ensure_resource_owner_in_scope(
        db,
        current_user,
        control_data.owner_id
    )

    control = create_control(
        db,
        control_data,
        current_user.id
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return control


@router.get(
    "/",
    response_model=list[ControlResponse]
)
def list_all_controls(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "controls",
            "view"
        )
    )
):
    """
    Get controls visible to the current user.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user
    )

    return (
        db.query(Control)
        .filter(
            Control.owner_id.in_(
                visible_user_ids
            )
        )
        .all()
    )


@router.get(
    "/{control_id}",
    response_model=ControlResponse
)
def get_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "controls",
            "view"
        )
    )
):
    """
    Get a control by ID if its owner is
    within the current user's visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user
    )

    control = (
        db.query(Control)
        .filter(
            Control.id == control_id,
            Control.owner_id.in_(
                visible_user_ids
            )
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    return control


@router.patch(
    "/{control_id}",
    response_model=ControlResponse
)
def update_existing_control(
    control_id: int,
    control_data: ControlUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "controls",
            "update"
        )
    )
):
    """
    Update an existing control within
    the current user's organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user
    )

    control = (
        db.query(Control)
        .filter(
            Control.id == control_id,
            Control.owner_id.in_(
                visible_user_ids
            )
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    if control_data.owner_id is not None:

        ensure_resource_owner_in_scope(
            db,
            current_user,
            control_data.owner_id
        )

    updated_control = update_control(
        db,
        control_id,
        control_data
    )

    if updated_control == "OWNER_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return updated_control


@router.delete(
    "/{control_id}"
)
def delete_existing_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "controls",
            "delete"
        )
    )
):
    """
    Delete an existing control within
    the current user's organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user
    )

    control = (
        db.query(Control)
        .filter(
            Control.id == control_id,
            Control.owner_id.in_(
                visible_user_ids
            )
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    deleted = delete_control(
        db,
        control_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    return {
        "message": "Control deleted successfully."
    }