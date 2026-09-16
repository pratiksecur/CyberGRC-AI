from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import (
    require_permission,
    get_access_scope,
)
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_user_in_scope
from app.auth.scopes import AccessScope

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


def _build_scoped_corrective_action_query(
    db: Session,
    current_user: User,
):
    """
    Build the corrective-action query according to the
    user's corrective-action visibility scope.

    OWN:
        Visibility is determined by assigned_to.

    SUBORDINATES / ORGANIZATION:
        Both assigned_to and the parent audit must be
        within the user's corrective-action scope.

    This preserves the distinction between a user's own
    assigned remediation work and management-level
    organizational visibility.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "corrective_actions",
    )

    query = (
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
            CorrectiveAction.assigned_to.in_(
                visible_user_ids
            )
        )
    )

    scope = get_access_scope(
        current_user,
        "corrective_actions",
    )

    if scope in (
        AccessScope.SUBORDINATES,
        AccessScope.ORGANIZATION,
    ):
        query = query.filter(
            Audit.auditor_id.in_(
                visible_user_ids
            )
        )

    return query


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

    Creation requires BOTH:
    1. The parent audit to be within the creator's scope.
    2. The assigned user to be within the creator's scope.

    This prevents creation against an out-of-scope finding
    or assignment to an out-of-scope user.
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

    # --------------------------------------------------
    # Parent audit authorization
    # --------------------------------------------------

    ensure_user_in_scope(
        db,
        current_user,
        audit.auditor_id,
        "corrective_actions",
    )

    # --------------------------------------------------
    # Assignee authorization
    # --------------------------------------------------

    ensure_user_in_scope(
        db,
        current_user,
        action_data.assigned_to,
        "corrective_actions",
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
    Return corrective actions according to the caller's
    corrective-action scope.

    OWN:
        Return actions assigned to the current user.

    SUBORDINATES / ORGANIZATION:
        Return actions where both the assignee and the
        parent audit are within the caller's scope.
    """

    query = _build_scoped_corrective_action_query(
        db,
        current_user,
    )

    actions = query.all()

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
    Return users that can be selected as corrective-action
    assignees within the current user's visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "corrective_actions",
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
    Return a corrective action according to the caller's
    corrective-action visibility scope.
    """

    action = (
        _build_scoped_corrective_action_query(
            db,
            current_user,
        )
        .filter(
            CorrectiveAction.id == action_id,
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
    Update a corrective action according to the caller's
    corrective-action visibility scope.
    """

    action = (
        _build_scoped_corrective_action_query(
            db,
            current_user,
        )
        .filter(
            CorrectiveAction.id == action_id,
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
    Delete a corrective action according to the caller's
    corrective-action visibility scope.
    """

    action = (
        _build_scoped_corrective_action_query(
            db,
            current_user,
        )
        .filter(
            CorrectiveAction.id == action_id,
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