from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids

from app.models.user import User

from app.schemas.reports import (
    RiskReportResponse,
    AuditReportResponse,
    ComplianceReportResponse,
)

from app.services.reports_service import (
    get_risk_report,
    get_audit_report,
    get_compliance_report,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/risks",
    response_model=RiskReportResponse,
)
def risk_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("reports", "view")
    ),
):
    """
    Generate a live risk report limited to
    risks within the authenticated user's scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "reports",
    )

    return get_risk_report(
        db,
        visible_user_ids,
    )


@router.get(
    "/audits",
    response_model=AuditReportResponse,
)
def audit_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("reports", "view")
    ),
):
    """
    Generate a live audit and findings report
    limited to audits within the authenticated
    user's scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "reports",
    )

    return get_audit_report(
        db,
        visible_user_ids,
    )


@router.get(
    "/compliance",
    response_model=ComplianceReportResponse,
)
def compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("reports", "view")
    ),
):
    """
    Generate a live compliance report limited
    to controls and related data within scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "reports",
    )

    return get_compliance_report(
        db,
        visible_user_ids,
    )