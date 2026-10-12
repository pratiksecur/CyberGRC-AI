"""Emails are case-insensitive: stored in lowercase, unique, and matched loosely."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.auth.hashing import hash_password
from app.auth.jwt_handler import create_access_token
from app.models.user import User


def _register(client, headers, email, password="Password123!"):
    return client.post(
        "/api/v1/auth/register",
        headers=headers,
        json={
            "full_name": "Case Test",
            "email": email,
            "password": password,
        },
    )


def _login(client, email, password="Password123!"):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def test_new_emails_are_stored_in_lowercase(
    client, db, users, auth_headers
):
    response = _register(
        client, auth_headers(users["admin"]), "Mixed.Case@Example.COM"
    )

    assert response.status_code == 201
    assert response.json()["email"] == "mixed.case@example.com"

    stored = db.query(User).filter(User.id == response.json()["id"]).one()

    assert stored.email == "mixed.case@example.com"


def test_same_email_in_other_capitalisation_is_a_duplicate(
    client, users, auth_headers
):
    headers = auth_headers(users["admin"])

    assert _register(client, headers, "dupe@example.com").status_code == 201

    again = _register(client, headers, "DUPE@Example.com")

    assert again.status_code == 400
    assert again.json()["detail"] == "Email already registered."


def test_login_ignores_capitalisation_and_spaces(
    client, users, auth_headers
):
    _register(client, auth_headers(users["admin"]), "login.case@example.com")

    for typed in (
        "login.case@example.com",
        "Login.Case@Example.com",
        "LOGIN.CASE@EXAMPLE.COM",
        "  login.case@example.com  ",
    ):
        response = _login(client, typed)

        assert response.status_code == 200, typed


def test_existing_mixed_case_account_can_still_sign_in(client, db, users):
    # An account created before emails were normalised.
    db.add(
        User(
            full_name="Legacy User",
            email="Legacy@Example.com",
            hashed_password=hash_password("Password123!"),
            role="Employee",
            organization_id=users["admin"].organization_id,
        )
    )
    db.commit()

    response = _login(client, "legacy@example.com")

    assert response.status_code == 200


def test_token_with_differently_cased_subject_is_accepted(client, users):
    token = create_access_token(data={"sub": users["admin"].email.upper()})

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == users["admin"].email


def test_database_refuses_two_accounts_that_differ_only_by_case(db, users):
    organization_id = users["admin"].organization_id

    db.add(
        User(
            full_name="First",
            email="twin@example.com",
            hashed_password=hash_password("Password123!"),
            role="Employee",
            organization_id=organization_id,
        )
    )
    db.commit()

    db.add(
        User(
            full_name="Second",
            email="TWIN@example.com",
            hashed_password=hash_password("Password123!"),
            role="Employee",
            organization_id=organization_id,
        )
    )

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_user_without_an_organization_is_rejected(db, users):
    db.add(
        User(
            full_name="No Tenant",
            email="notenant@example.com",
            hashed_password=hash_password("Password123!"),
            role="Employee",
        )
    )

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()