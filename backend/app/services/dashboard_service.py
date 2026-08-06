from sqlalchemy.orm import Session

from app.services.risk_service import get_total_risks
from app.services.control_service import get_total_controls
from app.services.audit_service import get_total_audits


def get_dashboard_data(db: Session):
    """
    Get executive dashboard statistics.
    """

    total_risks = get_total_risks(db)

    total_controls = get_total_controls(db)

    total_audits = get_total_audits(db)

    return {
        "totalRisks": total_risks,
        "controls": total_controls,
        "audits": total_audits,

        # Temporary placeholders
        "compliance": 87,
        "securityHealth": 92,
        "criticalRisks": 3,
        "activeControls": total_controls,
    }