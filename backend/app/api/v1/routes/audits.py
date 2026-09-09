from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_user_in_scope

from app.models.user import User
from app.models.audit import Audit

from app.schemas.audit import (
    AuditCreate,
    AuditUpdate,
    AuditResponse,
)

from app.services.audit_service import (
    create_audit,
    update_audit,
    delete_audit,
)


router = APIRouter(
    prefix="/audits",
    tags=["Audit Management"],
)


@router.post(
    "/",
    response_model=AuditResponse,
)
def create_new_audit(
    audit_data: AuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "audits",
            "create",
        )
    ),
):
    """
    Create a new audit.

    The creator is always the authenticated user.
    The assigned auditor must be within the creator's
    organizational scope.
    """

    # ------------------------------------------------------
    # Verify assigned auditor is within user's scope
    # ------------------------------------------------------

    ensure_user_in_scope(
        db,
        current_user,
        audit_data.auditor_id,
    )

    # ------------------------------------------------------
    # Create audit
    # ------------------------------------------------------

    audit = create_audit(
        db,
        audit_data,
        current_user.id,
    )

    if audit == "FRAMEWORK_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Framework not found.",
        )

    if audit == "AUDITOR_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Auditor not found.",
        )

    if audit == "CREATOR_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Creator not found.",
        )

    if audit == "INVALID_DATES":
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date.",
        )

    return audit


@router.get(
    "/",
    response_model=list[AuditResponse],
)
def list_all_audits(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "audits",
            "view",
        )
    ),
):
    """
    Get audits assigned to users within the
    current user's organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    return (
        db.query(Audit)
        .filter(
            Audit.auditor_id.in_(visible_user_ids)
        )
        .all()
    )


@router.get(
    "/{audit_id}",
    response_model=AuditResponse,
)
def get_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "audits",
            "view",
        )
    ),
):
    """
    Get an audit if its assigned auditor
    is within the current user's scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == audit_id,
            Audit.auditor_id.in_(visible_user_ids),
        )
        .first()
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found.",
        )

    return audit


@router.patch(
    "/{audit_id}",
    response_model=AuditResponse,
)
def update_existing_audit(
    audit_id: int,
    audit_data: AuditUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "audits",
            "update",
        )
    ),
):
    """
    Update an audit within the user's
    organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == audit_id,
            Audit.auditor_id.in_(visible_user_ids),
        )
        .first()
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found.",
        )

    # ------------------------------------------------------
    # Validate new auditor if reassigned
    # ------------------------------------------------------

    if audit_data.auditor_id is not None:
        ensure_user_in_scope(
            db,
            current_user,
            audit_data.auditor_id,
        )

        auditor = (
            db.query(User)
            .filter(
                User.id == audit_data.auditor_id
            )
            .first()
        )

        if auditor is None:
            raise HTTPException(
                status_code=404,
                detail="Auditor not found.",
            )

    audit = update_audit(
        db,
        audit_id,
        audit_data,
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found.",
        )

    if audit == "INVALID_DATES":
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date.",
        )

    return audit


@router.delete(
    "/{audit_id}",
)
def delete_existing_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "audits",
            "delete",
        )
    ),
):
    """
    Delete an audit within the user's
    organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
    )

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == audit_id,
            Audit.auditor_id.in_(visible_user_ids),
        )
        .first()
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found.",
        )

    deleted = delete_audit(
        db,
        audit_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found.",
        )

    return {
        "message": "Audit deleted successfully.",
    }