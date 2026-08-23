import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.provider_factory import get_ai_provider
from app.ai.prompts import AUDIT_SUMMARY_PROMPT

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


def summarize_audit(
    db: Session,
    audit_id: int,
) -> AuditSummaryResponse:
    """
    Generate an AI executive summary for an audit.

    Database-derived metrics are calculated independently
    and are never trusted to the AI model.

    AI is responsible only for:
    - Overall assessment
    - Executive summary
    - Priority recommendations
    """

    # ==========================================================
    # FETCH AUDIT
    # ==========================================================

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

    # ==========================================================
    # BUILD AI CONTEXT
    # ==========================================================

    if findings:

        findings_text = ""

        actions_text = ""

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
                == "open"
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

                if normalized_status in (
                    "completed",
                    "closed",
                ):
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

    else:

        findings_text = "No findings."

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
        actions=(
            actions_text
            if actions_text
            else "No corrective actions."
        ),
    )

    # ==========================================================
    # AI PROVIDER
    # ==========================================================

    try:

        provider = get_ai_provider()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"AI provider initialization failed: {str(e)}"
            ),
        )

    # ==========================================================
    # GENERATE AI RESPONSE
    # ==========================================================

    for attempt in range(2):

        try:

            response = provider.generate(
                prompt
            )

            cleaned_response = response.strip()

            # --------------------------------------------------
            # Remove markdown JSON fences if AI adds them
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

            # --------------------------------------------------
            # Parse JSON
            # --------------------------------------------------

            response_json = json.loads(
                cleaned_response
            )

            # ==================================================
            # IMPORTANT
            #
            # Override all numerical metrics with values
            # calculated directly from the database.
            #
            # The AI cannot alter these values.
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

            # --------------------------------------------------
            # Validate final response
            # --------------------------------------------------

            return AuditSummaryResponse(
                **response_json
            )

        except (
            json.JSONDecodeError,
            ValidationError,
        ):

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
                    f"AI audit summary failed: {str(e)}"
                ),
            )

    raise HTTPException(
        status_code=500,
        detail="Unable to generate audit summary.",
    )