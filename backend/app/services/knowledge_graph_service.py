from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.control_framework_control import (
    ControlFrameworkControl,
)
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)
from app.models.risk_treatment import RiskTreatment


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _node(
    node_id: int,
    node_type: str,
    label: str,
    *,
    status: str | None = None,
    metadata: dict | None = None,
) -> dict:
    return {
        "id": node_id,
        "node_type": node_type,
        "label": label,
        "status": status,
        "metadata": metadata or {},
    }


def _edge(
    source_id: int,
    source_type: str,
    target_id: int,
    target_type: str,
    relation: str,
) -> dict:
    return {
        "source_id": source_id,
        "source_type": source_type,
        "target_id": target_id,
        "target_type": target_type,
        "relation": relation,
    }


def build_knowledge_graph(
    db: Session,
    visible_user_ids: list[int],
    *,
    focus_risk_id: int | None = None,
) -> dict:
    """
    Build a deterministic, read-only GRC knowledge graph.

    The graph is derived entirely from existing relational GRC
    records. No graph database or additional persistence layer
    is required.

    Visibility is applied before graph relationships are exposed.
    """

    nodes: dict[tuple[str, int], dict] = {}

    edges: dict[
        tuple[
            str,
            int,
            str,
            int,
            str,
        ],
        dict,
    ] = {}

    def add_node(
        node_id: int,
        node_type: str,
        label: str,
        *,
        status: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        key = (node_type, node_id)

        if key not in nodes:
            nodes[key] = _node(
                node_id,
                node_type,
                label,
                status=status,
                metadata=metadata,
            )

    def add_edge(
        source_id: int,
        source_type: str,
        target_id: int,
        target_type: str,
        relation: str,
    ) -> None:
        source_key = (
            source_type,
            source_id,
        )

        target_key = (
            target_type,
            target_id,
        )

        if (
            source_key not in nodes
            or target_key not in nodes
        ):
            return

        key = (
            source_type,
            source_id,
            target_type,
            target_id,
            relation,
        )

        if key not in edges:
            edges[key] = _edge(
                source_id,
                source_type,
                target_id,
                target_type,
                relation,
            )

    # ==========================================================
    # VISIBLE RISKS
    # ==========================================================

    risk_query = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(
                visible_user_ids
            )
        )
        .order_by(Risk.id.asc())
    )

    if focus_risk_id is not None:
        risk_query = risk_query.filter(
            Risk.id == focus_risk_id
        )

    risks = risk_query.all()

    risk_ids = {
        risk.id
        for risk in risks
    }

    for risk in risks:
        add_node(
            risk.id,
            "RISK",
            risk.title,
            status=risk.status,
            metadata={
                "risk_score": risk.risk_score,
                "likelihood": risk.likelihood,
                "impact": risk.impact,
                "owner_id": risk.owner_id,
            },
        )

    # ==========================================================
    # VISIBLE CONTROLS
    # ==========================================================

    control_query = (
        db.query(Control)
        .filter(
            Control.owner_id.in_(
                visible_user_ids
            )
        )
        .order_by(Control.id.asc())
    )

    if focus_risk_id is not None:
        control_ids_for_focus = [
            row.control_id
            for row in (
                db.query(RiskControl)
                .filter(
                    RiskControl.risk_id == focus_risk_id
                )
                .all()
            )
        ]

        if control_ids_for_focus:
            control_query = control_query.filter(
                Control.id.in_(
                    control_ids_for_focus
                )
            )
        else:
            control_query = control_query.filter(
                Control.id == -1
            )

    controls = control_query.all()

    control_ids = {
        control.id
        for control in controls
    }

    for control in controls:
        add_node(
            control.id,
            "CONTROL",
            control.title,
            status=control.status,
            metadata={
                "effectiveness":
                    control.effectiveness,
                "control_type":
                    control.control_type,
                "owner_id":
                    control.owner_id,
            },
        )

    # ==========================================================
    # RISK -> CONTROL
    # ==========================================================

    risk_controls = []

    if risk_ids and control_ids:
        risk_controls = (
            db.query(RiskControl)
            .filter(
                RiskControl.risk_id.in_(
                    risk_ids
                ),
                RiskControl.control_id.in_(
                    control_ids
                ),
            )
            .order_by(
                RiskControl.id.asc()
            )
            .all()
        )

    for mapping in risk_controls:
        add_edge(
            mapping.risk_id,
            "RISK",
            mapping.control_id,
            "CONTROL",
            "RISK_SUPPORTS_CONTROL",
        )

    # ==========================================================
    # EVIDENCE
    # ==========================================================

    evidence_query = (
        db.query(Evidence)
        .filter(
            Evidence.uploaded_by.in_(
                visible_user_ids
            ),
            Evidence.control_id.in_(
                control_ids
            ),
        )
        .order_by(Evidence.id.asc())
    )

    evidence_records = evidence_query.all()

    evidence_ids = {
        evidence.id
        for evidence in evidence_records
    }

    for evidence in evidence_records:
        add_node(
            evidence.id,
            "EVIDENCE",
            evidence.title,
            metadata={
                "control_id":
                    evidence.control_id,
                "file_name":
                    evidence.file_name,
                "uploaded_by":
                    evidence.uploaded_by,
                "uploaded_at":
                    (
                        evidence.uploaded_at.isoformat()
                        if evidence.uploaded_at
                        else None
                    ),
            },
        )

        add_edge(
            evidence.control_id,
            "CONTROL",
            evidence.id,
            "EVIDENCE",
            "CONTROL_SUPPORTED_BY_EVIDENCE",
        )

    # ==========================================================
    # FRAMEWORK MAPPINGS
    # ==========================================================

    mappings = []

    if control_ids:
        mappings = (
            db.query(
                ControlFrameworkControl
            )
            .filter(
                ControlFrameworkControl.control_id.in_(
                    control_ids
                )
            )
            .order_by(
                ControlFrameworkControl.id.asc()
            )
            .all()
        )

    framework_control_ids = {
        mapping.framework_control_id
        for mapping in mappings
    }

    framework_controls = []

    if framework_control_ids:
        framework_controls = (
            db.query(FrameworkControl)
            .filter(
                FrameworkControl.id.in_(
                    framework_control_ids
                )
            )
            .order_by(
                FrameworkControl.id.asc()
            )
            .all()
        )

    framework_ids = {
        framework_control.framework_id
        for framework_control
        in framework_controls
    }

    frameworks = []

    if framework_ids:
        frameworks = (
            db.query(Framework)
            .filter(
                Framework.id.in_(
                    framework_ids
                )
            )
            .order_by(
                Framework.id.asc()
            )
            .all()
        )

    for framework in frameworks:
        add_node(
            framework.id,
            "FRAMEWORK",
            framework.name,
            metadata={
                "version":
                    framework.version,
            },
        )

    for framework_control in framework_controls:
        add_node(
            framework_control.id,
            "FRAMEWORK_REQUIREMENT",
            (
                f"{framework_control.control_code} - "
                f"{framework_control.title}"
            ),
            metadata={
                "framework_id":
                    framework_control.framework_id,
                "control_code":
                    framework_control.control_code,
            },
        )

        add_edge(
            framework_control.framework_id,
            "FRAMEWORK",
            framework_control.id,
            "FRAMEWORK_REQUIREMENT",
            "FRAMEWORK_CONTAINS_REQUIREMENT",
        )

    for mapping in mappings:
        add_edge(
            mapping.framework_control_id,
            "FRAMEWORK_REQUIREMENT",
            mapping.control_id,
            "CONTROL",
            "REQUIREMENT_MAPPED_TO_CONTROL",
        )

    # ==========================================================
    # AUDITS
    # ==========================================================

    audit_records = (
        db.query(Audit)
        .filter(
            or_(
                Audit.auditor_id.in_(
                    visible_user_ids
                ),
                Audit.created_by_id.in_(
                    visible_user_ids
                ),
            )
        )
        .order_by(Audit.id.asc())
        .all()
    )

    audit_ids = {
        audit.id
        for audit in audit_records
    }

    for audit in audit_records:
        add_node(
            audit.id,
            "AUDIT",
            audit.name,
            status=audit.status,
            metadata={
                "framework_id":
                    audit.framework_id,
                "auditor_id":
                    audit.auditor_id,
                "scope":
                    audit.scope,
                "start_date":
                    audit.start_date.isoformat(),
                "end_date":
                    audit.end_date.isoformat(),
            },
        )

    # ==========================================================
    # FINDINGS
    # ==========================================================

    finding_query = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.control_id.in_(
                control_ids
            ),
            AuditFinding.audit_id.in_(
                audit_ids
            ),
        )
        .order_by(
            AuditFinding.id.asc()
        )
    )

    findings = finding_query.all()

    finding_ids = {
        finding.id
        for finding in findings
    }

    for finding in findings:
        add_node(
            finding.id,
            "FINDING",
            finding.title,
            status=finding.status,
            metadata={
                "severity":
                    finding.severity,
                "control_id":
                    finding.control_id,
                "audit_id":
                    finding.audit_id,
            },
        )

        add_edge(
            finding.control_id,
            "CONTROL",
            finding.id,
            "FINDING",
            "CONTROL_HAS_FINDING",
        )

        add_edge(
            finding.audit_id,
            "AUDIT",
            finding.id,
            "FINDING",
            "AUDIT_IDENTIFIED_FINDING",
        )

    # ==========================================================
    # CORRECTIVE ACTIONS
    # ==========================================================

    actions = []

    if finding_ids:
        actions = (
            db.query(CorrectiveAction)
            .filter(
                CorrectiveAction.finding_id.in_(
                    finding_ids
                ),
                CorrectiveAction.assigned_to.in_(
                    visible_user_ids
                ),
            )
            .order_by(
                CorrectiveAction.id.asc()
            )
            .all()
        )

    action_ids = {
        action.id
        for action in actions
    }

    for action in actions:
        add_node(
            action.id,
            "CORRECTIVE_ACTION",
            action.title,
            status=action.status,
            metadata={
                "finding_id":
                    action.finding_id,
                "priority":
                    action.priority,
                "assigned_to":
                    action.assigned_to,
                "due_date":
                    action.due_date.isoformat(),
                "completed_at":
                    (
                        action.completed_at.isoformat()
                        if action.completed_at
                        else None
                    ),
            },
        )

        add_edge(
            action.finding_id,
            "FINDING",
            action.id,
            "CORRECTIVE_ACTION",
            "FINDING_REMEDIATED_BY_ACTION",
        )

    # ==========================================================
    # RISK TREATMENTS
    # ==========================================================

    treatments = []

    if risk_ids:
        treatments = (
            db.query(RiskTreatment)
            .filter(
                RiskTreatment.risk_id.in_(
                    risk_ids
                ),
                RiskTreatment.owner_id.in_(
                    visible_user_ids
                ),
            )
            .order_by(
                RiskTreatment.id.asc()
            )
            .all()
        )

    treatment_ids = {
        treatment.id
        for treatment in treatments
    }

    for treatment in treatments:
        add_node(
            treatment.id,
            "RISK_TREATMENT",
            (
                f"{treatment.strategy} treatment"
            ),
            status=treatment.status,
            metadata={
                "risk_id":
                    treatment.risk_id,
                "strategy":
                    treatment.strategy,
                "owner_id":
                    treatment.owner_id,
                "residual_risk_score":
                    treatment.residual_risk_score,
                "acceptance_status":
                    treatment.acceptance_status,
            },
        )

        add_edge(
            treatment.risk_id,
            "RISK",
            treatment.id,
            "RISK_TREATMENT",
            "RISK_HAS_TREATMENT",
        )

    # ==========================================================
    # RESPONSE DECISIONS
    # ==========================================================

    decisions = []

    if risk_ids:
        decisions = (
            db.query(
                RiskResponseDecisionRecord
            )
            .filter(
                RiskResponseDecisionRecord.risk_id.in_(
                    risk_ids
                )
            )
            .order_by(
                RiskResponseDecisionRecord.id.asc()
            )
            .all()
        )

    decision_ids = {
        decision.id
        for decision in decisions
    }

    for decision in decisions:
        add_node(
            decision.id,
            "RESPONSE_DECISION",
            (
                f"{decision.decision} decision"
            ),
            status=decision.status,
            metadata={
                "risk_id":
                    decision.risk_id,
                "decision":
                    decision.decision,
                "priority":
                    decision.priority,
                "governance_level":
                    decision.governance_level,
                "human_approval_required":
                    decision.human_approval_required,
                "risk_state":
                    decision.risk_state,
                "treatment_state":
                    decision.treatment_state,
            },
        )

        add_edge(
            decision.risk_id,
            "RISK",
            decision.id,
            "RESPONSE_DECISION",
            "RISK_HAS_RESPONSE_DECISION",
        )

    # ==========================================================
    # RESPONSE WORKFLOWS
    # ==========================================================

    workflows = []

    if risk_ids:
        workflows = (
            db.query(
                RiskResponseWorkflowRecord
            )
            .filter(
                RiskResponseWorkflowRecord.risk_id.in_(
                    risk_ids
                )
            )
            .order_by(
                RiskResponseWorkflowRecord.id.asc()
            )
            .all()
        )

    for workflow in workflows:
        add_node(
            workflow.id,
            "RESPONSE_WORKFLOW",
            workflow.title,
            status=workflow.status,
            metadata={
                "risk_id":
                    workflow.risk_id,
                "workflow_type":
                    workflow.workflow_type,
                "target_type":
                    workflow.target_type,
                "target_id":
                    workflow.target_id,
                "created_by":
                    workflow.created_by_id,
                "started_at":
                    (
                        workflow.started_at.isoformat()
                        if workflow.started_at
                        else None
                    ),
                "completed_at":
                    (
                        workflow.completed_at.isoformat()
                        if workflow.completed_at
                        else None
                    ),
            },
        )

        add_edge(
            workflow.risk_id,
            "RISK",
            workflow.id,
            "RESPONSE_WORKFLOW",
            "RISK_HAS_RESPONSE_WORKFLOW",
        )

        add_edge(
            workflow.decision_id,
            "RESPONSE_DECISION",
            workflow.id,
            "RESPONSE_WORKFLOW",
            "DECISION_CREATED_WORKFLOW",
        )

        target_map = {
            "CONTROL": (
                "CONTROL",
                control_ids,
            ),
            "EVIDENCE": (
                "EVIDENCE",
                evidence_ids,
            ),
            "CORRECTIVE_ACTION": (
                "CORRECTIVE_ACTION",
                action_ids,
            ),
            "RISK_TREATMENT": (
                "RISK_TREATMENT",
                treatment_ids,
            ),
            "RISK": (
                "RISK",
                risk_ids,
            ),
        }

        target_info = target_map.get(
            workflow.target_type
        )

        if (
            target_info is not None
            and workflow.target_id is not None
        ):
            target_type, allowed_ids = target_info

            if workflow.target_id in allowed_ids:
                add_edge(
                    workflow.id,
                    "RESPONSE_WORKFLOW",
                    workflow.target_id,
                    target_type,
                    "WORKFLOW_TARGETS_RESOURCE",
                )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    node_values = list(
        nodes.values()
    )

    edge_values = list(
        edges.values()
    )

    node_counts = Counter(
        node["node_type"]
        for node in node_values
    )

    edge_counts = Counter(
        edge["relation"]
        for edge in edge_values
    )

    connected_node_keys: set[
        tuple[str, int]
    ] = set()

    for edge in edge_values:
        connected_node_keys.add(
            (
                edge["source_type"],
                edge["source_id"],
            )
        )

        connected_node_keys.add(
            (
                edge["target_type"],
                edge["target_id"],
            )
        )

    disconnected_nodes = sum(
        1
        for key in nodes
        if key not in connected_node_keys
    )

    risk_control_risk_ids = {
        edge["source_id"]
        for edge in edge_values
        if (
            edge["relation"]
            == "RISK_SUPPORTS_CONTROL"
        )
    }

    control_evidence_control_ids = {
        edge["source_id"]
        for edge in edge_values
        if (
            edge["relation"]
            == "CONTROL_SUPPORTED_BY_EVIDENCE"
        )
    }

    framework_control_ids_connected = {
        edge["target_id"]
        for edge in edge_values
        if (
            edge["relation"]
            == "REQUIREMENT_MAPPED_TO_CONTROL"
        )
    }

    finding_ids_with_actions = {
        edge["source_id"]
        for edge in edge_values
        if (
            edge["relation"]
            == "FINDING_REMEDIATED_BY_ACTION"
        )
    }

    treatment_risk_ids = {
        edge["source_id"]
        for edge in edge_values
        if (
            edge["relation"]
            == "RISK_HAS_TREATMENT"
        )
    }

    decision_risk_ids = {
        edge["source_id"]
        for edge in edge_values
        if (
            edge["relation"]
            == "RISK_HAS_RESPONSE_DECISION"
        )
    }

    workflow_risk_ids = {
        edge["source_id"]
        for edge in edge_values
        if (
            edge["relation"]
            == "RISK_HAS_RESPONSE_WORKFLOW"
        )
    }

    summary = {
        "total_nodes":
            len(node_values),
        "total_edges":
            len(edge_values),
        "node_counts":
            dict(node_counts),
        "edge_counts":
            dict(edge_counts),
        "risks_with_controls":
            len(risk_control_risk_ids),
        "controls_with_evidence":
            len(control_evidence_control_ids),
        "controls_with_frameworks":
            len(framework_control_ids_connected),
        "findings_with_actions":
            len(finding_ids_with_actions),
        "risks_with_treatments":
            len(treatment_risk_ids),
        "risks_with_decisions":
            len(decision_risk_ids),
        "risks_with_workflows":
            len(workflow_risk_ids),
        "disconnected_nodes":
            disconnected_nodes,
    }

    return {
        "focus_risk_id":
            focus_risk_id,
        "nodes":
            node_values,
        "edges":
            edge_values,
        "summary":
            summary,
        "generated_at":
            _utcnow().isoformat(),
    }