from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.audit import (
    AuditCreate,
    AuditUpdate,
    AuditResponse,
)

from app.services.audit_service import (
    create_audit,
    get_all_audits,
    get_audit_by_id,
    update_audit,
    delete_audit,
)

router = APIRouter(
    prefix="/audits",
    tags=["Audit Management"]
)


@router.post(
    "/",
    response_model=AuditResponse
)
def create_new_audit(
    audit_data: AuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Create a new audit.
    """

    audit = create_audit(
        db,
        audit_data
    )

    if audit == "FRAMEWORK_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Framework not found."
        )

    if audit == "AUDITOR_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Auditor not found."
        )

    if audit == "INVALID_DATES":
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date."
        )

    return audit


@router.get(
    "/",
    response_model=list[AuditResponse]
)
def list_all_audits(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get all audits.
    """

    return get_all_audits(db)


@router.get(
    "/{audit_id}",
    response_model=AuditResponse
)
def get_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get audit by ID.
    """

    audit = get_audit_by_id(
        db,
        audit_id,
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found."
        )

    return audit


@router.patch(
    "/{audit_id}",
    response_model=AuditResponse
)
def update_existing_audit(
    audit_id: int,
    audit_data: AuditUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Update an audit.
    """

    audit = update_audit(
        db,
        audit_id,
        audit_data,
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found."
        )

    if audit == "INVALID_DATES":
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date."
        )

    return audit


@router.delete(
    "/{audit_id}"
)
def delete_existing_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Delete an audit.
    """

    deleted = delete_audit(
        db,
        audit_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found."
        )

    return {
        "message": "Audit deleted successfully."
    }