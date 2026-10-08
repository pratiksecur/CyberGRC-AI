from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.user import User

from app.schemas.corrective_action import (
    CorrectiveActionCreate,
    CorrectiveActionResponse,
    CorrectiveActionUpdate,
    CorrectiveActionAssigneeResponse,
)

from app.services.corrective_action_service import (
    create_corrective_action,
    get_corrective_action_by_id,
    get_corrective_actions_for_finding,
    update_corrective_action,
    delete_corrective_action,
    serialize_corrective_action,
)

from app.auth.dependencies import get_current_user
from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids


router = APIRouter(
    prefix="/corrective-actions",
    tags=["Corrective Actions"],
)


# ==========================================================
# PERMISSION HELPERS
# ==========================================================


def _ensure_permission(
    current_user: User,
    resource: str,
    action: str,
):
    """
    Enforce the project's existing permission dependency.

    require_permission() returns a FastAPI dependency callable,
    so permission checking is performed against the authenticated
    user through the existing project permission mechanism.
    """

    permission_dependency = require_permission(
        resource,
        action,
    )

    try:
        permission_dependency(current_user)
    except HTTPException:
        raise


# ==========================================================
# LIST CORRECTIVE ACTIONS
# ==========================================================


@router.get(
    "/",
    response_model=list[CorrectiveActionResponse],
)
def list_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List corrective actions visible to the current user.

    Tenant isolation is enforced before RBAC visibility.

    Response objects are explicitly serialized so that the
    relationship-derived fields required by CorrectiveActionResponse
    are included.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource="corrective_actions",
    )

    actions = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.organization_id
            == current_user.organization_id,
            CorrectiveAction.assigned_to.in_(visible_user_ids),
        )
        .all()
    )

    return [
        serialize_corrective_action(action)
        for action in actions
    ]


# ==========================================================
# LIST ASSIGNEES
# ==========================================================


@router.get(
    "/assignees",
    response_model=list[CorrectiveActionAssigneeResponse],
)
def list_assignees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get users that can be selected when assigning
    a corrective action.

    Only users belonging to the current organization
    and visible under the existing RBAC hierarchy
    are returned.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource="corrective_actions",
    )

    users = (
        db.query(User)
        .filter(
            User.id.in_(visible_user_ids),
            User.organization_id == current_user.organization_id,
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


# ==========================================================
# CREATE CORRECTIVE ACTION
# ==========================================================


@router.post(
    "/",
    response_model=CorrectiveActionResponse,
)
def create_action(
    action_data: CorrectiveActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a corrective action.

    Tenant rules:
    - Finding must belong to current organization.
    - Assignee must belong to current organization.
    - Organization is derived from authenticated context.
    """

    _ensure_permission(
        current_user,
        "corrective_actions",
        "create",
    )

    finding = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.id == action_data.finding_id,
            AuditFinding.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found.",
        )

    assignee = (
        db.query(User)
        .filter(
            User.id == action_data.assigned_to,
            User.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if assignee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found.",
        )

    result = create_corrective_action(
        db,
        action_data,
    )

    if result == "FINDING_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found.",
        )

    if result == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found.",
        )

    if result == "INVALID_DATES":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed date cannot be earlier than due date.",
        )

    return result


# ==========================================================
# GET CORRECTIVE ACTION
# ==========================================================


@router.get(
    "/{action_id}",
    response_model=CorrectiveActionResponse,
)
def get_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a corrective action.

    Tenant isolation is enforced directly on the resource.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource="corrective_actions",
    )

    action = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.id == action_id,
            CorrectiveAction.organization_id
            == current_user.organization_id,
            CorrectiveAction.assigned_to.in_(visible_user_ids),
        )
        .first()
    )

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    return serialize_corrective_action(action)


# ==========================================================
# LIST ACTIONS FOR FINDING
# ==========================================================


@router.get(
    "/finding/{finding_id}",
    response_model=list[CorrectiveActionResponse],
)
def list_actions_for_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get corrective actions belonging to a finding.

    Both finding and corrective actions must belong to
    the authenticated user's organization.
    """

    finding = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.id == finding_id,
            AuditFinding.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found.",
        )

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource="corrective_actions",
    )

    actions = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.finding_id == finding_id,
            CorrectiveAction.organization_id
            == current_user.organization_id,
            CorrectiveAction.assigned_to.in_(visible_user_ids),
        )
        .all()
    )

    return [
        serialize_corrective_action(action)
        for action in actions
    ]


