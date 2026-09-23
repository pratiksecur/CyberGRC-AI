from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_treatment import RiskTreatment
from app.models.user import User

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding

from app.models.framework import Framework
from app.models.framework_control import FrameworkControl

from app.models.control import Control
from app.models.evidence import Evidence

from app.models.control_framework_control import (
    ControlFrameworkControl,
)

from app.services.risk_treatment_residual_service import (
    select_authoritative_treatment,
    treatment_authority_rank,
    has_residual_assessment,
)


def _risk_treatment_context(
    db: Session,
    risk: Risk,
    visible_user_ids: list[int],
):
    """
    Calculate report treatment metrics using the canonical treatment
    lifecycle semantics shared with GRC Intelligence and Monitoring.

    Treatment visibility is constrained by the already-resolved report
    visibility set for treatment owners.
    """

    treatments = (
        db.query(RiskTreatment)
        .filter(
            RiskTreatment.risk_id == risk.id,
            RiskTreatment.owner_id.in_(visible_user_ids),
        )
        .order_by(
            RiskTreatment.updated_at.desc(),
            RiskTreatment.created_at.desc(),
            RiskTreatment.id.desc(),
        )
        .all()
    )

    effective_treatments = [
        treatment
        for treatment in treatments
        if (
            treatment_authority_rank(treatment) < 99
            and has_residual_assessment(treatment)
        )
    ]

    selected = select_authoritative_treatment(
        treatments
    )

    controls = (
        db.query(Control)
        .join(
            RiskControl,
            RiskControl.control_id == Control.id,
        )
        .filter(
            RiskControl.risk_id == risk.id,
            Control.owner_id.in_(visible_user_ids),
        )
        .all()
    )

    if controls:
        average_effectiveness = sum(
            control.effectiveness
            for control in controls
        ) / len(controls)

        control_estimated_residual_risk = round(
            risk.risk_score
            * (1 - average_effectiveness / 100),
            2,
        )
    else:
        control_estimated_residual_risk = float(
            risk.risk_score
        )

    treatment_residual_risk = (
        selected.residual_risk_score
        if selected is not None
        else None
    )

    treatment_aware_residual_risk = (
        float(treatment_residual_risk)
        if treatment_residual_risk is not None
        else float(control_estimated_residual_risk)
    )

    return {
        "treatment_count": len(treatments),
        "effective_treatment_count": len(
            effective_treatments
        ),
        "treatment_residual_risk": (
            treatment_residual_risk
        ),
        "treatment_aware_residual_risk": (
            treatment_aware_residual_risk
        ),
        "selected_treatment_id": (
            selected.id
            if selected is not None
            else None
        ),
        "selected_treatment_strategy": (
            selected.strategy
            if selected is not None
            else None
        ),
        "selected_treatment_status": (
            selected.status
            if selected is not None
            else None
        ),
        "selected_treatment_acceptance_status": (
            selected.acceptance_status
            if selected is not None
            else None
        ),
        "control_estimated_residual_risk": (
            control_estimated_residual_risk
        ),
    }


