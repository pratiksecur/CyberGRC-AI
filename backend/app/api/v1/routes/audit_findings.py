from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session


from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_user_in_scope
from app.auth.tenant import apply_tenant_filter


from app.models.audit import Audit
from app.models.control import Control
from app.models.audit_finding import AuditFinding
from app.models.user import User


from app.schemas.audit_finding import (
    AuditFindingCreate,
    AuditFindingUpdate,
    AuditFindingResponse,
)


from app.services.audit_finding_service import (
    create_audit_finding,
    update_audit_finding,
    delete_audit_finding,
)


router = APIRouter(
    prefix="/audit-findings",
    tags=["Audit Findings"],
)


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "/",
    response_model=AuditFindingResponse,
)
def create_new_audit_finding(
    finding_data: AuditFindingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("audit_findings", "create")
    ),
):
    """
    Create an audit finding.

    Tenant rules:
    - The parent audit must be within the current user's scope.
    - The referenced control must exist.
    - Audit and control must belong to the same organization.
    - The organization is inherited from the audit.
    - The client cannot choose the finding's organization.
    """

    # ------------------------------------------------------
    # Resolve parent audit
    # ------------------------------------------------------

    audit = (
        apply_tenant_filter(
            db.query(Audit),
            Audit,
            current_user,
        )
        .filter(
            Audit.id == finding_data.audit_id,
        )
        .first()
    )

    if audit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    # ------------------------------------------------------
    # Verify audit visibility
    # ------------------------------------------------------

    ensure_user_in_scope(
        db,
        current_user,
        audit.auditor_id,
        "audit_findings",
    )

    # ------------------------------------------------------
    # Resolve control
    # ------------------------------------------------------

    control = (
        apply_tenant_filter(
            db.query(Control),
            Control,
            current_user,
        )
        .filter(
            Control.id == finding_data.control_id,
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    # ------------------------------------------------------
    # Tenant boundary
    #
    # A finding connects an Audit and a Control.
    # Those resources must belong to the same organization.
    # ------------------------------------------------------

    if (
        audit.organization_id is None
        or control.organization_id is None
        or audit.organization_id != control.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Audit and control must belong to the same "
                "organization."
            ),
        )

    # ------------------------------------------------------
    # Create finding
    #
    # The service derives organization_id from the audit.
    # It is never accepted from the client.
    # ------------------------------------------------------

    finding = create_audit_finding(
        db,
        finding_data,
    )

    if finding == "AUDIT_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    if finding == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    if finding == "ORGANIZATION_MISMATCH":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Audit and control must belong to the same "
                "organization."
            ),
        )

    return finding


# ==========================================================
# LIST
# ==========================================================

