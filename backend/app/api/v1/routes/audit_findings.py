from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_user_in_scope

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

    The finding must belong to an audit whose
    assigned auditor is within the user's scope.

    The referenced control must exist, but its owner
    does not determine the finding's organizational scope.
    """

    audit = (
        db.query(Audit)
        .filter(Audit.id == finding_data.audit_id)
        .first()
    )

    if audit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    # The audit's assigned auditor determines
    # whether the finding is within scope.
    ensure_user_in_scope(
        db,
        current_user,
        audit.auditor_id,
        "audit_findings",
    )

    control = (
        db.query(Control)
        .filter(Control.id == finding_data.control_id)
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

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

    return finding


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
    Return only findings belonging to audits
    within the authenticated user's visibility scope.
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
            Audit.auditor_id.in_(visible_user_ids)
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
    Return a finding only if its parent audit
    is within the authenticated user's scope.
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

    The existing finding must be within the user's scope.

    If the finding is moved to another audit, the new audit's
    assigned auditor must also be within the user's scope.

    A new control only needs to exist because the control
    itself does not determine the finding's organizational scope.
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
        )
        .first()
    )

    if finding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit finding not found.",
        )

    # If changing the audit, validate the new audit's scope.
    if finding_data.audit_id is not None:

        new_audit = (
            db.query(Audit)
            .filter(
                Audit.id == finding_data.audit_id
            )
            .first()
        )

        if new_audit is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found.",
            )

        ensure_user_in_scope(
            db,
            current_user,
            new_audit.auditor_id,
            "audit_findings",
        )

    # If changing the control, only verify that it exists.
    if finding_data.control_id is not None:

        new_control = (
            db.query(Control)
            .filter(
                Control.id == finding_data.control_id
            )
            .first()
        )

        if new_control is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Control not found.",
            )

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

    return finding


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
    Delete an audit finding only if its parent audit
    is within the authenticated user's scope.
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