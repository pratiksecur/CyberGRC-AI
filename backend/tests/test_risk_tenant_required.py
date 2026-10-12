"""A risk can never exist without an organization."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.risk import Risk


def _risk(owner_id, created_by_id, **extra):
    return Risk(
        title="Tenant test risk",
        description="Checks that a risk always belongs to a tenant.",
        likelihood=2,
        impact=3,
        risk_score=6,
        owner_id=owner_id,
        created_by_id=created_by_id,
        **extra,
    )


def test_organization_column_is_not_nullable():
    assert Risk.__table__.c.organization_id.nullable is False


def test_missing_organization_comes_from_the_owner(db, users):
    risk = _risk(users["analyst"].id, users["admin"].id)

    db.add(risk)
    db.commit()
    db.refresh(risk)

    assert risk.organization_id == users["analyst"].organization_id


def test_owner_in_another_organization_sets_that_organization(
    db, users, second_organization
):
    other_user = second_organization["user"]

    risk = _risk(other_user.id, other_user.id)

    db.add(risk)
    db.commit()
    db.refresh(risk)

    assert risk.organization_id == second_organization["organization"].id


def test_explicit_organization_is_kept(db, users):
    risk = _risk(
        users["analyst"].id,
        users["admin"].id,
        organization_id=users["analyst"].organization_id,
    )

    db.add(risk)
    db.commit()

    assert risk.organization_id == users["analyst"].organization_id


def test_risk_without_a_resolvable_organization_is_rejected(db, users):
    risk = _risk(999999, users["admin"].id)

    db.add(risk)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()