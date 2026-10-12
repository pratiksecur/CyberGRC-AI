from datetime import date, timedelta

from app.models.control import Control
from app.models.risk import Risk
from app.models.risk_treatment import RiskTreatment
from app.services.executive_intelligence_service import (
    build_executive_intelligence,
)


def test_executive_intelligence_returns_core_posture(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    result = build_executive_intelligence(
        db,
        [admin.id],
    )

    assert "risk_posture" in result
    assert "compliance_posture" in result
    assert "control_health" in result
    assert "regulatory_exposure" in result
    assert "findings" in result
    assert "remediation" in result
    assert "treatment_effectiveness" in result
    assert "workflow_health" in result
    assert "explainability" in result


def test_executive_intelligence_respects_risk_visibility(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    admin_risk = resource_data[
        "risks"
    ]["admin"]

    manager = users["manager"]

    result = build_executive_intelligence(
        db,
        [manager.id],
    )

    visible_ids = {
        item["owner_id"]
        for item in result[
            "business_unit_exposure"
        ]
    }

    assert (
        admin_risk.owner_id
        not in visible_ids
        or admin_risk.owner_id == manager.id
    )


def test_executive_intelligence_detects_critical_risk(
    db,
    users,
):
    admin = users["admin"]

    risk = Risk(
        title="Phase 67 Critical Risk",
        description="Executive intelligence test.",
        likelihood=4,
        impact=5,
        risk_score=20,
        status="Open",
        owner_id=admin.id,
        created_by_id=admin.id,
    )

    db.add(risk)
    db.commit()

    result = build_executive_intelligence(
        db,
        [admin.id],
    )

    assert result[
        "risk_posture"
    ]["critical"] >= 1

    assert any(
        item["signal"]
        == "CRITICAL_RISKS"
        for item in result[
            "explainability"
        ]
    )


def test_executive_intelligence_detects_ineffective_control(
    db,
    users,
):
    admin = users["admin"]

    control = Control(
        title="Phase 67 Ineffective Control",
        description="Executive intelligence test.",
        control_type="Preventive",
        status="Active",
        effectiveness=40,
        owner_id=admin.id,
        created_by_id=admin.id,
    )

    db.add(control)
    db.commit()

    result = build_executive_intelligence(
        db,
        [admin.id],
    )

    assert (
        result["control_health"]
        ["ineffective"]
        >= 1
    )

    assert any(
        item["signal"]
        == "INEFFECTIVE_CONTROLS"
        for item in result[
            "explainability"
        ]
    )


def test_executive_intelligence_detects_overdue_treatment(
    db,
    users,
):
    admin = users["admin"]

    risk = Risk(
        title="Treatment Intelligence Risk",
        description="Executive intelligence test.",
        likelihood=4,
        impact=4,
        risk_score=16,
        status="Open",
        owner_id=admin.id,
        created_by_id=admin.id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status="In Progress",
        treatment_plan=(
            "Implement and continuously review "
            "the treatment controls."
        ),
        owner_id=admin.id,
        target_date=(
            date.today()
            - timedelta(days=2)
        ),
        residual_likelihood=3,
        residual_impact=3,
        residual_risk_score=9,
        acceptance_status="Not Required",
    )

    db.add(treatment)
    db.commit()

    result = build_executive_intelligence(
        db,
        [admin.id],
    )

    assert (
        result[
            "treatment_effectiveness"
        ]["overdue"]
        >= 1
    )


def test_executive_intelligence_is_read_only(
    db,
    users,
):
    admin = users["admin"]

    before_risks = db.query(
        Risk
    ).count()

    before_controls = db.query(
        Control
    ).count()

    result = build_executive_intelligence(
        db,
        [admin.id],
    )

    assert result is not None

    assert db.query(Risk).count() == before_risks
    assert (
        db.query(Control).count()
        == before_controls
    )