def get_risk_report(
    db: Session,
    visible_user_ids: list[int],
):
    """
    Generate a live risk report limited to
    risks within the authenticated user's scope.

    Treatment-aware residual-risk values use the canonical
    Phase 55.7 treatment-selection semantics.
    """

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(visible_user_ids)
        )
        .all()
    )

    total_risks = len(risks)

    critical_risks = sum(
        1
        for risk in risks
        if risk.risk_score > 15
    )

    high_risks = sum(
        1
        for risk in risks
        if 10 <= risk.risk_score <= 15
    )

    medium_risks = sum(
        1
        for risk in risks
        if 5 <= risk.risk_score < 10
    )

    low_risks = sum(
        1
        for risk in risks
        if risk.risk_score < 5
    )

    open_risks = sum(
        1
        for risk in risks
        if risk.status == "Open"
    )

    closed_risks = sum(
        1
        for risk in risks
        if risk.status == "Closed"
    )

    if total_risks > 0:
        average_risk_score = round(
            sum(
                risk.risk_score
                for risk in risks
            )
            / total_risks,
            2,
        )
    else:
        average_risk_score = 0.0

    risk_items = []

    treatment_aware_scores = []
    total_treatments = 0
    risks_with_effective_treatment = 0
    pending_acceptances = 0
    approved_acceptances = 0

    for risk in risks:
        treatment_context = _risk_treatment_context(
            db,
            risk,
            visible_user_ids,
        )

        total_treatments += (
            treatment_context["treatment_count"]
        )

        if (
            treatment_context[
                "effective_treatment_count"
            ]
            > 0
        ):
            risks_with_effective_treatment += 1

        treatment_aware_scores.append(
            treatment_context[
                "treatment_aware_residual_risk"
            ]
        )

        pending_acceptances += sum(
            1
            for treatment in (
                db.query(RiskTreatment)
                .filter(
                    RiskTreatment.risk_id == risk.id,
                    RiskTreatment.owner_id.in_(
                        visible_user_ids
                    ),
                    RiskTreatment.strategy == "Accept",
                    RiskTreatment.acceptance_status
                    == "Pending",
                )
                .all()
            )
        )

        approved_acceptances += sum(
            1
            for treatment in (
                db.query(RiskTreatment)
                .filter(
                    RiskTreatment.risk_id == risk.id,
                    RiskTreatment.owner_id.in_(
                        visible_user_ids
                    ),
                    RiskTreatment.strategy == "Accept",
                    RiskTreatment.acceptance_status
                    == "Approved",
                )
                .all()
            )
        )

        owner = (
            db.query(User)
            .filter(
                User.id == risk.owner_id
            )
            .first()
        )

        risk_items.append(
            {
                "id": risk.id,
                "title": risk.title,
                "description": risk.description,
                "likelihood": risk.likelihood,
                "impact": risk.impact,
                "risk_score": risk.risk_score,
                "status": risk.status,

                "treatment_count": (
                    treatment_context[
                        "treatment_count"
                    ]
                ),
                "effective_treatment_count": (
                    treatment_context[
                        "effective_treatment_count"
                    ]
                ),
                "treatment_residual_risk": (
                    treatment_context[
                        "treatment_residual_risk"
                    ]
                ),
                "treatment_aware_residual_risk": (
                    treatment_context[
                        "treatment_aware_residual_risk"
                    ]
                ),
                "control_estimated_residual_risk": (
                    treatment_context[
                        "control_estimated_residual_risk"
                    ]
                ),
                "selected_treatment_id": (
                    treatment_context[
                        "selected_treatment_id"
                    ]
                ),
                "selected_treatment_strategy": (
                    treatment_context[
                        "selected_treatment_strategy"
                    ]
                ),
                "selected_treatment_status": (
                    treatment_context[
                        "selected_treatment_status"
                    ]
                ),
                "selected_treatment_acceptance_status": (
                    treatment_context[
                        "selected_treatment_acceptance_status"
                    ]
                ),
                "owner_id": risk.owner_id,
                "owner_name": (
                    owner.full_name
                    if owner
                    else "Unknown"
                ),
                "created_at": (
                    risk.created_at.isoformat()
                    if risk.created_at
                    else ""
                ),
            }
        )

    risk_items.sort(
        key=lambda risk: risk["risk_score"],
        reverse=True,
    )

    return {
        "summary": {
            "total_risks": total_risks,
            "critical_risks": critical_risks,
            "high_risks": high_risks,
            "medium_risks": medium_risks,
            "low_risks": low_risks,
            "open_risks": open_risks,
            "closed_risks": closed_risks,
            "average_risk_score": average_risk_score,
            "average_treatment_aware_residual_risk": (
                round(
                    sum(treatment_aware_scores)
                    / len(treatment_aware_scores),
                    2,
                )
                if treatment_aware_scores
                else 0.0
            ),
            "total_treatments": total_treatments,
            "risks_with_effective_treatment": (
                risks_with_effective_treatment
            ),
            "pending_acceptances": pending_acceptances,
            "approved_acceptances": approved_acceptances,
        },
        "risks": risk_items,
    }


