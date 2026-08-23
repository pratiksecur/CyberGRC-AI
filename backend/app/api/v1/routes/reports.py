from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_roles
from app.core.roles import UserRole

from app.models.user import User

from app.schemas.reports import (
    RiskReportResponse,
)

from app.services.reports_service import (
    get_risk_report,
)

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
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    ),
):
    """
    Generate a live risk report.
    """

    return get_risk_report(db)

@router.get(
    "/audits",
    response_model=AuditReportResponse,
)
def audit_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    ),
):
    """
    Generate a live audit and findings report.
    """

    return get_audit_report(db)

@router.get(
    "/compliance",
    response_model=ComplianceReportResponse,
)
def compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    ),
):
    """
    Generate a live compliance report.
    """

    return get_compliance_report(db)