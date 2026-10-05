"""
Compatibility wrapper for the Phase 61.9 Risk Response
Workflow AI Explanation Service.

The canonical implementation lives at:

    app.services.ai.risk_response_workflow_ai_service

This module re-exports the canonical implementation so that
there is only one actual implementation of the workflow AI
explanation logic.
"""

from app.services.ai.risk_response_workflow_ai_service import (
    explain_risk_response_workflow,
)

__all__ = [
    "explain_risk_response_workflow",
]