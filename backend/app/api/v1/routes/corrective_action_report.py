from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_roles
from app.core.roles import UserRole

from app.models.user import User

from app.schemas.corrective_action_report import (
    CorrectiveActionReportResponse,
)

from app.services.corrective_action_report_service import (
    get_corrective_action_report,
)


router = APIRouter(
    prefix="/reports/corrective-actions",
    tags=["Reports"],
)


@router.get(
    "/",
    response_model=CorrectiveActionReportResponse,
)
def corrective_action_report(
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
    Generate a corrective actions report.
    """

    return get_corrective_action_report(db)