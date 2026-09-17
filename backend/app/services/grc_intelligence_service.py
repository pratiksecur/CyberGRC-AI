from datetime import date

from sqlalchemy.orm import Session

from app.auth.visibility import get_visible_user_ids

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.control_framework_control import ControlFrameworkControl
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.user import User

from app.schemas.intelligence import (
    GRCIntelligenceOverviewMetrics,
    GRCIntelligenceOverviewResponse,
    IntelligenceAction,
    IntelligenceControl,
    IntelligenceEvidence,
    IntelligenceFinding,
    IntelligenceFramework,
    RiskIntelligenceMetrics,
    RiskIntelligenceResponse,
)


# ==========================================================
# CONSTANTS
# ==========================================================

COMPLETED_ACTION_STATUSES = {
    "Completed",
    "Closed",
}

OPEN_FINDING_STATUSES = {
    "Open",
    "In Progress",
}

# Keep this consistent with the existing dashboard
# critical-risk threshold.
CRITICAL_RISK_THRESHOLD = 15


# ==========================================================
# HELPERS
# ==========================================================

def _percent(
    numerator: int,
    denominator: int,
) -> float:

    if denominator <= 0:
        return 0.0

    return round(
        (numerator / denominator) * 100,
        2,
    )


def _action_is_overdue(
    action: CorrectiveAction,
    today: date,
) -> bool:

    return (
        action.due_date is not None
        and action.due_date < today
        and action.status not in COMPLETED_ACTION_STATUSES
    )


# ==========================================================
# BUILD RISK INTELLIGENCE
# ==========================================================

