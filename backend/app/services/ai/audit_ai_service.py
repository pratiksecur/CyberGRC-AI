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


def summarize_audit(
    db: Session,
    audit_id: int,
) -> AuditSummaryResponse:
    """
    Generate an AI executive summary for an audit.
    """

    audit = get_audit_by_id(
        db,
        audit_id,
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found."
        )

    findings = get_findings_for_audit(
        db,
        audit_id,
    )

    if findings:

        findings_text = ""

        actions_text = ""

        for finding in findings:

            findings_text += (
                f"""
Title: {finding.title}
Severity: {finding.severity}
Status: {finding.status}
Recommendation: {finding.recommendation}

"""
            )

            actions = get_corrective_actions_for_finding(
                db,
                finding.id,
            )

            for action in actions:

                actions_text += (
                    f"""
Title: {action.title}
Priority: {action.priority}
Status: {action.status}
Due Date: {action.due_date}

"""
                )

    else:

        findings_text = "No findings."

        actions_text = "No corrective actions."

    prompt = AUDIT_SUMMARY_PROMPT.format(
        audit_name=audit.name,
        audit_scope=audit.scope,
        audit_status=audit.status,
        findings=findings_text,
        actions=actions_text,
    )

    provider = get_ai_provider()

    for attempt in range(2):

        response = provider.generate(prompt)

        try:

            return AuditSummaryResponse(
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