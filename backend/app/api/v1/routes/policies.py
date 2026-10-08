from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.database.database import get_db

from app.models.user import User

from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
)

from app.services.policy_service import (
    create_policy,
    get_all_policies,
    get_policy_by_id,
    update_policy,
    delete_policy,
)


router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


@router.post(
    "/",
    response_model=PolicyResponse,
)
def create_new_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "policies",
            "create",
        )
    ),
):
    return create_policy(
        db,
        policy_data,
        current_user,
    )


@router.get(
    "/",
    response_model=list[PolicyResponse],
)
def list_all_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "policies",
            "view",
        )
    ),
):
    return get_all_policies(
        db,
        current_user,
    )


@router.get(
    "/{policy_id}",
    response_model=PolicyResponse,
)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "policies",
            "view",
        )
    ),
):
    return get_policy_by_id(
        db,
        policy_id,
        current_user,
    )


@router.patch(
    "/{policy_id}",
    response_model=PolicyResponse,
)
def update_existing_policy(
    policy_id: int,
    policy_data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "policies",
            "update",
        )
    ),
):
    return update_policy(
        db,
        policy_id,
        policy_data,
        current_user,
    )


@router.delete(
    "/{policy_id}",
)
def delete_existing_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "policies",
            "delete",
        )
    ),
):
    delete_policy(
        db,
        policy_id,
        current_user,
    )

    return {
        "message": "Policy deleted successfully."
    }