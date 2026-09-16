import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.provider_factory import get_ai_provider
from app.ai.prompts import EXECUTIVE_DASHBOARD_PROMPT

from app.auth.visibility import get_visible_user_ids

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.risk import Risk
from app.models.user import User

from app.schemas.ai import (
    ExecutiveDashboardResponse,
)


def generate_executive_dashboard(
    db: Session,
    current_user: User,
) -> ExecutiveDashboardResponse:
    """
    Generate the GRC Manager's AI Executive Summary.

    Operational records are restricted to the current
    user's appropriate visibility scope.

    Corrective actions require BOTH the assigned user
    and parent audit to be within the user's scope.
    """

    # ==================================================
    # AUTHORIZED USER SCOPES
    # ==================================================

    risk_visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    control_visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "controls",
    )

    evidence_visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "evidence",
    )

    audit_visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "audits",
    )

    action_visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "corrective_actions",
    )

    # ==================================================
    # FETCH SCOPED DATA
    # ==================================================

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(
                risk_visible_user_ids
            )
        )
        .all()
    )

    controls = (
        db.query(Control)
        .filter(
            Control.owner_id.in_(
                control_visible_user_ids
            )
        )
        .all()
    )

    # Frameworks are reference data.
    frameworks = (
        db.query(Framework)
        .all()
    )

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.uploaded_by.in_(
                evidence_visible_user_ids
            )
        )
        .all()
    )

    audits = (
        db.query(Audit)
        .filter(
            Audit.auditor_id.in_(
                audit_visible_user_ids
            )
        )
        .all()
    )

    # ==================================================
    # CORRECTIVE ACTIONS
    # ==================================================

    # A corrective action is visible only when:
    #
    #   assigned_to ∈ action scope
    #   AND
    #   parent audit auditor ∈ action scope
    #
    # This mirrors the API authorization boundary.

    corrective_actions = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id
            == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id
            == Audit.id,
        )
        .filter(
            CorrectiveAction.assigned_to.in_(
                action_visible_user_ids
            ),
            Audit.auditor_id.in_(
                action_visible_user_ids
            ),
        )
        .all()
    )

    # ==================================================
    # AUTHORITATIVE METRICS
    # ==================================================

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
        if str(action.status).lower()
        not in (
            "completed",
            "closed",
        )
    )

    # ==================================================
    # BUILD AI PROMPT
    # ==================================================

    prompt = EXECUTIVE_DASHBOARD_PROMPT.format(
        total_risks=total_risks,
        critical_risks=critical_risks,
        total_controls=total_controls,
        total_frameworks=total_frameworks,
        total_evidence=total_evidence,
        total_audits=total_audits,
        pending_actions=pending_actions,
    )

    # ==================================================
    # AI PROVIDER
    # ==================================================

    try:
        provider = get_ai_provider()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "AI provider initialization failed: "
                f"{str(e)}"
            ),
        )

    # ==================================================
    # GENERATE RESPONSE
    # ==================================================

    for attempt in range(2):

        try:
            response = provider.generate(
                prompt
            )

            cleaned_response = response.strip()

            # --------------------------------------------------
            # Remove JSON markdown fences
            # --------------------------------------------------

            if cleaned_response.startswith(
                "```json"
            ):
                cleaned_response = (
                    cleaned_response[7:]
                    .strip()
                )

                if cleaned_response.endswith(
                    "```"
                ):
                    cleaned_response = (
                        cleaned_response[:-3]
                        .strip()
                    )

            elif cleaned_response.startswith(
                "```"
            ):
                cleaned_response = (
                    cleaned_response[3:]
                    .strip()
                )

                if cleaned_response.endswith(
                    "```"
                ):
                    cleaned_response = (
                        cleaned_response[:-3]
                        .strip()
                    )

            response_json = json.loads(
                cleaned_response
            )

            return ExecutiveDashboardResponse(
                **response_json
            )

        except (
            json.JSONDecodeError,
            ValidationError,
        ):

            if attempt == 0:

                prompt += """

IMPORTANT

Return ONLY valid JSON.

Do not use markdown.

Do not include explanations outside
the JSON object.

Return ONLY the required JSON object.
"""

                continue

            raise HTTPException(
                status_code=500,
                detail=(
                    "AI returned invalid JSON "
                    "after retry."
                ),
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    "AI executive summary failed: "
                    f"{str(e)}"
                ),
            )

    raise HTTPException(
        status_code=500,
        detail=(
            "Unable to generate executive summary."
        ),
    )