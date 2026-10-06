from datetime import datetime, timedelta, timezone

from app.models.control import Control
from app.models.evidence import Evidence
from app.models.risk import Risk

from app.services.ai_grc_analyst_service import (
    build_ai_grc_analyst_context,
    get_analyst_question_category,
)


def test_question_category_risk():
    assert (
        get_analyst_question_category(
            "What are our biggest risks?"
        )
        == "RISK"
    )


def test_question_category_control():
    assert (
        get_analyst_question_category(
            "Which controls are ineffective?"
        )
        == "CONTROL"
    )


def test_question_category_evidence():
    assert (
        get_analyst_question_category(
            "Where are we missing evidence?"
        )
        == "EVIDENCE"
    )


def test_question_category_regulatory():
    assert (
        get_analyst_question_category(
            "What are our DORA compliance gaps?"
        )
        == "REGULATORY"
    )


def test_question_category_assurance():
    assert (
        get_analyst_question_category(
            "Which corrective actions remain open?"
        )
        == "ASSURANCE"
    )


def test_context_respects_visibility(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    context = build_ai_grc_analyst_context(
        db,
        [admin.id],
    )

    assert "risk_summary" in context
    assert "control_summary" in context
    assert "evidence_summary" in context
    assert "regulatory_summary" in context
    assert "control_intelligence_summary" in context


def test_context_contains_risk_summary(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    risk = Risk(
        title="Critical test risk",
        description="Test risk",
        likelihood=4,
        impact=5,
        risk_score=20,
        status="Open",
        owner_id=admin.id,
        created_by_id=admin.id,
    )

    db.add(risk)
    db.commit()

    context = build_ai_grc_analyst_context(
        db,
        [admin.id],
    )

    assert context["risk_summary"]["critical"] >= 1
    

def test_context_contains_control_summary(
    db,
    users,
):
    admin = users["admin"]

    control = Control(
        title="Ineffective test control",
        description="Test control",
        control_type="Preventive",
        status="Active",
        owner_id=admin.id,
        created_by_id=admin.id,
        effectiveness=40,
    )

    db.add(control)
    db.commit()

    context = build_ai_grc_analyst_context(
        db,
        [admin.id],
    )

    assert (
        context["control_summary"]
        ["ineffective"]
        >= 1
    )


def test_context_detects_missing_evidence(
    db,
    users,
):
    admin = users["admin"]

    control = Control(
        title="Control without evidence",
        description="Test control",
        control_type="Preventive",
        status="Active",
        owner_id=admin.id,
        created_by_id=admin.id,
        effectiveness=80,
    )

    db.add(control)
    db.commit()

    context = build_ai_grc_analyst_context(
        db,
        [admin.id],
    )

    assert (
        control.id
        in context["evidence_summary"]
        ["controls_missing_evidence"]
    )