# ==========================================================
# UPDATE CORRECTIVE ACTION
# ==========================================================


@router.patch(
    "/{action_id}",
    response_model=CorrectiveActionResponse,
)
def update_action(
    action_id: int,
    action_data: CorrectiveActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a corrective action.

    Tenant enforcement:
    - Existing action must belong to current organization.
    - finding_id, when supplied, must reference a finding
      in the same organization.
    - assigned_to, when supplied, must reference a user
      in the same organization.
    - organization_id is never mutable.
    - Cross-tenant parent/assignee changes are rejected.
    """

    _ensure_permission(
        current_user,
        "corrective_actions",
        "update",
    )

    # ------------------------------------------------------
    # 1. Resolve existing action inside current tenant
    # ------------------------------------------------------

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource="corrective_actions",
    )

    action = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.id == action_id,
            CorrectiveAction.organization_id
            == current_user.organization_id,
            CorrectiveAction.assigned_to.in_(visible_user_ids),
        )
        .first()
    )

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    # ------------------------------------------------------
    # 2. Validate finding relationship
    # ------------------------------------------------------

    if action_data.finding_id is not None:

        target_finding = (
            db.query(AuditFinding)
            .filter(
                AuditFinding.id == action_data.finding_id,
                AuditFinding.organization_id
                == current_user.organization_id,
            )
            .first()
        )

        if target_finding is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Corrective action cannot be moved "
                    "to a finding in another organization."
                ),
            )

        if target_finding.organization_id != action.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Corrective action cannot be moved "
                    "across organizations."
                ),
            )

    # ------------------------------------------------------
    # 3. Validate assignee relationship
    # ------------------------------------------------------

    if action_data.assigned_to is not None:

        target_assignee = (
            db.query(User)
            .filter(
                User.id == action_data.assigned_to,
                User.organization_id
                == current_user.organization_id,
            )
            .first()
        )

        if target_assignee is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Corrective action cannot be assigned "
                    "to a user in another organization."
                ),
            )

        if target_assignee.organization_id != action.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Corrective action assignee must belong "
                    "to the same organization."
                ),
            )

    # ------------------------------------------------------
    # 4. Update relationship fields
    # ------------------------------------------------------

    if action_data.finding_id is not None:
        action.finding_id = action_data.finding_id

    if action_data.assigned_to is not None:
        action.assigned_to = action_data.assigned_to

    # ------------------------------------------------------
    # 5. Update normal fields through service
    # ------------------------------------------------------

    result = update_corrective_action(
        db,
        action_id,
        action_data,
    )

    if result == "INVALID_DATES":
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed date cannot be earlier than due date.",
        )

    if result is None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    # ------------------------------------------------------
    # 6. Final tenant integrity validation
    # ------------------------------------------------------

    db.refresh(
        db.query(CorrectiveAction)
        .filter(CorrectiveAction.id == action_id)
        .first()
    )

    final_action = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.id == action_id,
            CorrectiveAction.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if final_action is None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-organization corrective action detected.",
        )

    final_assignee = (
        db.query(User)
        .filter(
            User.id == final_action.assigned_to,
        )
        .first()
    )

    if (
        final_assignee is None
        or final_assignee.organization_id
        != current_user.organization_id
    ):
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Corrective action assignee must belong "
                "to the same organization."
            ),
        )

    final_finding = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.id == final_action.finding_id,
        )
        .first()
    )

    if (
        final_finding is None
        or final_finding.organization_id
        != current_user.organization_id
    ):
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Corrective action finding must belong "
                "to the same organization."
            ),
        )

    return serialize_corrective_action(final_action)


# ==========================================================
# DELETE CORRECTIVE ACTION
# ==========================================================


@router.delete(
    "/{action_id}",
)
def delete_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a corrective action.

    Tenant isolation is enforced before deletion.
    """

    _ensure_permission(
        current_user,
        "corrective_actions",
        "delete",
    )

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource="corrective_actions",
    )

    action = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.id == action_id,
            CorrectiveAction.organization_id
            == current_user.organization_id,
            CorrectiveAction.assigned_to.in_(visible_user_ids),
        )
        .first()
    )

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    result = delete_corrective_action(
        db,
        action_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corrective action not found.",
        )

    return {
        "message": "Corrective action deleted successfully."
    }