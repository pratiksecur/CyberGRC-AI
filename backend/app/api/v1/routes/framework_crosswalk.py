from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.auth.tenant import get_tenant_resource
from app.auth.visibility import get_visible_user_ids
from app.database.database import get_db
from app.models.control import Control
from app.models.user import User
from app.schemas.framework_crosswalk import (
    CrosswalkOpportunitiesResponse,
    CrosswalkRelatedResponse,
    CrosswalkSuggestionsResponse,
)
from app.services.framework_control_service import (
    get_framework_control_by_id,
)
from app.services.framework_crosswalk_service import (
    get_control_suggestions,
    get_crosswalk_opportunities,
    get_related_requirements,
)

router = APIRouter(
    prefix="/framework-crosswalk",
    tags=["Framework Crosswalk"],
)

# Every endpoint here is read-only. A suggestion is applied by the person
# through the normal mapping endpoint (POST /control-framework-controls/).


@router.get(
    "/opportunities",
    response_model=CrosswalkOpportunitiesResponse,
)
def list_crosswalk_opportunities(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("control_framework_mappings", "view")
    ),
):
    """
    Unmapped requirements that controls already mapped to a related
    requirement in another framework may also support.
    """

    visible_user_ids = set(
        get_visible_user_ids(
            db,
            current_user,
            "control_framework_mappings",
        )
    )

    return get_crosswalk_opportunities(
        db,
        current_user.organization_id,
        visible_user_ids,
    )


@router.get(
    "/framework-control/{framework_control_id}/related",
    response_model=CrosswalkRelatedResponse,
)
def list_related_requirements(
    framework_control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("framework_controls", "view")
    ),
):
    """Requirements in other frameworks that share a theme with this one."""

    framework_control = get_framework_control_by_id(
        db,
        framework_control_id,
        current_user,
    )

    if framework_control is None:
        raise HTTPException(
            status_code=404,
            detail="Framework Control not found.",
        )

    visible_user_ids = set(
        get_visible_user_ids(
            db,
            current_user,
            "control_framework_mappings",
        )
    )

    return get_related_requirements(
        db,
        framework_control,
        current_user.organization_id,
        visible_user_ids,
    )


@router.get(
    "/control/{control_id}/suggestions",
    response_model=CrosswalkSuggestionsResponse,
)
def list_control_suggestions(
    control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("control_framework_mappings", "view")
    ),
):
    """Further requirements this control may support, for human review."""

    control = get_tenant_resource(
        db,
        Control,
        control_id,
        current_user,
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found.",
        )

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    if control.owner_id not in visible_user_ids:
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot access mappings for a "
                "Control outside your organizational scope."
            ),
        )

    return get_control_suggestions(
        db,
        control,
        current_user.organization_id,
    )
