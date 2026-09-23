from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.auth.visibility import get_visible_user_ids

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.risk import Risk
from app.models.risk_treatment import RiskTreatment
from app.models.risk_control import RiskControl
from app.models.user import User

from app.services.risk_treatment_residual_service import (
    select_authoritative_treatment,
)

from app.schemas.monitoring import (
    MonitoringAlert,
    MonitoringMetrics,
    MonitoringOverviewResponse,
    RiskMonitoringResponse,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

CRITICAL_RISK_THRESHOLD = 15

CRITICAL_RISK_NOTIFICATION_THRESHOLD = 20

INEFFECTIVE_CONTROL_THRESHOLD = 50

STALE_EVIDENCE_DAYS = 90

TREATMENT_STUCK_DAYS = 30

TREATMENT_RESIDUAL_THRESHOLD = 15

OPEN_FINDING_STATUSES = {
    "Open",
    "In Progress",
}

COMPLETED_ACTION_STATUSES = {
    "Completed",
    "Closed",
}


# ==========================================================
# TIME
# ==========================================================

def _utc_now() -> datetime:
    """
    Return a timezone-aware UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    )


# ==========================================================
# ALERT FACTORY
# ==========================================================

def _alert(
    alert_type: str,
    severity: str,
    resource_type: str,
    resource_id: int,
    title: str,
    message: str,
    risk_id: int | None = None,
) -> MonitoringAlert:

    return MonitoringAlert(
        alert_type=alert_type,
        severity=severity,
        resource_type=resource_type,
        resource_id=resource_id,
        title=title,
        message=message,
        risk_id=risk_id,
        detected_at=_utc_now(),
    )


# ==========================================================
# RISK -> CONTROL LOOKUP
# ==========================================================

def _get_visible_risk_controls(
    db: Session,
    risk: Risk,
    visible_control_owners: set[int],
):
    """
    Return controls linked to the risk that the current user
    is allowed to see.
    """

    return (
        db.query(Control)
        .join(
            RiskControl,
            RiskControl.control_id
            == Control.id,
        )
        .filter(
            RiskControl.risk_id == risk.id,
            Control.owner_id.in_(
                visible_control_owners
            ),
        )
        .order_by(
            Control.id.asc()
        )
        .all()
    )


# ==========================================================
# RISK TREATMENT MONITORING
# ==========================================================

def _get_visible_risk_treatments(
    db: Session,
    risk: Risk,
    visible_treatment_owners: set[int],
):
    """
    Return treatments for a visible risk whose treatment owners are
    also visible to the current user.

    Treatment visibility is intentionally evaluated independently from
    risk visibility to preserve the Phase 55 object-level authorization
    boundary.
    """

    return (
        db.query(RiskTreatment)
        .filter(
            RiskTreatment.risk_id == risk.id,
            RiskTreatment.owner_id.in_(
                visible_treatment_owners
            ),
        )
        .order_by(
            RiskTreatment.updated_at.desc(),
            RiskTreatment.created_at.desc(),
            RiskTreatment.id.desc(),
        )
        .all()
    )


def _monitor_risk_treatments(
    db: Session,
    risk: Risk,
    visible_treatment_owners: set[int],
) -> list[MonitoringAlert]:
    """
    Evaluate treatment lifecycle state for one visible risk.

    Alerts are deterministic and derived from current database state.
    No treatment data outside the caller's treatment visibility scope is
    included.

    Authoritative treatment selection is delegated to the centralized
    Phase 55 residual-risk service so Monitoring uses the exact same
    treatment semantics as Intelligence and Reports.
    """

    alerts: list[MonitoringAlert] = []

    treatments = _get_visible_risk_treatments(
        db,
        risk,
        visible_treatment_owners,
    )

    if not treatments:
        return alerts

    now = _utc_now()
    today = now.date()

    # ------------------------------------------------------
    # AUTHORITATIVE TREATMENT
    # ------------------------------------------------------

    effective_treatment = select_authoritative_treatment(
        treatments
    )

    # ------------------------------------------------------
    # TREATMENT LIFECYCLE SIGNALS
    # ------------------------------------------------------

    for treatment in treatments:

        if (
            treatment.status not in {
                "Completed",
                "Cancelled",
            }
            and treatment.target_date is not None
            and treatment.target_date < today
        ):
            severity = (
                "CRITICAL"
                if risk.risk_score >= CRITICAL_RISK_NOTIFICATION_THRESHOLD
                else "HIGH"
            )

            alerts.append(
                _alert(
                    alert_type="OVERDUE_RISK_TREATMENT",
                    severity=severity,
                    resource_type="risk_treatment",
                    resource_id=treatment.id,
                    title="Risk Treatment Is Overdue",
                    message=(
                        f"Treatment #{treatment.id} for {risk.title} "
                        f"was due on {treatment.target_date.isoformat()}."
                    ),
                    risk_id=risk.id,
                )
            )

        if treatment.status == "In Progress":
            updated_at = treatment.updated_at

            if updated_at is not None:
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(
                        tzinfo=timezone.utc
                    )

                if updated_at <= now - timedelta(
                    days=TREATMENT_STUCK_DAYS
                ):
                    alerts.append(
                        _alert(
                            alert_type="STUCK_RISK_TREATMENT",
                            severity=(
                                "HIGH"
                                if risk.risk_score > CRITICAL_RISK_THRESHOLD
                                else "MEDIUM"
                            ),
                            resource_type="risk_treatment",
                            resource_id=treatment.id,
                            title="Risk Treatment Has Stalled",
                            message=(
                                f"Treatment #{treatment.id} for {risk.title} "
                                f"has remained In Progress for at least "
                                f"{TREATMENT_STUCK_DAYS} days."
                            ),
                            risk_id=risk.id,
                        )
                    )

        if (
            treatment.status == "Planned"
            and risk.risk_score > CRITICAL_RISK_THRESHOLD
        ):
            alerts.append(
                _alert(
                    alert_type="PLANNED_HIGH_RISK_TREATMENT",
                    severity=(
                        "CRITICAL"
                        if risk.risk_score >= CRITICAL_RISK_NOTIFICATION_THRESHOLD
                        else "HIGH"
                    ),
                    resource_type="risk_treatment",
                    resource_id=treatment.id,
                    title="High-Risk Treatment Is Still Planned",
                    message=(
                        f"Treatment #{treatment.id} for {risk.title} "
                        f"is still Planned while the risk score is "
                        f"{risk.risk_score}."
                    ),
                    risk_id=risk.id,
                )
            )

        if (
            treatment.strategy == "Accept"
            and treatment.acceptance_status == "Pending"
        ):
            alerts.append(
                _alert(
                    alert_type="PENDING_RISK_ACCEPTANCE",
                    severity=(
                        "HIGH"
                        if risk.risk_score > CRITICAL_RISK_THRESHOLD
                        else "MEDIUM"
                    ),
                    resource_type="risk_treatment",
                    resource_id=treatment.id,
                    title="Risk Acceptance Is Pending",
                    message=(
                        f"Treatment #{treatment.id} for {risk.title} "
                        "requires risk-acceptance approval."
                    ),
                    risk_id=risk.id,
                )
            )

        if (
            treatment.strategy == "Accept"
            and treatment.acceptance_status == "Approved"
        ):
            alerts.append(
                _alert(
                    alert_type="APPROVED_RISK_ACCEPTANCE",
                    severity="LOW",
                    resource_type="risk_treatment",
                    resource_id=treatment.id,
                    title="Risk Acceptance Approved",
                    message=(
                        f"Treatment #{treatment.id} for {risk.title} "
                        "has an approved risk acceptance decision."
                    ),
                    risk_id=risk.id,
                )
            )

    # ------------------------------------------------------
    # CANCELLED WITHOUT EFFECTIVE REPLACEMENT
    # ------------------------------------------------------

    has_cancelled_treatment = any(
        treatment.status == "Cancelled"
        for treatment in treatments
    )

    if has_cancelled_treatment and effective_treatment is None:
        alerts.append(
            _alert(
                alert_type="CANCELLED_TREATMENT_WITHOUT_REPLACEMENT",
                severity=(
                    "CRITICAL"
                    if risk.risk_score >= CRITICAL_RISK_NOTIFICATION_THRESHOLD
                    else "HIGH"
                ),
                resource_type="risk",
                resource_id=risk.id,
                title="Cancelled Treatment Has No Effective Replacement",
                message=(
                    f"{risk.title} has cancelled risk treatment activity "
                    "without an effective treatment residual assessment."
                ),
                risk_id=risk.id,
            )
        )

    # ------------------------------------------------------
    # ELEVATED TREATMENT RESIDUAL RISK
    # ------------------------------------------------------

    if effective_treatment is not None:
        residual_score = (
            effective_treatment.residual_risk_score
        )

        if (
            residual_score is not None
            and residual_score > TREATMENT_RESIDUAL_THRESHOLD
        ):
            alerts.append(
                _alert(
                    alert_type="ELEVATED_TREATMENT_RESIDUAL_RISK",
                    severity=(
                        "CRITICAL"
                        if residual_score >= CRITICAL_RISK_NOTIFICATION_THRESHOLD
                        else "HIGH"
                    ),
                    resource_type="risk_treatment",
                    resource_id=effective_treatment.id,
                    title="Treatment Residual Risk Remains Elevated",
                    message=(
                        f"The authoritative treatment for {risk.title} "
                        f"has a residual risk score of {residual_score}."
                    ),
                    risk_id=risk.id,
                )
            )

    return alerts


# ==========================================================
# RISK MONITORING
# ==========================================================

def _monitor_risk(
    db: Session,
    risk: Risk,
    current_user: User,
) -> list[MonitoringAlert]:
    """
    Evaluate one risk and its visible downstream GRC state.
    """

    alerts: list[MonitoringAlert] = []

    # Treatment lifecycle is evaluated within the same risk and treatment
    # visibility boundaries as the API.
    alerts.extend(
        _monitor_risk_treatments(
            db,
            risk,
            set(
                get_visible_user_ids(
                    db,
                    current_user,
                    "risk_treatments",
                )
            ),
        )
    )

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
    # CRITICAL RISK
    # ------------------------------------------------------

    if risk.risk_score > CRITICAL_RISK_THRESHOLD:

        severity = (
            "CRITICAL"
            if risk.risk_score
            >= CRITICAL_RISK_NOTIFICATION_THRESHOLD
            else "HIGH"
        )

        alerts.append(
            _alert(
                alert_type="CRITICAL_RISK",
                severity=severity,
                resource_type="risk",
                resource_id=risk.id,
                title="Critical Risk Detected",
                message=(
                    f"{risk.title} has a risk score "
                    f"of {risk.risk_score}."
                ),
                risk_id=risk.id,
            )
        )

    # ------------------------------------------------------
    # CONTROLS
    # ------------------------------------------------------

    controls = _get_visible_risk_controls(
        db,
        risk,
        visible_controls,
    )

    if not controls:

        alerts.append(
            _alert(
                alert_type="RISK_WITHOUT_CONTROLS",
                severity="HIGH",
                resource_type="risk",
                resource_id=risk.id,
                title="Risk Has No Controls",
                message=(
                    f"{risk.title} does not currently "
                    "have any visible controls mapped to it."
                ),
                risk_id=risk.id,
            )
        )

    # ------------------------------------------------------
    # CONTROL MONITORING
    # ------------------------------------------------------

    for control in controls:

        evidence = (
            db.query(Evidence)
            .filter(
                Evidence.control_id == control.id,
                Evidence.uploaded_by.in_(
                    visible_evidence
                ),
            )
            .order_by(
                Evidence.id.asc()
            )
            .all()
        )

        # ----------------------------------------------
        # CONTROL WITHOUT EVIDENCE
        # ----------------------------------------------

        if not evidence:

            alerts.append(
                _alert(
                    alert_type="CONTROL_WITHOUT_EVIDENCE",
                    severity="HIGH",
                    resource_type="control",
                    resource_id=control.id,
                    title="Control Has No Evidence",
                    message=(
                        f"{control.title} does not have "
                        "visible supporting evidence."
                    ),
                    risk_id=risk.id,
                )
            )

        # ----------------------------------------------
        # INEFFECTIVE CONTROL
        # ----------------------------------------------

        if (
            control.effectiveness
            <= INEFFECTIVE_CONTROL_THRESHOLD
        ):

            alerts.append(
                _alert(
                    alert_type="INEFFECTIVE_CONTROL",
                    severity="HIGH",
                    resource_type="control",
                    resource_id=control.id,
                    title="Control Effectiveness Is Low",
                    message=(
                        f"{control.title} has an effectiveness "
                        f"rating of {control.effectiveness}%."
                    ),
                    risk_id=risk.id,
                )
            )

        # ----------------------------------------------
        # STALE EVIDENCE
        # ----------------------------------------------

        stale_cutoff = (
            _utc_now()
            - timedelta(
                days=STALE_EVIDENCE_DAYS
            )
        )

        for evidence_item in evidence:

            uploaded_at = (
                evidence_item.uploaded_at
            )

            if uploaded_at is None:
                continue

            # Normalize naive DB timestamps.

            if uploaded_at.tzinfo is None:

                uploaded_at = uploaded_at.replace(
                    tzinfo=timezone.utc
                )

            if uploaded_at < stale_cutoff:

                alerts.append(
                    _alert(
                        alert_type="STALE_EVIDENCE",
                        severity="MEDIUM",
                        resource_type="evidence",
                        resource_id=evidence_item.id,
                        title="Evidence Is Stale",
                        message=(
                            f"{evidence_item.title} has not "
                            "been refreshed within the configured "
                            f"{STALE_EVIDENCE_DAYS}-day window."
                        ),
                        risk_id=risk.id,
                    )
                )

        # ----------------------------------------------
        # FINDINGS
        # ----------------------------------------------

        findings = (
            db.query(AuditFinding)
            .join(
                Audit,
                Audit.id
                == AuditFinding.audit_id,
            )
            .filter(
                AuditFinding.control_id
                == control.id,
                Audit.auditor_id.in_(
                    visible_audits
                ),
            )
            .order_by(
                AuditFinding.id.asc()
            )
            .all()
        )

        for finding in findings:

            # ------------------------------------------
            # CRITICAL FINDING
            # ------------------------------------------

            if (
                str(
                    finding.severity
                ).lower()
                == "critical"
            ):

                alerts.append(
                    _alert(
                        alert_type="CRITICAL_FINDING",
                        severity="CRITICAL",
                        resource_type="audit_finding",
                        resource_id=finding.id,
                        title="Critical Audit Finding",
                        message=(
                            f"{finding.title} is a critical "
                            "audit finding."
                        ),
                        risk_id=risk.id,
                    )
                )

            # ------------------------------------------
            # OPEN FINDING
            # ------------------------------------------

            if finding.status in (
                OPEN_FINDING_STATUSES
            ):

                alerts.append(
                    _alert(
                        alert_type="OPEN_FINDING",
                        severity="MEDIUM",
                        resource_type="audit_finding",
                        resource_id=finding.id,
                        title="Open Audit Finding",
                        message=(
                            f"{finding.title} remains "
                            "unresolved."
                        ),
                        risk_id=risk.id,
                    )
                )

            # ------------------------------------------
            # CORRECTIVE ACTIONS
            # ------------------------------------------

            actions = (
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

            for action in actions:

                if (
                    action.status
                    in COMPLETED_ACTION_STATUSES
                ):
                    continue

                # --------------------------------------
                # CRITICAL ACTION
                # --------------------------------------

                if action.priority == "Critical":

                    alerts.append(
                        _alert(
                            alert_type="CRITICAL_ACTION",
                            severity="CRITICAL",
                            resource_type="corrective_action",
                            resource_id=action.id,
                            title="Critical Corrective Action",
                            message=(
                                f"{action.title} is a critical "
                                "remediation action."
                            ),
                            risk_id=risk.id,
                        )
                    )

                # --------------------------------------
                # OVERDUE ACTION
                # --------------------------------------

                if (
                    action.due_date is not None
                    and action.due_date
                    < datetime.now().date()
                ):

                    alerts.append(
                        _alert(
                            alert_type="OVERDUE_ACTION",
                            severity="HIGH",
                            resource_type="corrective_action",
                            resource_id=action.id,
                            title="Corrective Action Overdue",
                            message=(
                                f"{action.title} was due on "
                                f"{action.due_date.isoformat()}."
                            ),
                            risk_id=risk.id,
                        )
                    )

    return alerts


# ==========================================================
# SINGLE RISK MONITORING
# ==========================================================

def get_risk_monitoring(
    db: Session,
    risk_id: int,
    current_user: User,
) -> RiskMonitoringResponse | None:

    visible_risks = set(
        get_visible_user_ids(
            db,
            current_user,
            "risks",
        )
    )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(
                visible_risks
            ),
        )
        .first()
    )

    if risk is None:
        return None

    alerts = _monitor_risk(
        db,
        risk,
        current_user,
    )

    return RiskMonitoringResponse(
        generated_at=_utc_now(),
        risk_id=risk.id,
        risk_score=risk.risk_score,
        alerts=alerts,
    )


# ==========================================================
# MONITORING OVERVIEW
# ==========================================================

def get_monitoring_overview(
    db: Session,
    current_user: User,
) -> MonitoringOverviewResponse:

    visible_risks = set(
        get_visible_user_ids(
            db,
            current_user,
            "risks",
        )
    )

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(
                visible_risks
            )
        )
        .order_by(
            Risk.risk_score.desc(),
            Risk.id.asc(),
        )
        .all()
    )

    alerts: list[MonitoringAlert] = []

    for risk in risks:

        alerts.extend(
            _monitor_risk(
                db,
                risk,
                current_user,
            )
        )

    # ======================================================
    # METRICS
    # ======================================================

    critical_alerts = sum(
        1
        for alert in alerts
        if alert.severity == "CRITICAL"
    )

    high_alerts = sum(
        1
        for alert in alerts
        if alert.severity == "HIGH"
    )

    medium_alerts = sum(
        1
        for alert in alerts
        if alert.severity == "MEDIUM"
    )

    low_alerts = sum(
        1
        for alert in alerts
        if alert.severity == "LOW"
    )

    critical_risks = sum(
        1
        for risk in risks
        if risk.risk_score
        > CRITICAL_RISK_THRESHOLD
    )

    risks_without_controls = sum(
        1
        for risk in risks
        if not _get_visible_risk_controls(
            db,
            risk,
            set(
                get_visible_user_ids(
                    db,
                    current_user,
                    "controls",
                )
            ),
        )
    )

    # ------------------------------------------------------
    # CONTROL-LEVEL METRICS
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

    controls = (
        db.query(Control)
        .filter(
            Control.owner_id.in_(
                visible_controls
            )
        )
        .all()
    )

    controls_without_evidence = 0

    ineffective_controls = 0

    for control in controls:

        evidence_exists = (
            db.query(Evidence.id)
            .filter(
                Evidence.control_id
                == control.id,
                Evidence.uploaded_by.in_(
                    visible_evidence
                ),
            )
            .first()
            is not None
        )

        if not evidence_exists:

            controls_without_evidence += 1

        if (
            control.effectiveness
            <= INEFFECTIVE_CONTROL_THRESHOLD
        ):

            ineffective_controls += 1

    # ------------------------------------------------------
    # FINDINGS
    # ------------------------------------------------------

    critical_findings = sum(
        1
        for alert in alerts
        if alert.alert_type
        == "CRITICAL_FINDING"
    )

    open_findings = sum(
        1
        for alert in alerts
        if alert.alert_type
        == "OPEN_FINDING"
    )

    # ------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------

    overdue_actions = sum(
        1
        for alert in alerts
        if alert.alert_type
        == "OVERDUE_ACTION"
    )

    critical_actions = sum(
        1
        for alert in alerts
        if alert.alert_type
        == "CRITICAL_ACTION"
    )

    # ------------------------------------------------------
    # STALE EVIDENCE
    # ------------------------------------------------------

    stale_evidence = sum(
        1
        for alert in alerts
        if alert.alert_type
        == "STALE_EVIDENCE"
    )

    treatment_alerts = sum(
        1
        for alert in alerts
        if alert.resource_type == "risk_treatment"
        or alert.alert_type
        in {
            "CANCELLED_TREATMENT_WITHOUT_REPLACEMENT",
        }
    )

    overdue_treatments = sum(
        1
        for alert in alerts
        if alert.alert_type == "OVERDUE_RISK_TREATMENT"
    )

    stuck_treatments = sum(
        1
        for alert in alerts
        if alert.alert_type == "STUCK_RISK_TREATMENT"
    )

    planned_high_risk_treatments = sum(
        1
        for alert in alerts
        if alert.alert_type == "PLANNED_HIGH_RISK_TREATMENT"
    )

    pending_acceptances = sum(
        1
        for alert in alerts
        if alert.alert_type == "PENDING_RISK_ACCEPTANCE"
    )

    elevated_residual_risks = sum(
        1
        for alert in alerts
        if alert.alert_type == "ELEVATED_TREATMENT_RESIDUAL_RISK"
    )

    cancelled_without_replacement = sum(
        1
        for alert in alerts
        if alert.alert_type == "CANCELLED_TREATMENT_WITHOUT_REPLACEMENT"
    )

    approved_acceptances = sum(
        1
        for alert in alerts
        if alert.alert_type == "APPROVED_RISK_ACCEPTANCE"
    )

    # ------------------------------------------------------
    # SORT ALERTS
    # ------------------------------------------------------

    severity_order = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    alerts.sort(
        key=lambda item: (
            severity_order.get(
                item.severity,
                99,
            ),
            item.resource_type,
            item.resource_id,
        )
    )

    metrics = MonitoringMetrics(
        total_alerts=len(alerts),

        critical_alerts=critical_alerts,

        high_alerts=high_alerts,

        medium_alerts=medium_alerts,

        low_alerts=low_alerts,

        critical_risks=critical_risks,

        risks_without_controls=(
            risks_without_controls
        ),

        controls_without_evidence=(
            controls_without_evidence
        ),

        ineffective_controls=(
            ineffective_controls
        ),

        critical_findings=critical_findings,

        open_findings=open_findings,

        overdue_actions=overdue_actions,

        critical_actions=critical_actions,

        stale_evidence=stale_evidence,

        treatment_alerts=treatment_alerts,
        overdue_treatments=overdue_treatments,
        stuck_treatments=stuck_treatments,
        planned_high_risk_treatments=planned_high_risk_treatments,
        pending_acceptances=pending_acceptances,
        elevated_residual_risks=elevated_residual_risks,
        cancelled_without_replacement=cancelled_without_replacement,
        approved_acceptances=approved_acceptances,
    )

    return MonitoringOverviewResponse(
        generated_at=_utc_now(),
        metrics=metrics,
        alerts=alerts,
    )