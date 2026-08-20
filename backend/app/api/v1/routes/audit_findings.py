from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.audit_finding import (
    AuditFindingCreate,
    AuditFindingUpdate,
    AuditFindingResponse,
)

from app.services.audit_finding_service import (
    create_audit_finding,
    get_all_audit_findings,
    get_audit_finding_by_id,
    update_audit_finding,
    delete_audit_finding,
)


router = APIRouter(
    prefix="/audit-findings",
    tags=["Audit Findings"]
)


# ============================================================
# CREATE AUDIT FINDING
# ============================================================

@router.post(
    "/",
    response_model=AuditFindingResponse
)
def create_finding(
    finding_data: AuditFindingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):

    finding = create_audit_finding(
        db,
        finding_data
    )

    if finding == "AUDIT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Audit not found."
        )

    if finding == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    return finding


# ============================================================
# LIST ALL AUDIT FINDINGS
# ============================================================

@router.get(
    "/",
    response_model=list[AuditFindingResponse]
)
def list_findings(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):

    return get_all_audit_findings(db)


# ============================================================
# GET SINGLE AUDIT FINDING
# ============================================================

@router.get(
    "/{finding_id}",
    response_model=AuditFindingResponse
)
def get_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):

    finding = get_audit_finding_by_id(
        db,
        finding_id,
    )

    if finding is None:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    return finding


# ============================================================
# UPDATE AUDIT FINDING
# ============================================================

@router.patch(
    "/{finding_id}",
    response_model=AuditFindingResponse
)
def update_finding(
    finding_id: int,
    finding_data: AuditFindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):

    finding = update_audit_finding(
        db,
        finding_id,
        finding_data,
    )

    if finding is None:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    if finding == "AUDIT_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Audit not found."
        )

    if finding == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    return finding


# ============================================================
# DELETE AUDIT FINDING
# ============================================================

@router.delete(
    "/{finding_id}"
)
def delete_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):

    deleted = delete_audit_finding(
        db,
        finding_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Finding not found."
        )

    return {
        "message": "Finding deleted successfully."
    }