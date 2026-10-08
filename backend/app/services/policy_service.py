from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.models.user import User

from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
)

from app.exceptions.exceptions import (
    ResourceNotFound,
    DuplicateResource,
)


def _get_same_tenant_user(
    db: Session,
    user_id: int,
    current_user: User,
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if user is None:
        raise ResourceNotFound("Policy Owner")

    return user


def create_policy(
    db: Session,
    policy_data: PolicyCreate,
    current_user: User,
):
    """
    Create a policy inside the authenticated user's organization.
    """

    owner = _get_same_tenant_user(
        db,
        policy_data.owner_id,
        current_user,
    )

    existing = (
        db.query(Policy)
        .filter(
            Policy.organization_id
            == current_user.organization_id,
            Policy.name == policy_data.name,
        )
        .first()
    )

    if existing:
        raise DuplicateResource("Policy")

    policy = Policy(
        organization_id=current_user.organization_id,
        owner_id=owner.id,
        name=policy_data.name,
        version=policy_data.version,
        description=policy_data.description,
        status=policy_data.status,
        effective_date=policy_data.effective_date,
        review_date=policy_data.review_date,
    )

    db.add(policy)

    db.commit()

    db.refresh(policy)

    return policy


def get_all_policies(
    db: Session,
    current_user: User,
):
    return (
        db.query(Policy)
        .filter(
            Policy.organization_id
            == current_user.organization_id,
        )
        .order_by(
            Policy.name.asc(),
            Policy.id.asc(),
        )
        .all()
    )


def get_policy_by_id(
    db: Session,
    policy_id: int,
    current_user: User,
):
    policy = (
        db.query(Policy)
        .filter(
            Policy.id == policy_id,
            Policy.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if policy is None:
        raise ResourceNotFound("Policy")

    return policy


def update_policy(
    db: Session,
    policy_id: int,
    policy_data: PolicyUpdate,
    current_user: User,
):
    policy = get_policy_by_id(
        db,
        policy_id,
        current_user,
    )

    if policy_data.owner_id is not None:
        owner = _get_same_tenant_user(
            db,
            policy_data.owner_id,
            current_user,
        )

        policy.owner_id = owner.id

    if (
        policy_data.name is not None
        and policy_data.name != policy.name
    ):
        existing = (
            db.query(Policy)
            .filter(
                Policy.organization_id
                == current_user.organization_id,
                Policy.name == policy_data.name,
                Policy.id != policy.id,
            )
            .first()
        )

        if existing:
            raise DuplicateResource("Policy")

        policy.name = policy_data.name

    if policy_data.version is not None:
        policy.version = policy_data.version

    if policy_data.description is not None:
        policy.description = policy_data.description

    if policy_data.status is not None:
        policy.status = policy_data.status

    if policy_data.effective_date is not None:
        policy.effective_date = policy_data.effective_date

    if policy_data.review_date is not None:
        policy.review_date = policy_data.review_date

    db.commit()

    db.refresh(policy)

    return policy


def delete_policy(
    db: Session,
    policy_id: int,
    current_user: User,
):
    policy = get_policy_by_id(
        db,
        policy_id,
        current_user,
    )

    db.delete(policy)

    db.commit()

    return True