def _build_risk_intelligence(
    db: Session,
    risk: Risk,
    current_user: User,
) -> RiskIntelligenceResponse:
    """
    Build a scope-aware GRC intelligence graph for one risk.

    Every downstream resource uses its own visibility scope.
    This prevents the intelligence layer from becoming an
    authorization bypass.
    """

    # ------------------------------------------------------
    # RESOURCE-SPECIFIC VISIBILITY
    # ------------------------------------------------------

    visible_controls = set(
        get_visible_user_ids(
            db,
            current_user,
            "controls",
        )
    )

    visible_evidence = set(
        get_visible_user_ids(
            db,
            current_user,
            "evidence",
        )
    )

    visible_audits = set(
        get_visible_user_ids(
            db,
            current_user,
            "audits",
        )
    )

    visible_actions = set(
        get_visible_user_ids(
            db,
            current_user,
            "corrective_actions",
        )
    )

    # ------------------------------------------------------
    # RISK -> CONTROL
    # ------------------------------------------------------

    mappings = (
        db.query(RiskControl)
        .join(
            Control,
            Control.id == RiskControl.control_id,
        )
        .filter(
            RiskControl.risk_id == risk.id,
            Control.owner_id.in_(visible_controls),
        )
        .order_by(
            RiskControl.control_id.asc()
        )
        .all()
    )

    controls: list[IntelligenceControl] = []

    effectiveness_values: list[int] = []

    framework_ids: set[int] = set()

    findings: list[IntelligenceFinding] = []
    actions: list[IntelligenceAction] = []

    today = date.today()

    # ------------------------------------------------------
    # WALK EACH CONTROL
    # ------------------------------------------------------

    for mapping in mappings:

        control = mapping.control

        # ==================================================
        # CONTROL -> EVIDENCE
        # ==================================================

        evidence_rows = (
            db.query(Evidence)
            .filter(
                Evidence.control_id == control.id,
                Evidence.uploaded_by.in_(visible_evidence),
            )
            .order_by(
                Evidence.id.asc()
            )
            .all()
        )

        evidence_items = [
            IntelligenceEvidence(
                id=evidence.id,
                control_id=evidence.control_id,
                title=evidence.title,
                file_name=evidence.file_name,
            )
            for evidence in evidence_rows
        ]

        # ==================================================
        # EFFECTIVENESS
        # ==================================================

        effectiveness_values.append(
            int(control.effectiveness or 0)
        )

        # ==================================================
        # CONTROL -> FRAMEWORK
        # ==================================================

        framework_rows = (
            db.query(
                Framework,
                FrameworkControl.control_code,
            )
            .join(
                FrameworkControl,
                FrameworkControl.framework_id
                == Framework.id,
            )
            .join(
                ControlFrameworkControl,
                ControlFrameworkControl.framework_control_id
                == FrameworkControl.id,
            )
            .filter(
                ControlFrameworkControl.control_id
                == control.id,
            )
            .order_by(
                Framework.id.asc(),
                FrameworkControl.id.asc(),
            )
            .all()
        )

        framework_items = []

        seen_framework_mapping: set[
            tuple[int, str]
        ] = set()

        for framework, control_code in framework_rows:

            key = (
                framework.id,
                control_code,
            )

            if key in seen_framework_mapping:
                continue

            seen_framework_mapping.add(key)

            framework_ids.add(
                framework.id
            )

            framework_items.append(
                IntelligenceFramework(
                    id=framework.id,
                    name=framework.name,
                    version=framework.version,
                    control_code=control_code,
                )
            )

        # ==================================================
        # CONTROL -> AUDIT FINDINGS
        # ==================================================

        finding_rows = (
            db.query(AuditFinding)
            .join(
                Audit,
                Audit.id == AuditFinding.audit_id,
            )
            .filter(
                AuditFinding.control_id == control.id,
                Audit.auditor_id.in_(visible_audits),
            )
            .order_by(
                AuditFinding.id.asc()
            )
            .all()
        )

        control_findings: list[
            IntelligenceFinding
        ] = []

        # --------------------------------------------------
        # FINDINGS -> CORRECTIVE ACTIONS
        # --------------------------------------------------

        for finding in finding_rows:

            action_rows = (
                db.query(CorrectiveAction)
                .filter(
                    CorrectiveAction.finding_id
                    == finding.id,
                    CorrectiveAction.assigned_to.in_(
                        visible_actions
                    ),
                )
                .order_by(
                    CorrectiveAction.id.asc()
                )
                .all()
            )

            action_items = [
                IntelligenceAction(
                    id=action.id,
                    finding_id=action.finding_id,
                    title=action.title,
                    priority=action.priority,
                    status=action.status,
                    assigned_to=action.assigned_to,
                    due_date=action.due_date,
                    overdue=_action_is_overdue(
                        action,
                        today,
                    ),
                )
                for action in action_rows
            ]

            actions.extend(
                action_items
            )

            finding_item = IntelligenceFinding(
                id=finding.id,
                audit_id=finding.audit_id,
                control_id=finding.control_id,
                title=finding.title,
                severity=finding.severity,
                status=finding.status,
                actions=action_items,
            )

            control_findings.append(
                finding_item
            )

            findings.append(
                finding_item
            )

        # ==================================================
        # FINAL CONTROL INTELLIGENCE
        # ==================================================

        controls.append(
            IntelligenceControl(
                id=control.id,
                title=control.title,
                status=control.status,
                effectiveness=int(
                    control.effectiveness or 0
                ),
                evidence=evidence_items,
                frameworks=framework_items,
                findings=control_findings,
            )
        )

    # ======================================================
    # AGGREGATE METRICS
    # ======================================================

    control_count = len(controls)

    finding_count = len(findings)

    action_count = len(actions)

    controls_with_evidence = sum(
        1
        for control in controls
        if len(control.evidence) > 0
    )

    open_findings = sum(
        1
        for finding in findings
        if finding.status
        in OPEN_FINDING_STATUSES
    )

    critical_findings = sum(
        1
        for finding in findings
        if str(
            finding.severity
        ).lower() == "critical"
    )

    open_actions = sum(
        1
        for action in actions
        if action.status
        not in COMPLETED_ACTION_STATUSES
    )

    overdue_actions = sum(
        1
        for action in actions
        if action.overdue
    )

    completed_actions = (
        action_count
        - open_actions
    )

    # ======================================================
    # CONTROL EFFECTIVENESS
    # ======================================================

    if effectiveness_values:

        average_effectiveness = round(
            sum(effectiveness_values)
            / len(effectiveness_values),
            2,
        )

    else:

        average_effectiveness = 0.0

    # ======================================================
    # ESTIMATED RESIDUAL RISK
    # ======================================================

    # The current Risk model does not have a persisted
    # residual-risk field.
    #
    # Therefore this is an explicitly derived estimate:
    #
    #     risk score × (1 - control effectiveness / 100)
    #
    # It must NOT be interpreted as a stored risk value.

    if control_count:

        estimated_residual_risk = round(
            float(risk.risk_score)
            * (
                1
                - (
                    average_effectiveness
                    / 100
                )
            ),
            2,
        )

    else:

        estimated_residual_risk = float(
            risk.risk_score
        )

    # ======================================================
    # METRICS RESPONSE
    # ======================================================

    metrics = RiskIntelligenceMetrics(

        control_count=control_count,

        controls_with_evidence=(
            controls_with_evidence
        ),

        evidence_coverage_percent=_percent(
            controls_with_evidence,
            control_count,
        ),

        average_control_effectiveness=(
            average_effectiveness
        ),

        framework_count=len(
            framework_ids
        ),

        finding_count=finding_count,

        open_findings=open_findings,

        critical_findings=critical_findings,

        action_count=action_count,

        open_actions=open_actions,

        overdue_actions=overdue_actions,

        remediation_completion_percent=_percent(
            completed_actions,
            action_count,
        ),

        estimated_residual_risk=(
            estimated_residual_risk
        ),
    )

    # ======================================================
    # FINAL RESPONSE
    # ======================================================

    return RiskIntelligenceResponse(

        risk_id=risk.id,

        risk_title=risk.title,

        risk_score=risk.risk_score,

        risk_status=risk.status,

        owner_id=risk.owner_id,

        metrics=metrics,

        controls=controls,
    )


