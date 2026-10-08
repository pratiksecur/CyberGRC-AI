import pytest

from app.auth.tenant import (
    apply_tenant_filter,
    ensure_related_resources_same_organization,
    ensure_resource_organization_id,
    ensure_resource_same_organization,
    get_tenant_resource,
)


class DummyResource:
    def __init__(self, organization_id):
        self.organization_id = organization_id


def test_resource_in_same_organization_is_allowed(users):
    user = users["admin"]

    resource = DummyResource(
        organization_id=user.organization_id,
    )

    ensure_resource_same_organization(
        user,
        resource,
    )


def test_resource_from_different_organization_is_blocked(users):
    user = users["admin"]

    resource = DummyResource(
        organization_id=user.organization_id + 999999,
    )

    with pytest.raises(
        PermissionError,
        match="Cross-organization access is not permitted.",
    ):
        ensure_resource_same_organization(
            user,
            resource,
        )


def test_resource_without_organization_is_blocked(users):
    user = users["admin"]

    resource = DummyResource(
        organization_id=None,
    )

    with pytest.raises(
        PermissionError,
        match="Resource organization is unavailable.",
    ):
        ensure_resource_same_organization(
            user,
            resource,
        )


def test_organization_id_in_same_tenant_is_allowed(users):
    user = users["admin"]

    ensure_resource_organization_id(
        user,
        user.organization_id,
    )


def test_organization_id_from_different_tenant_is_blocked(users):
    user = users["admin"]

    with pytest.raises(
        PermissionError,
        match="Cross-organization access is not permitted.",
    ):
        ensure_resource_organization_id(
            user,
            user.organization_id + 999999,
        )


def test_related_resources_from_same_tenant_are_allowed(users):
    user = users["admin"]

    resource_a = DummyResource(
        organization_id=user.organization_id,
    )

    resource_b = DummyResource(
        organization_id=user.organization_id,
    )

    ensure_related_resources_same_organization(
        user,
        resource_a,
        resource_b,
    )


def test_related_resources_from_different_tenant_are_blocked(users):
    user = users["admin"]

    resource_a = DummyResource(
        organization_id=user.organization_id,
    )

    resource_b = DummyResource(
        organization_id=user.organization_id + 999999,
    )

    with pytest.raises(
        PermissionError,
        match="Cross-organization access is not permitted.",
    ):
        ensure_related_resources_same_organization(
            user,
            resource_a,
            resource_b,
        )