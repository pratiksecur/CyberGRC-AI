from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.auth.dependencies import get_current_user

from app.database.database import get_db

from app.models.user import User

from app.schemas.framework import (
    FrameworkCreate,
    FrameworkUpdate,
    FrameworkResponse,
)

from app.auth.visibility import get_visible_user_ids
from app.services.regulatory_intelligence_service import (
    build_regulatory_intelligence_report,
)

from app.services.framework_service import (
    create_framework,
    get_all_frameworks,
    get_framework_by_id,
    update_framework,
    delete_framework,
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
    return create_framework(
        db,
        framework_data,
        current_user,
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
    return get_all_frameworks(
        db,
        current_user,
    )


@router.get(
    "/intelligence",
)
def get_framework_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "frameworks",
            "view",
        )
    ),
):
    """Return a tenant-scoped regulatory intelligence report."""
    visible_user_ids = set(
        get_visible_user_ids(
            db,
            current_user,
            resource="frameworks",
        )
    )
    return build_regulatory_intelligence_report(
        db,
        visible_user_ids,
        organization_id=current_user.organization_id,
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
    return get_framework_by_id(
        db,
        framework_id,
        current_user,
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
    return update_framework(
        db,
        framework_id,
        framework_data,
        current_user,
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
    delete_framework(
        db,
        framework_id,
        current_user,
    )

    return {
        "message": "Framework deleted successfully."
    }