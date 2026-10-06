from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeGraphNode(BaseModel):
    id: int

    node_type: str

    label: str

    status: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class KnowledgeGraphEdge(BaseModel):
    source_id: int

    source_type: str

    target_id: int

    target_type: str

    relation: str


class KnowledgeGraphSummary(BaseModel):
    total_nodes: int

    total_edges: int

    node_counts: dict[str, int] = Field(
        default_factory=dict
    )

    edge_counts: dict[str, int] = Field(
        default_factory=dict
    )

    risks_with_controls: int = 0

    controls_with_evidence: int = 0

    controls_with_frameworks: int = 0

    findings_with_actions: int = 0

    risks_with_treatments: int = 0

    risks_with_decisions: int = 0

    risks_with_workflows: int = 0

    disconnected_nodes: int = 0


class KnowledgeGraphResponse(BaseModel):
    focus_risk_id: int | None = None

    nodes: list[KnowledgeGraphNode]

    edges: list[KnowledgeGraphEdge]

    summary: KnowledgeGraphSummary

    generated_at: str