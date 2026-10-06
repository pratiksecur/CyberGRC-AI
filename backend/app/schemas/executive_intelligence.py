from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExecutiveIntelligenceResponse(
    BaseModel
):
    risk_posture: dict[str, Any] = Field(
        default_factory=dict
    )

    compliance_posture: dict[str, Any] = Field(
        default_factory=dict
    )

    control_health: dict[str, Any] = Field(
        default_factory=dict
    )

    regulatory_exposure: dict[str, Any] = Field(
        default_factory=dict
    )

    findings: dict[str, Any] = Field(
        default_factory=dict
    )

    remediation: dict[str, Any] = Field(
        default_factory=dict
    )

    treatment_effectiveness: dict[str, Any] = Field(
        default_factory=dict
    )

    workflow_health: dict[str, Any] = Field(
        default_factory=dict
    )

    regulatory: dict[str, Any] = Field(
        default_factory=dict
    )

    business_unit_exposure: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )

    explainability: list[
        dict[str, Any]
    ] = Field(
        default_factory=list
    )

    scope: dict[str, Any] = Field(
        default_factory=dict
    )

    generated_at: str