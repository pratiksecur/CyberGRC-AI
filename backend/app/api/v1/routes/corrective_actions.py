from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_user_in_scope

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.user import User

from app.schemas.corrective_action import (
    CorrectiveActionCreate,
    CorrectiveActionUpdate,
    CorrectiveActionResponse,
    CorrectiveActionAssigneeResponse,
)

from app.services.corrective_action_service import (
    create_corrective_action,
    get_corrective_action_by_id,
    update_corrective_action,
    delete_corrective_action,
    _serialize_corrective_action,
)


router = APIRouter(
    prefix="/corrective-actions",
    tags=["Corrective Actions"],
)


@router.post(
    "/",
    response_model=CorrectiveActionResponse,
)
def create_action(
    action_data: CorrectiveActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("corrective_actions", "create")
    ),
):
    """
    Create a corrective action.

    The parent finding must belong to an audit
    within the user's organizational scope.

    The assigned user must also be within scope.
    """

    finding = (
        db.query(AuditFinding)
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            AuditFinding.id == action_data.finding_id,
        )
        .first()
    )

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == finding.audit_id,
        )
        .first()
    )

    if audit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    # The parent audit determines the action's scope.
    ensure_user_in_scope(
        db,
        current_user,
        audit.auditor_id,
    )

    # The assignee must be within the creator's scope.
    ensure_user_in_scope(
        db,
        current_user,
        action_data.assigned_to,
    )

    action = create_corrective_action(
        db,
        action_data,
    )

    if action == "FINDING_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    if action == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found.",
        )

    if action == "INVALID_DATES":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completion date cannot be before due date.",
        )

    return action


@router.get(
    "/",
    response_model=list[CorrectiveActionResponse],
)
def list_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("corrective_actions", "view")
    ),
):
    """
    Return only corrective actions whose parent
    finding belongs to an audit within scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    actions = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            Audit.auditor_id.in_(visible_user_ids)
        )
        .all()
    )

    return [
        _serialize_corrective_action(action)
        for action in actions
    ]


@router.get(
    "/assignees",
    response_model=list[CorrectiveActionAssigneeResponse],
)
def list_assignees(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("corrective_actions", "view")
    ),
):
    """
    Get users that can be selected when assigning
    a corrective action.

    Only users within the current user's organizational
    visibility scope are returned.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    users = (
        db.query(User)
        .filter(
            User.id.in_(visible_user_ids)
        )
        .order_by(
            User.full_name.asc()
        )
        .all()
    )

    return [
        {
            "id": user.id,
            "name": user.full_name,
        }
        for user in users
    ]


@router.get(
    "/{action_id}",
    response_model=CorrectiveActionResponse,
)
def get_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("corrective_actions", "view")
    ),
):
    """
    Return a corrective action only if its parent
    finding belongs to an audit within scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    action = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            CorrectiveAction.id == action_id,
            Audit.auditor_id.in_(visible_user_ids),
        )
        .first()
    )

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    return _serialize_corrective_action(action)


@router.patch(
    "/{action_id}",
    response_model=CorrectiveActionResponse,
)
def update_action(
    action_id: int,
    action_data: CorrectiveActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("corrective_actions", "update")
    ),
):
    """
    Update a corrective action only if its parent
    finding belongs to an audit within scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    action = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            CorrectiveAction.id == action_id,
            Audit.auditor_id.in_(visible_user_ids),
        )
        .first()
    )

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    updated_action = update_corrective_action(
        db,
        action_id,
        action_data,
    )

    if updated_action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    if updated_action == "INVALID_DATES":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completion date cannot be before due date.",
        )

    return updated_action


@router.delete(
    "/{action_id}",
)
def delete_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("corrective_actions", "delete")
    ),
):
    """
    Delete a corrective action only if its parent
    finding belongs to an audit within scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    action = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            CorrectiveAction.id == action_id,
            Audit.auditor_id.in_(visible_user_ids),
        )
        .first()
    )

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    deleted = delete_corrective_action(
        db,
        action_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    return {
        "message": "Corrective action deleted successfully."
    }