def get_audit_report(
    db: Session,
    visible_user_ids: list[int],
):
    """
    Generate a live audit and findings report
    limited to audits within the authenticated
    user's visibility scope.
    """

    audits = (
        db.query(Audit)
        .filter(
            Audit.auditor_id.in_(visible_user_ids)
        )
        .all()
    )

    audit_ids = {
        audit.id
        for audit in audits
    }

    findings = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.audit_id.in_(audit_ids)
        )
        .all()
    ) if audit_ids else []

    total_audits = len(audits)

    planned_audits = sum(
        1
        for audit in audits
        if audit.status == "Planned"
    )

    in_progress_audits = sum(
        1
        for audit in audits
        if audit.status == "In Progress"
    )

    completed_audits = sum(
        1
        for audit in audits
        if audit.status == "Completed"
    )

    total_findings = len(findings)

    critical_findings = sum(
        1
        for finding in findings
        if finding.severity == "Critical"
    )

    high_findings = sum(
        1
        for finding in findings
        if finding.severity == "High"
    )

    medium_findings = sum(
        1
        for finding in findings
        if finding.severity == "Medium"
    )

    low_findings = sum(
        1
        for finding in findings
        if finding.severity == "Low"
    )

    open_findings = sum(
        1
        for finding in findings
        if finding.status == "Open"
    )

    closed_findings = sum(
        1
        for finding in findings
        if finding.status == "Closed"
    )

    audit_items = []

    for audit in audits:

        framework = (
            db.query(Framework)
            .filter(
                Framework.id == audit.framework_id
            )
            .first()
        )

        auditor = (
            db.query(User)
            .filter(
                User.id == audit.auditor_id
            )
            .first()
        )

        audit_findings = [
            finding
            for finding in findings
            if finding.audit_id == audit.id
        ]

        finding_count = len(
            audit_findings
        )

        critical_finding_count = sum(
            1
            for finding in audit_findings
            if finding.severity == "Critical"
        )

        open_finding_count = sum(
            1
            for finding in audit_findings
            if finding.status == "Open"
        )

        audit_items.append(
            {
                "id": audit.id,
                "name": audit.name,
                "framework_id": audit.framework_id,
                "framework_name": (
                    framework.name
                    if framework
                    else "Unknown"
                ),
                "auditor_id": audit.auditor_id,
                "auditor_name": (
                    auditor.full_name
                    if auditor
                    else "Unknown"
                ),
                "scope": audit.scope,
                "status": audit.status,
                "start_date": (
                    audit.start_date.isoformat()
                    if audit.start_date
                    else ""
                ),
                "end_date": (
                    audit.end_date.isoformat()
                    if audit.end_date
                    else ""
                ),
                "finding_count": finding_count,
                "critical_finding_count": (
                    critical_finding_count
                ),
                "open_finding_count": (
                    open_finding_count
                ),
                "created_at": (
                    audit.created_at.isoformat()
                    if audit.created_at
                    else ""
                ),
            }
        )

    audit_items.sort(
        key=lambda audit: audit["created_at"],
        reverse=True,
    )

    return {
        "summary": {
            "total_audits": total_audits,
            "planned_audits": planned_audits,
            "in_progress_audits": in_progress_audits,
            "completed_audits": completed_audits,
            "total_findings": total_findings,
            "critical_findings": critical_findings,
            "high_findings": high_findings,
            "medium_findings": medium_findings,
            "low_findings": low_findings,
            "open_findings": open_findings,
            "closed_findings": closed_findings,
        },
        "audits": audit_items,
    }


