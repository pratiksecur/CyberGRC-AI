import json
from typing import Optional

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
from app.ai.prompts import AUDIT_SUMMARY_PROMPT

from app.auth.ai_access import get_authorized_audit
from app.auth.visibility import get_visible_user_ids

from app.models.user import User

from app.schemas.ai import AuditSummaryResponse

from app.services.audit_service import get_audit_by_id
from app.services.audit_finding_service import (
    get_findings_for_audit,
)
from app.services.corrective_action_service import (
    get_corrective_actions_for_finding,
)


def _get_value(item, key, default=None):
    """
    Safely retrieve a value from either:
    - SQLAlchemy model objects
    - dictionaries
    """

    if isinstance(item, dict):
        return item.get(key, default)

    return getattr(item, key, default)


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


def summarize_audit(
    db: Session,
    audit_id: int,
    current_user: Optional[User] = None,
) -> AuditSummaryResponse:
    """
    Generate an AI executive summary for an audit.

    When current_user is supplied, authorization is enforced
    inside the service layer as well as at the API route.

    Database-derived metrics are calculated independently
    and are never trusted to the AI model.

    AI is responsible only for:
    - Overall assessment
    - Executive summary
    - Priority recommendations
    """

    # ==========================================================
    # FETCH AUTHORIZED AUDIT
    # ==========================================================

    if current_user is not None:

        audit = get_authorized_audit(
            db,
            current_user,
            audit_id,
        )

    else:
        # Backward compatibility for existing internal callers
        # and tests. Public API routes always provide current_user.
        audit = get_audit_by_id(
            db,
            audit_id,
        )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found.",
        )

    # ==========================================================
    # AUTHORIZED CORRECTIVE-ACTION SCOPE
    # ==========================================================

    if current_user is not None:
        action_visible_user_ids = set(
            get_visible_user_ids(
                db,
                current_user,
                "corrective_actions",
            )
        )
    else:
        action_visible_user_ids = None

    # ==========================================================
    # FETCH FINDINGS
    # ==========================================================

    findings = get_findings_for_audit(
        db,
        audit_id,
    )

    # ==========================================================
    # DATABASE METRICS
    #
    # These values are calculated by the application.
    # The AI does NOT determine them.
    # ==========================================================

    critical_findings = 0
    open_findings = 0
    completed_actions = 0
    pending_actions = 0

    findings_text = ""
    actions_text = ""

    # ==========================================================
    # BUILD AI CONTEXT
    # ==========================================================

    if findings:

        for finding in findings:

            finding_id = _get_value(
                finding,
                "id",
            )

            finding_title = _get_value(
                finding,
                "title",
                "Untitled finding",
            )

            finding_severity = _get_value(
                finding,
                "severity",
                "Unknown",
            )

            finding_status = _get_value(
                finding,
                "status",
                "Unknown",
            )

            finding_recommendation = _get_value(
                finding,
                "recommendation",
                "No recommendation provided.",
            )

            # --------------------------------------------------
            # Calculate finding metrics
            # --------------------------------------------------

            if (
                str(finding_severity).lower()
                == "critical"
            ):
                critical_findings += 1

            if (
                str(finding_status).lower()
                in {
                    "open",
                    "in progress",
                }
            ):
                open_findings += 1

            # --------------------------------------------------
            # Add finding to AI context
            # --------------------------------------------------

            findings_text += f"""
Title: {finding_title}
Severity: {finding_severity}
Status: {finding_status}
Recommendation: {finding_recommendation}

"""

            # --------------------------------------------------
            # Fetch corrective actions
            # --------------------------------------------------

            if finding_id is None:
                continue

            actions = get_corrective_actions_for_finding(
                db,
                finding_id,
            )

            if not actions:
                continue

            for action in actions:

                action_assigned_to = _get_value(
                    action,
                    "assigned_to",
                )

                # --------------------------------------------------
                # Defense-in-depth action authorization
                #
                # A corrective action is included only when its
                # assignee is inside the caller's corrective-action
                # scope.
                # --------------------------------------------------

                if (
                    action_visible_user_ids is not None
                    and action_assigned_to
                    not in action_visible_user_ids
                ):
                    continue

                action_title = _get_value(
                    action,
                    "title",
                    "Untitled corrective action",
                )

                action_priority = _get_value(
                    action,
                    "priority",
                    "Unknown",
                )

                action_status = _get_value(
                    action,
                    "status",
                    "Unknown",
                )

                action_due_date = _get_value(
                    action,
                    "due_date",
                )

                # --------------------------------------------------
                # Calculate action metrics
                # --------------------------------------------------

                normalized_status = str(
                    action_status
                ).lower()

                if normalized_status in {
                    "completed",
                    "closed",
                }:
                    completed_actions += 1

                else:
                    pending_actions += 1

                # --------------------------------------------------
                # Add action to AI context
                # --------------------------------------------------

                actions_text += f"""
Title: {action_title}
Priority: {action_priority}
Status: {action_status}
Due Date: {action_due_date}

"""

    if not findings_text:
        findings_text = "No findings."

    if not actions_text:
        actions_text = "No corrective actions."

    # ==========================================================
    # BUILD PROMPT
    # ==========================================================

    prompt = AUDIT_SUMMARY_PROMPT.format(
        audit_name=_get_value(
            audit,
            "name",
            "Unnamed audit",
        ),
        audit_scope=_get_value(
            audit,
            "scope",
            "No scope provided.",
        ),
        audit_status=_get_value(
            audit,
            "status",
            "Unknown",
        ),
        findings=findings_text,
        actions=actions_text,
    )

    # ==========================================================
    # SECURE PROMPT
    # ==========================================================

    try:
        prompt = secure_prompt(prompt)

    except AIGovernanceError:
        record_ai_event(
            "audit_summary",
            model="unknown",
            outcome="rejected",
            validation="prompt",
        )

        raise HTTPException(
            status_code=503,
            detail="AI request could not be processed.",
        )

    # ==========================================================
    # AI PROVIDER
    # ==========================================================

    try:
        provider = get_ai_provider()

    except Exception:
        record_ai_event(
            "audit_summary",
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

    # ==========================================================
    # GENERATE AI RESPONSE
    # ==========================================================

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

            # ==================================================
            # AUTHORITATIVE DATABASE METRICS
            #
            # Never trust AI-generated numerical metrics.
            # ==================================================

            response_json[
                "critical_findings"
            ] = critical_findings

            response_json[
                "open_findings"
            ] = open_findings

            response_json[
                "completed_actions"
            ] = completed_actions

            response_json[
                "pending_actions"
            ] = pending_actions

            result = validate_ai_model(
                response_json,
                AuditSummaryResponse,
            )

            record_ai_event(
                "audit_summary",
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

Do not use ```json.

Do not include explanations outside the JSON object.

Return ONLY the JSON object matching the required schema.

The numerical metrics are handled by the application.
Do not invent or calculate them.
"""
                continue

            record_ai_event(
                "audit_summary",
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

Do not use ```json.

Do not include explanations outside the JSON object.

Return ONLY the JSON object matching the required schema.

The numerical metrics are handled by the application.
Do not invent or calculate them.
"""
                continue

            record_ai_event(
                "audit_summary",
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
                "audit_summary",
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
        detail="Unable to generate audit summary.",
    )