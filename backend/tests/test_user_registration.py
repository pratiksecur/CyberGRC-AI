"""User creation is administrator-only and stays inside the admin's tenant."""

import pytest

from app.core.roles import UserRole
from app.models.user import User


def _payload(email="new.user@example.com", **extra):
    return {
        "full_name": "New User",
        "email": email,
        "password": "Password123!",
        **extra,
    }


def test_anonymous_registration_is_closed(client, users):
    response = client.post("/api/v1/auth/register", json=_payload())

    assert response.status_code == 401


@pytest.mark.parametrize("key", ["manager", "analyst", "auditor", "employee"])
def test_non_admins_cannot_create_users(client, users, auth_headers, key):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers(users[key]),
        json=_payload(),
    )

    assert response.status_code == 403


def test_admin_creates_an_employee_in_their_own_organization(
    client, db, users, auth_headers
):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers(users["admin"]),
        json=_payload(),
    )

    assert response.status_code == 201
    assert response.json()["role"] == UserRole.EMPLOYEE.value

    created = db.query(User).filter(User.email == "new.user@example.com").one()

    assert created.organization_id == users["admin"].organization_id


def test_admin_can_choose_a_role(client, users, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers(users["admin"]),
        json=_payload(role=UserRole.AUDITOR.value),
    )

    assert response.status_code == 201
    assert response.json()["role"] == UserRole.AUDITOR.value


def test_unknown_role_is_rejected(client, users, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers(users["admin"]),
        json=_payload(role="Super Admin"),
    )

    assert response.status_code == 422


def test_organization_cannot_be_chosen_in_the_request(
    client, db, users, second_organization, auth_headers
):
    other_id = second_organization["organization"].id

    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers(users["admin"]),
        json=_payload(organization_id=other_id),
    )

    assert response.status_code == 201

    created = db.query(User).filter(User.email == "new.user@example.com").one()

    assert created.organization_id == users["admin"].organization_id
    assert created.organization_id != other_id


def test_another_organizations_admin_creates_users_in_that_organization(
    client, db, users, second_organization, auth_headers
):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers(second_organization["user"]),
        json=_payload(),
    )

    assert response.status_code == 201

    created = db.query(User).filter(User.email == "new.user@example.com").one()

    assert created.organization_id == second_organization["organization"].id
    assert created.organization_id != users["admin"].organization_id


def test_duplicate_email_is_rejected(client, users, auth_headers):
    response = client.post(
        "/api/v1/auth/register",
        headers=auth_headers(users["admin"]),
        json=_payload(email=users["manager"].email),
    )

    assert response.status_code == 400


def test_created_user_can_log_in(client, users, auth_headers):
    client.post(
        "/api/v1/auth/register",
        headers=auth_headers(users["admin"]),
        json=_payload(),
    )

    client.cookies.clear()

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "new.user@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    me = client.get("/api/v1/auth/me")

    assert me.status_code == 200
    assert me.json()["email"] == "new.user@example.com"