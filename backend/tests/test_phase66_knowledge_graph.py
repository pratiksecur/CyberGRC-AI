from datetime import date

from app.models.control_framework_control import (
    ControlFrameworkControl,
)
from app.models.framework_control import (
    FrameworkControl,
)
from app.models.risk_control import (
    RiskControl,
)
from app.models.risk_treatment import (
    RiskTreatment,
)

from app.services.knowledge_graph_service import (
    build_knowledge_graph,
)


def _node_ids(
    graph,
    node_type,
):
    return {
        node["id"]
        for node in graph["nodes"]
        if node["node_type"] == node_type
    }


def _relations(graph):
    return {
        edge["relation"]
        for edge in graph["edges"]
    }


def test_admin_graph_contains_core_grc_nodes(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    graph = build_knowledge_graph(
        db,
        [admin.id],
    )

    assert graph["nodes"]

    assert (
        "RISK"
        in graph["summary"]["node_counts"]
    )

    assert (
        "CONTROL"
        in graph["summary"]["node_counts"]
    )

    assert (
        "EVIDENCE"
        in graph["summary"]["node_counts"]
    )

    assert (
        "AUDIT"
        in graph["summary"]["node_counts"]
    )

    assert (
        "FINDING"
        in graph["summary"]["node_counts"]
    )

    assert (
        "CORRECTIVE_ACTION"
        in graph["summary"]["node_counts"]
    )


def test_risk_control_evidence_chain(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    risk = resource_data[
        "risks"
    ]["admin"]

    control = resource_data[
        "controls"
    ]["admin"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    db.commit()

    graph = build_knowledge_graph(
        db,
        [admin.id],
    )

    assert (
        risk.id
        in _node_ids(
            graph,
            "RISK",
        )
    )

    assert (
        control.id
        in _node_ids(
            graph,
            "CONTROL",
        )
    )

    relations = _relations(
        graph
    )

    assert (
        "RISK_SUPPORTS_CONTROL"
        in relations
    )

    assert (
        "CONTROL_SUPPORTED_BY_EVIDENCE"
        in relations
    )


def test_framework_requirement_is_connected_to_control(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    control = resource_data[
        "controls"
    ]["admin"]

    from app.models.framework import Framework

    framework = Framework(
        name="Phase 66 Framework",
        version="1.0",
        description="Phase 66 graph test framework.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    framework_control = FrameworkControl(
        framework_id=framework.id,
        control_code="CC-1",
        title="Phase 66 Requirement",
        description="Graph requirement.",
    )

    db.add(framework_control)
    db.commit()
    db.refresh(framework_control)

    db.add(
        ControlFrameworkControl(
            control_id=control.id,
            framework_control_id=(
                framework_control.id
            ),
        )
    )

    db.commit()

    graph = build_knowledge_graph(
        db,
        [admin.id],
    )

    assert (
        framework.id
        in _node_ids(
            graph,
            "FRAMEWORK",
        )
    )

    assert (
        framework_control.id
        in _node_ids(
            graph,
            "FRAMEWORK_REQUIREMENT",
        )
    )

    relations = _relations(
        graph
    )

    assert (
        "FRAMEWORK_CONTAINS_REQUIREMENT"
        in relations
    )

    assert (
        "REQUIREMENT_MAPPED_TO_CONTROL"
        in relations
    )


def test_risk_treatment_is_connected_to_risk(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    risk = resource_data[
        "risks"
    ]["admin"]

    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status="In Progress",
        treatment_plan="Phase 66 treatment graph test.",
        owner_id=admin.id,
        target_date=date.today(),
        residual_likelihood=2,
        residual_impact=3,
        residual_risk_score=6,
        acceptance_status="Not Required",
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    graph = build_knowledge_graph(
        db,
        [admin.id],
    )

    assert (
        treatment.id
        in _node_ids(
            graph,
            "RISK_TREATMENT",
        )
    )

    assert (
        "RISK_HAS_TREATMENT"
        in _relations(graph)
    )

    assert (
        graph["summary"]
        ["risks_with_treatments"]
        >= 1
    )


def test_employee_graph_does_not_expose_admin_risk(
    db,
    users,
    resource_data,
):
    employee = users["employee"]

    admin_risk = resource_data[
        "risks"
    ]["admin"]

    employee_risk = resource_data[
        "risks"
    ]["employee"]

    graph = build_knowledge_graph(
        db,
        [employee.id],
    )

    risk_ids = _node_ids(
        graph,
        "RISK",
    )

    assert (
        employee_risk.id
        in risk_ids
    )

    assert (
        admin_risk.id
        not in risk_ids
    )


def test_focus_risk_returns_only_connected_risk_graph(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    risk = resource_data[
        "risks"
    ]["admin"]

    control = resource_data[
        "controls"
    ]["admin"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    db.commit()

    graph = build_knowledge_graph(
        db,
        [admin.id],
        focus_risk_id=risk.id,
    )

    assert (
        graph["focus_risk_id"]
        == risk.id
    )

    risk_ids = _node_ids(
        graph,
        "RISK",
    )

    assert risk_ids == {
        risk.id
    }

    assert (
        control.id
        in _node_ids(
            graph,
            "CONTROL",
        )
    )


def test_graph_is_read_only(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    risk = resource_data[
        "risks"
    ]["admin"]

    original_title = risk.title

    build_knowledge_graph(
        db,
        [admin.id],
    )

    db.refresh(risk)

    assert (
        risk.title
        == original_title
    )