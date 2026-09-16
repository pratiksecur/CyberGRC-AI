from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids

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
        require_permission("reports", "view")
    ),
):
    """
    Generate a corrective actions report limited
    to corrective actions within the authenticated
    user's report visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "reports",
    )

    return get_corrective_action_report(
        db,
        visible_user_ids,
    )