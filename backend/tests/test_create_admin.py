"""The command that creates the first administrator."""

import pytest

from app.auth.hashing import verify_password
from app.core.roles import UserRole
from app.models.user import User
from app.seed.create_admin import create_admin


def test_creates_an_admin_in_the_organization(db, users):
    admin = create_admin(
        db,
        email="  First.Admin@Example.com ",
        full_name="First Admin",
        password="a-long-password",
        organization_id=users["admin"].organization_id,
    )

    assert admin.role == UserRole.ADMIN.value
    assert admin.email == "first.admin@example.com"
    assert admin.organization_id == users["admin"].organization_id
    assert admin.hashed_password != "a-long-password"
    assert verify_password("a-long-password", admin.hashed_password)


def test_created_admin_can_log_in(client, db, users):
    create_admin(
        db,
        email="first.admin@example.com",
        full_name="First Admin",
        password="a-long-password",
        organization_id=users["admin"].organization_id,
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "first.admin@example.com",
            "password": "a-long-password",
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"email": "not-an-email"}, "valid email"),
        ({"full_name": "x"}, "Full name"),
        ({"password": "short"}, "Password must be"),
        ({"organization_id": 999999}, "does not exist"),
    ],
)
def test_rejects_bad_input(db, users, overrides, message):
    values = {
        "email": "first.admin@example.com",
        "full_name": "First Admin",
        "password": "a-long-password",
        "organization_id": users["admin"].organization_id,
        **overrides,
    }

    with pytest.raises(ValueError, match=message):
        create_admin(db, **values)

    assert db.query(User).filter(User.email == "first.admin@example.com").count() == 0


def test_rejects_an_existing_email(db, users):
    with pytest.raises(ValueError, match="already exists"):
        create_admin(
            db,
            email=users["manager"].email,
            full_name="Duplicate",
            password="a-long-password",
            organization_id=users["admin"].organization_id,
        )