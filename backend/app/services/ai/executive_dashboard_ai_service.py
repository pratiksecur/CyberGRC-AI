import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.governance import (
    AIGovernanceError,
    record_ai_event,
    secure_prompt,
    validate_ai_model,
    validate_raw_response,
)
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


def _clean_json_response(response: str) -> str:
    """
    Remove optional Markdown JSON fences while preserving
    the actual JSON payload.
    """

    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    return cleaned


def generate_executive_dashboard(
    db: Session,
    current_user: User,
) -> ExecutiveDashboardResponse:
    """
    Generate the GRC Manager's AI Executive Summary.

    Operational records are restricted to the current
    user's appropriate visibility scope.

    Corrective actions require BOTH:
    - assigned user within scope
    - parent audit within scope

    All numerical metrics are calculated by the application
    and are supplied to the AI as factual context.
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
        not in {
            "completed",
            "closed",
        }
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
    # SECURE PROMPT
    # ==================================================

    try:
        prompt = secure_prompt(prompt)

    except AIGovernanceError:
        record_ai_event(
            "executive_dashboard",
            model="unknown",
            outcome="rejected",
            validation="prompt",
        )

        raise HTTPException(
            status_code=503,
            detail="AI request could not be processed.",
        )

    # ==================================================
    # AI PROVIDER
    # ==================================================

    try:
        provider = get_ai_provider()

    except Exception:
        record_ai_event(
            "executive_dashboard",
            model="unknown",
            outcome="failure",
            validation="provider_initialization",
        )

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable.",
        )

    model_name = getattr(
        provider,
        "model",
        "unknown",
    )

    # ==================================================
    # GENERATE RESPONSE
    # ==================================================

    for attempt in range(2):

        try:

            response = validate_raw_response(
                provider.generate(prompt)
            )

            cleaned_response = _clean_json_response(
                response
            )

            response_json = json.loads(
                cleaned_response
            )

            if not isinstance(
                response_json,
                dict,
            ):
                raise AIGovernanceError(
                    "AI output must be a JSON object."
                )

            result = validate_ai_model(
                response_json,
                ExecutiveDashboardResponse,
            )

            record_ai_event(
                "executive_dashboard",
                model=model_name,
                outcome="success",
                validation="schema",
            )

            return result

        except AIGovernanceError:

            if attempt == 0:
                prompt += """

IMPORTANT

Your previous response was invalid.

Return ONLY valid JSON.

Do not use markdown.

Do not include explanations outside
the JSON object.

Return ONLY the required JSON object.
"""
                continue

            record_ai_event(
                "executive_dashboard",
                model=model_name,
                outcome="rejected",
                validation="governance",
            )

            raise HTTPException(
                status_code=502,
                detail="AI returned an invalid response after retry.",
            )

        except json.JSONDecodeError:

            if attempt == 0:
                prompt += """

IMPORTANT

Your previous response was invalid.

Return ONLY valid JSON.

Do not use markdown.

Do not include explanations outside
the JSON object.

Return ONLY the required JSON object.
"""
                continue

            record_ai_event(
                "executive_dashboard",
                model=model_name,
                outcome="rejected",
                validation="json",
            )

            raise HTTPException(
                status_code=502,
                detail="AI returned invalid JSON after retry.",
            )

        except Exception:

            record_ai_event(
                "executive_dashboard",
                model=model_name,
                outcome="failure",
                validation="provider",
            )

            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable.",
            )

    raise HTTPException(
        status_code=503,
        detail="Unable to generate executive summary.",
    )