from app.auth.tenant import (
    ensure_organization_id,
    ensure_same_organization,
    get_current_organization,
)
from app.auth.visibility import (
    get_visible_user_ids,
)
from app.models.organization import Organization
from app.models.user import User


def test_users_have_organization_membership(
    db,
    users,
):
    organization_ids = {
        user.organization_id
        for user in users.values()
    }

    assert len(organization_ids) == 1


def test_current_user_organization_is_resolved(
    db,
    users,
):
    admin = users["admin"]

    organization = get_current_organization(
        db,
        admin,
    )

    assert organization.id == 1
    assert (
        organization.name
        == "Default Organization"
    )
    assert (
        organization.slug
        == "default-organization"
    )
    assert organization.is_active is True


def test_same_organization_is_allowed(
    users,
):
    admin = users["admin"]
    manager = users["manager"]

    ensure_same_organization(
        admin,
        manager,
    )


def test_cross_organization_is_rejected(
    db,
    users,
):
    admin = users["admin"]

    other_organization = Organization(
        name="Other Organization",
        slug="other-organization",
        is_active=True,
    )

    db.add(
        other_organization
    )

    db.commit()
    db.refresh(
        other_organization
    )

    external_user = User(
        full_name="External User",
        email="external@example.com",
        hashed_password="test-password",
        role="Employee",
        manager_id=None,
        department="External",
        organization_id=other_organization.id,
    )

    db.add(
        external_user
    )

    db.commit()
    db.refresh(
        external_user
    )

    try:
        ensure_same_organization(
            admin,
            external_user,
        )
        assert False, (
            "Cross-organization access "
            "should have been rejected."
        )
    except PermissionError as exc:
        assert (
            str(exc)
            == "Cross-organization access "
            "is not permitted."
        )


def test_organization_id_validation(
    users,
):
    admin = users["admin"]

    ensure_organization_id(
        admin,
        admin.organization_id,
    )


def test_cross_organization_id_validation_is_rejected(
    users,
):
    admin = users["admin"]

    try:
        ensure_organization_id(
            admin,
            999999,
        )
        assert False, (
            "Cross-organization organization_id "
            "should have been rejected."
        )
    except PermissionError as exc:
        assert (
            str(exc)
            == "Cross-organization access "
            "is not permitted."
        )


def test_organization_visibility_is_tenant_scoped(
    db,
    users,
):
    admin = users["admin"]

    visible_ids = get_visible_user_ids(
        db,
        admin,
        resource="users",
    )

    expected_ids = {
        user.id
        for user in users.values()
    }

    assert set(
        visible_ids
    ) == expected_ids


def test_subordinate_visibility_remains_within_tenant(
    db,
    users,
):
    manager = users["manager"]

    visible_ids = get_visible_user_ids(
        db,
        manager,
        resource="risks",
    )

    expected_ids = {
        users["manager"].id,
        users["analyst"].id,
        users["auditor"].id,
        users["employee"].id,
    }

    assert set(
        visible_ids
    ) == expected_ids


def test_organization_model_has_expected_structure(
    db,
):
    organization = Organization(
        name="Structure Test Organization",
        slug="structure-test-organization",
        is_active=True,
    )

    db.add(
        organization
    )

    db.commit()
    db.refresh(
        organization
    )

    assert organization.id is not None
    assert (
        organization.name
        == "Structure Test Organization"
    )
    assert (
        organization.slug
        == "structure-test-organization"
    )
    assert organization.is_active is True