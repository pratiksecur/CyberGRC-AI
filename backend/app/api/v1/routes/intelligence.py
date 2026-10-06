from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids

from app.models.user import User
from app.models.risk import Risk

from app.schemas.intelligence import (
    GRCIntelligenceOverviewResponse,
    RiskIntelligenceResponse,
)

from app.schemas.knowledge_graph import (
    KnowledgeGraphResponse,
)

from app.services.grc_intelligence_service import (
    get_grc_intelligence_overview,
    get_risk_intelligence,
)

from app.services.knowledge_graph_service import (
    build_knowledge_graph,
)


router = APIRouter(
    prefix="/intelligence",
    tags=["GRC Intelligence"],
)


# ==========================================================
# RISK INTELLIGENCE
# ==========================================================

@router.get(
    "/risk/{risk_id}",
    response_model=RiskIntelligenceResponse,
)
def get_risk_intelligence_endpoint(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Return scope-aware GRC intelligence for a single risk.

    The risk itself is checked against the user's risk scope.
    Downstream controls, evidence, audits and corrective
    actions are independently filtered using their own
    resource scopes.
    """

    intelligence = get_risk_intelligence(
        db,
        risk_id,
        current_user,
    )

    if intelligence is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    return intelligence


# ==========================================================
# GRC INTELLIGENCE OVERVIEW
# ==========================================================

@router.get(
    "/overview",
    response_model=GRCIntelligenceOverviewResponse,
)
def get_grc_intelligence_overview_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Return an aggregated GRC intelligence overview
    limited to the current user's visibility.
    """

    return get_grc_intelligence_overview(
        db,
        current_user,
    )


# ==========================================================
# GRC KNOWLEDGE GRAPH
# ==========================================================

@router.get(
    "/knowledge-graph",
    response_model=KnowledgeGraphResponse,
)
def get_knowledge_graph_endpoint(
    risk_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Return a visibility-aware GRC knowledge graph.

    The graph is deterministic and read-only.

    It does not mutate risks, controls, evidence,
    findings, corrective actions, treatments,
    decisions, or workflows.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    # ------------------------------------------------------
    # Focused risk visibility
    # ------------------------------------------------------
    #
    # A user may have permission to use the knowledge graph
    # while still being unable to see a particular risk.
    #
    # Therefore, a focused risk must independently satisfy
    # the user's risk visibility scope before the graph
    # service is allowed to build the focused graph.
    #
    # Returning 404 prevents disclosure of the existence of
    # resources outside the caller's visibility boundary.
    # ------------------------------------------------------

    if risk_id is not None:
        focused_risk = (
            db.query(Risk)
            .filter(
                Risk.id == risk_id,
                Risk.owner_id.in_(
                    visible_user_ids
                ),
            )
            .first()
        )

        if focused_risk is None:
            raise HTTPException(
                status_code=404,
                detail="Risk not found.",
            )

    graph = build_knowledge_graph(
        db,
        visible_user_ids,
        focus_risk_id=risk_id,
    )

    if (
        risk_id is not None
        and not graph["nodes"]
    ):
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    return graph