# ==========================================================
# SINGLE RISK INTELLIGENCE
# ==========================================================

def get_risk_intelligence(
    db: Session,
    risk_id: int,
    current_user: User,
) -> RiskIntelligenceResponse | None:

    visible_risk_owners = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(
                visible_risk_owners
            ),
        )
        .first()
    )

    if risk is None:
        return None

    return _build_risk_intelligence(
        db,
        risk,
        current_user,
    )


# ==========================================================
# GRC INTELLIGENCE OVERVIEW
# ==========================================================

def get_grc_intelligence_overview(
    db: Session,
    current_user: User,
) -> GRCIntelligenceOverviewResponse:

    visible_risk_owners = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(
                visible_risk_owners
            )
        )
        .order_by(
            Risk.risk_score.desc(),
            Risk.id.asc(),
        )
        .all()
    )

    risk_intelligence = [
        _build_risk_intelligence(
            db,
            risk,
            current_user,
        )
        for risk in risks
    ]

    # ======================================================
    # FINDINGS
    # ======================================================

    total_findings = sum(
        item.metrics.finding_count
        for item in risk_intelligence
    )

    open_findings = sum(
        item.metrics.open_findings
        for item in risk_intelligence
    )

    critical_findings = sum(
        item.metrics.critical_findings
        for item in risk_intelligence
    )

    # ======================================================
    # ACTIONS
    # ======================================================

    total_actions = sum(
        item.metrics.action_count
        for item in risk_intelligence
    )

    open_actions = sum(
        item.metrics.open_actions
        for item in risk_intelligence
    )

    overdue_actions = sum(
        item.metrics.overdue_actions
        for item in risk_intelligence
    )

    completed_actions = (
        total_actions
        - open_actions
    )

    # ======================================================
    # OVERVIEW METRICS
    # ======================================================

    metrics = GRCIntelligenceOverviewMetrics(

        total_risks=len(risks),

        critical_risks=sum(
            1
            for risk in risks
            if risk.risk_score
            > CRITICAL_RISK_THRESHOLD
        ),

        risks_with_controls=sum(
            1
            for item in risk_intelligence
            if item.metrics.control_count > 0
        ),

        risks_with_evidence=sum(
            1
            for item in risk_intelligence
            if (
                item.metrics
                .controls_with_evidence
                > 0
            )
        ),

        total_findings=total_findings,

        open_findings=open_findings,

        critical_findings=critical_findings,

        total_actions=total_actions,

        open_actions=open_actions,

        overdue_actions=overdue_actions,

        remediation_completion_percent=_percent(
            completed_actions,
            total_actions,
        ),
    )

    return GRCIntelligenceOverviewResponse(
        metrics=metrics,
        risks=risk_intelligence,
    )