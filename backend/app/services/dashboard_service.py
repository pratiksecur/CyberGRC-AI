from datetime import date

from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.models.control import Control
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.user import User


def get_dashboard_data(db: Session):
    """
    Get executive dashboard statistics using
    live database data.
    """

    # ==================================================
    # RISKS
    # ==================================================

    risks = (
        db.query(Risk)
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

        # Maximum possible risk score is 25
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

    controls = (
        db.query(Control)
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
    # AUDITS
    # ==================================================

    total_audits = (
        db.query(Audit)
        .count()
    )


    # ==================================================
    # AUDIT FINDINGS
    # ==================================================

    findings = (
        db.query(AuditFinding)
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

    actions = (
        db.query(CorrectiveAction)
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
        .filter(
            AuditFinding.severity == "Critical"
        )
        .order_by(
            AuditFinding.created_at.desc()
        )
        .first()
    )

    if critical_finding is not None:

        critical_action = (
            db.query(CorrectiveAction)
            .filter(
                CorrectiveAction.finding_id
                == critical_finding.id
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
    # COMPLIANCE
    # ==================================================

    compliance = round(
        average_effectiveness
    )


    # ==================================================
    # SECURITY HEALTH
    #
    # 50% Risk Health
    # 50% Control Effectiveness
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
    # DASHBOARD RESPONSE
    # ==================================================

    return {

        "totalRisks": total_risks,

        "criticalRisks": critical_risks,

        "controls": total_controls,

        "activeControls": active_controls,

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