from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids

from app.models.user import User

from app.schemas.framework import (
    FrameworkCreate,
    FrameworkUpdate,
    FrameworkResponse,
)

from app.schemas.regulatory_intelligence import (
    RegulatoryIntelligenceResponse,
)

from app.services.framework_service import (
    create_framework,
    get_all_frameworks,
    get_framework_by_id,
    update_framework,
    delete_framework,
)

from app.services.regulatory_intelligence_service import (
    build_regulatory_intelligence_report,
)


router = APIRouter(
    prefix="/frameworks",
    tags=["Compliance Frameworks"],
)


@router.post(
    "/",
    response_model=FrameworkResponse,
)
def create_new_framework(
    framework_data: FrameworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "frameworks",
            "create",
        )
    ),
):
    """
    Create a new compliance framework.
    """

    return create_framework(
        db,
        framework_data,
    )


@router.get(
    "/",
    response_model=list[FrameworkResponse],
)
def list_all_frameworks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "frameworks",
            "view",
        )
    ),
):
    """
    Get all compliance frameworks.

    Frameworks are organization-wide resources.
    """

    return get_all_frameworks(db)


# ==========================================================
# PHASE 64 — REGULATORY INTELLIGENCE
# IMPORTANT:
# This route must remain BEFORE /{framework_id}.
# ==========================================================

@router.get(
    "/intelligence",
    response_model=RegulatoryIntelligenceResponse,
)
def get_regulatory_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "frameworks",
            "view",
        )
    ),
):
    """
    Get deterministic regulatory intelligence.

    Framework
        -> Requirement
        -> Control
        -> Evidence
        -> Risk

    This endpoint is read-only and does not
    perform compliance or remediation actions.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "controls",
    )

    return build_regulatory_intelligence_report(
        db,
        visible_user_ids,
    )


@router.get(
    "/{framework_id}",
    response_model=FrameworkResponse,
)
def get_framework(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "frameworks",
            "view",
        )
    ),
):
    """
    Get a framework by ID.
    """

    return get_framework_by_id(
        db,
        framework_id,
    )


@router.patch(
    "/{framework_id}",
    response_model=FrameworkResponse,
)
def update_existing_framework(
    framework_id: int,
    framework_data: FrameworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "frameworks",
            "update",
        )
    ),
):
    """
    Update a compliance framework.
    """

    return update_framework(
        db,
        framework_id,
        framework_data,
    )


@router.delete(
    "/{framework_id}",
)
def delete_existing_framework(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "frameworks",
            "delete",
        )
    ),
):
    """
    Delete a compliance framework.
    """

    delete_framework(
        db,
        framework_id,
    )

    return {
        "message": "Framework deleted successfully.",
    }