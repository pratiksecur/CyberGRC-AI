import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.provider_factory import get_ai_provider
from app.ai.prompts import EXECUTIVE_DASHBOARD_PROMPT

from app.schemas.ai import (
    ExecutiveDashboardResponse,
)

from app.services.risk_service import (
    get_all_risks,
)

from app.services.control_service import (
    get_all_controls,
)

from app.services.framework_service import (
    get_all_frameworks,
)

from app.services.evidence_service import (
    get_all_evidence,
)

from app.services.audit_service import (
    get_all_audits,
)

from app.services.corrective_action_service import (
    get_all_corrective_actions,
)


def generate_executive_dashboard(
    db: Session,
) -> ExecutiveDashboardResponse:
    """
    Generate an AI-powered executive cybersecurity dashboard.
    """

    # --------------------------------------------------
    # Fetch Data
    # --------------------------------------------------

    risks = get_all_risks(db)

    controls = get_all_controls(db)

    frameworks = get_all_frameworks(db)

    evidence = get_all_evidence(db)

    audits = get_all_audits(db)

    corrective_actions = get_all_corrective_actions(db)

    # --------------------------------------------------
    # Calculate Metrics
    # --------------------------------------------------

    total_risks = len(risks)

    critical_risks = sum(
        1
        for risk in risks
        if risk.risk_score >= 20
    )

    total_controls = len(controls)

    total_frameworks = len(frameworks)

    total_evidence = len(evidence)

    total_audits = len(audits)

    pending_actions = sum(
        1
        for action in corrective_actions
        if action.status.lower() != "completed"
    )

    # --------------------------------------------------
    # Build Prompt
    # --------------------------------------------------

    prompt = EXECUTIVE_DASHBOARD_PROMPT.format(
        total_risks=total_risks,
        critical_risks=critical_risks,
        total_controls=total_controls,
        total_frameworks=total_frameworks,
        total_evidence=total_evidence,
        total_audits=total_audits,
        pending_actions=pending_actions,
    )

    provider = get_ai_provider()

    # --------------------------------------------------
    # Retry on Invalid JSON
    # --------------------------------------------------

    for attempt in range(2):

        response = provider.generate(prompt)

        try:

            return ExecutiveDashboardResponse(
                **json.loads(response)
            )

        except (
            json.JSONDecodeError,
            ValidationError,
        ):

            if attempt == 0:

                prompt += """

IMPORTANT

Return ONLY valid JSON.

"""

                continue

            raise HTTPException(
                status_code=500,
                detail="AI returned invalid JSON."
            )