def get_compliance_report(
    db: Session,
    visible_user_ids: list[int],
):
    """
    Generate a live compliance report limited to
    controls and related data within the user's scope.

    Frameworks themselves remain visible because
    framework viewing is organization-level.
    """

    frameworks = (
        db.query(Framework)
        .all()
    )

    controls = (
        db.query(Control)
        .filter(
            Control.owner_id.in_(visible_user_ids)
        )
        .all()
    )

    control_ids = {
        control.id
        for control in controls
    }

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.control_id.in_(control_ids)
        )
        .all()
    ) if control_ids else []

    audits = (
        db.query(Audit)
        .filter(
            Audit.auditor_id.in_(visible_user_ids)
        )
        .all()
    )

    audit_ids = {
        audit.id
        for audit in audits
    }

    findings = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.audit_id.in_(audit_ids)
        )
        .filter(
            AuditFinding.control_id.in_(control_ids)
        )
        .all()
    ) if audit_ids and control_ids else []

    mappings = (
        db.query(ControlFrameworkControl)
        .all()
    )

    total_frameworks = len(
        frameworks
    )

    total_controls = len(
        controls
    )

    active_controls = sum(
        1
        for control in controls
        if control.status == "Active"
    )

    if total_controls > 0:
        average_control_effectiveness = round(
            sum(
                control.effectiveness
                for control in controls
            )
            / total_controls,
            2,
        )
    else:
        average_control_effectiveness = 0.0

    total_evidence = len(
        evidence
    )

    total_findings = len(
        findings
    )

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

    framework_items = []

    for framework in frameworks:

        framework_control_ids = {
            framework_control.id
            for framework_control in (
                db.query(FrameworkControl)
                .filter(
                    FrameworkControl.framework_id
                    == framework.id
                )
                .all()
            )
        }

        framework_control_mappings = [
            mapping
            for mapping in mappings
            if mapping.framework_control_id
            in framework_control_ids
        ]

        framework_control_ids_set = {
            mapping.control_id
            for mapping
            in framework_control_mappings
        }

        framework_controls = [
            control
            for control in controls
            if control.id
            in framework_control_ids_set
        ]

        control_count = len(
            framework_controls
        )

        active_control_count = sum(
            1
            for control
            in framework_controls
            if control.status == "Active"
        )

        if control_count > 0:
            average_effectiveness = round(
                sum(
                    control.effectiveness
                    for control
                    in framework_controls
                )
                / control_count,
                2,
            )
        else:
            average_effectiveness = 0.0

        visible_framework_control_ids = {
            control.id
            for control in framework_controls
        }

        framework_evidence = [
            item
            for item in evidence
            if item.control_id
            in visible_framework_control_ids
        ]

        evidence_count = len(
            framework_evidence
        )

        framework_findings = [
            finding
            for finding in findings
            if finding.control_id
            in visible_framework_control_ids
        ]

        finding_count = len(
            framework_findings
        )

        critical_finding_count = sum(
            1
            for finding in framework_findings
            if finding.severity == "Critical"
        )

        open_finding_count = sum(
            1
            for finding in framework_findings
            if finding.status == "Open"
        )

        framework_items.append(
            {
                "id": framework.id,
                "name": framework.name,
                "version": framework.version,
                "control_count": control_count,
                "active_control_count": active_control_count,
                "average_effectiveness": (
                    average_effectiveness
                ),
                "evidence_count": evidence_count,
                "finding_count": finding_count,
                "critical_finding_count": (
                    critical_finding_count
                ),
                "open_finding_count": (
                    open_finding_count
                ),
            }
        )

    framework_items.sort(
        key=lambda framework: (
            framework["average_effectiveness"]
        ),
        reverse=True,
    )

    return {
        "summary": {
            "total_frameworks": total_frameworks,
            "total_controls": total_controls,
            "active_controls": active_controls,
            "average_control_effectiveness": (
                average_control_effectiveness
            ),
            "total_evidence": total_evidence,
            "total_findings": total_findings,
            "open_findings": open_findings,
            "critical_findings": critical_findings,
        },
        "frameworks": framework_items,
    }