@router.get(
    "/",
    response_model=list[AuditFindingResponse],
)
def list_all_findings(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("audit_findings", "view")
    ),
):
    """
    Return only findings belonging to audits within the
    authenticated user's visibility scope.

    Tenant isolation is additionally enforced through the
    audit relationship and resource organization.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "audit_findings",
    )

    results = (
        db.query(
            AuditFinding,
            Audit.name,
            Control.title,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .join(
            Control,
            AuditFinding.control_id == Control.id,
        )
        .filter(
            Audit.auditor_id.in_(visible_user_ids),
            Audit.organization_id == current_user.organization_id,
            AuditFinding.organization_id == current_user.organization_id,
            Control.organization_id == current_user.organization_id,
        )
        .all()
    )

    return [
        {
            "id": finding.id,
            "audit_id": finding.audit_id,
            "audit_name": audit_name,
            "control_id": finding.control_id,
            "control_name": control_name,
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity,
            "recommendation": finding.recommendation,
            "status": finding.status,
            "created_at": finding.created_at,
            "updated_at": finding.updated_at,
        }
        for finding, audit_name, control_name in results
    ]


# ==========================================================
# GET ONE
# ==========================================================

@router.get(
    "/{finding_id}",
    response_model=AuditFindingResponse,
)
def get_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("audit_findings", "view")
    ),
):
    """
    Return a finding only if:

    - The finding is within the user's visibility scope.
    - The finding belongs to the user's organization.
    - Its parent audit belongs to the same organization.
    - Its control belongs to the same organization.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "audit_findings",
    )

    result = (
        db.query(
            AuditFinding,
            Audit.name,
            Control.title,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .join(
            Control,
            AuditFinding.control_id == Control.id,
        )
        .filter(
            AuditFinding.id == finding_id,
            Audit.auditor_id.in_(visible_user_ids),
            Audit.organization_id == current_user.organization_id,
            AuditFinding.organization_id == current_user.organization_id,
            Control.organization_id == current_user.organization_id,
        )
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    finding, audit_name, control_name = result

    return {
        "id": finding.id,
        "audit_id": finding.audit_id,
        "audit_name": audit_name,
        "control_id": finding.control_id,
        "control_name": control_name,
        "title": finding.title,
        "description": finding.description,
        "severity": finding.severity,
        "recommendation": finding.recommendation,
        "status": finding.status,
        "created_at": finding.created_at,
        "updated_at": finding.updated_at,
    }


# ==========================================================
# UPDATE
# ==========================================================

@router.patch(
    "/{finding_id}",
    response_model=AuditFindingResponse,
)
def update_existing_finding(
    finding_id: int,
    finding_data: AuditFindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("audit_findings", "update")
    ),
):
    """
    Update an audit finding.

    Tenant rules:
    - Existing finding must belong to the current organization.
    - Existing finding must be within the user's visibility scope.
    - A replacement audit must belong to the current organization.
    - A replacement control must belong to the current organization.
    - If both audit/control are involved, they must belong to
      the same organization.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "audit_findings",
    )

    # ------------------------------------------------------
    # Resolve existing finding within tenant + visibility
    # ------------------------------------------------------

    finding = (
        db.query(AuditFinding)
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            AuditFinding.id == finding_id,
            Audit.auditor_id.in_(visible_user_ids),
            AuditFinding.organization_id == current_user.organization_id,
            Audit.organization_id == current_user.organization_id,
        )
        .first()
    )

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    # ------------------------------------------------------
    # Resolve current control
    # ------------------------------------------------------

    current_control = (
        apply_tenant_filter(
            db.query(Control),
            Control,
            current_user,
        )
        .filter(
            Control.id == finding.control_id,
        )
        .first()
    )

    if current_control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    if current_control.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    # ------------------------------------------------------
    # Validate replacement audit
    # ------------------------------------------------------

    target_audit = (
        apply_tenant_filter(
            db.query(Audit),
            Audit,
            current_user,
        )
        .filter(
            Audit.id == finding_data.audit_id
            if finding_data.audit_id is not None
            else Audit.id == finding.audit_id
        )
        .first()
    )

    if target_audit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    # The target audit must belong to the current organization.
    if target_audit.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-organization audit access is not permitted.",
        )

    # If changing the audit, validate its visibility scope.
    if finding_data.audit_id is not None:
        ensure_user_in_scope(
            db,
            current_user,
            target_audit.auditor_id,
            "audit_findings",
        )

    # ------------------------------------------------------
    # Validate replacement control
    # ------------------------------------------------------

    target_control = current_control

    if finding_data.control_id is not None:

        target_control = (
            apply_tenant_filter(
                db.query(Control),
                Control,
                current_user,
            )
            .filter(
                Control.id == finding_data.control_id,
            )
            .first()
        )

        if target_control is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Control not found.",
            )

        if target_control.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Cross-organization control access "
                    "is not permitted."
                ),
            )

    # ------------------------------------------------------
    # Final tenant consistency check
    # ------------------------------------------------------

    if (
        target_audit.organization_id
        != target_control.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Audit and control must belong to the same "
                "organization."
            ),
        )

    # ------------------------------------------------------
    # Update finding
    # ------------------------------------------------------

    finding = update_audit_finding(
        db,
        finding_id,
        finding_data,
    )

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    if finding == "AUDIT_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    if finding == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    if finding == "ORGANIZATION_MISMATCH":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Audit and control must belong to the same "
                "organization."
            ),
        )

    return finding


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{finding_id}",
)
def delete_existing_finding(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("audit_findings", "delete")
    ),
):
    """
    Delete an audit finding only if:

    - It belongs to the current organization.
    - Its parent audit belongs to the current organization.
    - Its parent audit is within the user's visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "audit_findings",
    )

    finding = (
        db.query(AuditFinding)
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            AuditFinding.id == finding_id,
            Audit.auditor_id.in_(visible_user_ids),
            AuditFinding.organization_id == current_user.organization_id,
            Audit.organization_id == current_user.organization_id,
        )
        .first()
    )

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    deleted = delete_audit_finding(
        db,
        finding_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    return {
        "message": "Audit finding deleted successfully."
    }