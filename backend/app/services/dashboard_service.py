from datetime import date

from sqlalchemy.orm import Session

from app.auth.visibility import get_visible_user_ids
from app.models.risk import Risk
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.user import User


def _visible_ids(
    db: Session,
    current_user: User,
    resource: str,
) -> list[int]:

    return get_visible_user_ids(
        db,
        current_user,
        resource,
    )


def get_dashboard_data(
    db: Session,
    current_user: User,
):
    """
    Get dashboard statistics using only resources that are
    visible to the authenticated user.

    The dashboard intentionally uses the same resource-level
    scope rules as the main GRC API modules.
    """

    # ==================================================
    # RISKS
    # ==================================================

    risk_visible_user_ids = _visible_ids(
        db,
        current_user,
        "risks",
    )

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(risk_visible_user_ids)
        )
        .all()
    )

    total_risks = len(risks)

    critical_risks = sum(
        1
        for risk in risks
        if risk.risk_score > 15
    )

    if total_risks > 0:

        average_risk_score = (
            sum(
                risk.risk_score
                for risk in risks
            )
            / total_risks
        )

        risk_health = (
            100
            - (
                average_risk_score
                / 25
                * 100
            )
        )

    else:

        risk_health = 100

    # ==================================================
    # CONTROLS
    # ==================================================

    control_visible_user_ids = _visible_ids(
        db,
        current_user,
        "controls",
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

    total_controls = len(controls)

    active_controls = sum(
        1
        for control in controls
        if control.status == "Active"
    )

    if total_controls > 0:

        average_effectiveness = (
            sum(
                control.effectiveness
                for control in controls
            )
            / total_controls
        )

    else:

        average_effectiveness = 0

    # ==================================================
    # EVIDENCE
    # ==================================================

    evidence_visible_user_ids = _visible_ids(
        db,
        current_user,
        "evidence",
    )

    total_evidence = (
        db.query(Evidence)
        .filter(
            Evidence.uploaded_by.in_(
                evidence_visible_user_ids
            )
        )
        .count()
    )

    # ==================================================
    # AUDITS
    # ==================================================

    audit_visible_user_ids = _visible_ids(
        db,
        current_user,
        "audits",
    )

    total_audits = (
        db.query(Audit)
        .filter(
            Audit.auditor_id.in_(
                audit_visible_user_ids
            )
        )
        .count()
    )

    # ==================================================
    # AUDIT FINDINGS
    # ==================================================

    finding_visible_user_ids = _visible_ids(
        db,
        current_user,
        "audit_findings",
    )

    findings = (
        db.query(AuditFinding)
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            Audit.auditor_id.in_(
                finding_visible_user_ids
            )
        )
        .all()
    )

    total_findings = len(findings)

    open_findings = sum(
        1
        for finding in findings
        if finding.status == "Open"
    )

    critical_findings = sum(
        1
        for finding in findings
        if finding.severity == "Critical"
    )

    # ==================================================
    # CORRECTIVE ACTIONS
    # ==================================================

    action_visible_user_ids = _visible_ids(
        db,
        current_user,
        "corrective_actions",
    )

    actions = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            Audit.auditor_id.in_(
                action_visible_user_ids
            )
        )
        .all()
    )

    total_actions = len(actions)

    pending_actions = sum(
        1
        for action in actions
        if action.status not in (
            "Completed",
            "Closed",
        )
    )

    today = date.today()

    overdue_actions = sum(
        1
        for action in actions
        if (
            action.status not in (
                "Completed",
                "Closed",
            )
            and action.due_date is not None
            and action.due_date < today
        )
    )

    # ==================================================
    # CRITICAL REMEDIATION
    # ==================================================

    critical_remediation = None

    critical_finding = (
        db.query(AuditFinding)
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            AuditFinding.severity == "Critical",
            Audit.auditor_id.in_(
                finding_visible_user_ids
            ),
        )
        .order_by(
            AuditFinding.created_at.desc()
        )
        .first()
    )

    if critical_finding is not None:

        critical_action = (
            db.query(CorrectiveAction)
            .join(
                AuditFinding,
                CorrectiveAction.finding_id == AuditFinding.id,
            )
            .join(
                Audit,
                AuditFinding.audit_id == Audit.id,
            )
            .filter(
                CorrectiveAction.finding_id
                == critical_finding.id,
                Audit.auditor_id.in_(
                    action_visible_user_ids
                ),
            )
            .order_by(
                CorrectiveAction.created_at.desc()
            )
            .first()
        )

        if critical_action is not None:

            assignee = (
                db.query(User)
                .filter(
                    User.id
                    == critical_action.assigned_to
                )
                .first()
            )

            critical_remediation = {
                "findingId": critical_finding.id,

                "findingTitle": (
                    critical_finding.title
                ),

                "findingSeverity": (
                    critical_finding.severity
                ),

                "actionId": critical_action.id,

                "actionTitle": (
                    critical_action.title
                ),

                "assigneeName": (
                    assignee.full_name
                    if assignee
                    else "Unassigned"
                ),

                "priority": (
                    critical_action.priority
                ),

                "status": (
                    critical_action.status
                ),

                "dueDate": (
                    critical_action.due_date.isoformat()
                    if critical_action.due_date
                    else ""
                ),
            }

    # ==================================================
    # COMPLIANCE / CONTROL EFFECTIVENESS
    # ==================================================

    # This remains the existing control-effectiveness
    # proxy until the GRC Intelligence Engine replaces it
    # with a real framework/evidence-based calculation.

    compliance = round(
        average_effectiveness
    )

    # ==================================================
    # SECURITY HEALTH
    # ==================================================

    security_health = round(
        (
            risk_health
            + average_effectiveness
        )
        / 2
    )

    security_health = max(
        0,
        min(
            100,
            security_health
        )
    )

    # ==================================================
    # RESPONSE
    # ==================================================

    return {

        "totalRisks": total_risks,

        "criticalRisks": critical_risks,

        "controls": total_controls,

        "activeControls": active_controls,

        "totalEvidence": total_evidence,

        "audits": total_audits,

        "compliance": compliance,

        "securityHealth": security_health,

        "totalFindings": total_findings,

        "openFindings": open_findings,

        "criticalFindings": critical_findings,

        "totalActions": total_actions,

        "pendingActions": pending_actions,

        "overdueActions": overdue_actions,

        "criticalRemediation": (
            critical_remediation
        ),
    }