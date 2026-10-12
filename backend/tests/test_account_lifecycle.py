"""Password changes, admin resets, deactivation and token revocation."""

import pytest

from app.auth import password_policy
from app.auth.jwt_handler import create_access_token

GOOD = "Password123!"
NEW = "a-brand-new-passphrase"


def _login(client, email, password=GOOD):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def _bearer(client, email, password=GOOD):
    response = _login(client, email, password)

    assert response.status_code == 200, response.text

    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _me(client, headers):
    return client.get("/api/v1/auth/me", headers=headers)


# ----------------------------------------------------------
# Password policy
# ----------------------------------------------------------

@pytest.mark.parametrize(
    "password",
    [
        "short",
        "aaaaaaaaaaaa",
        "Password123",
        "x" * 80,
    ],
)
def test_weak_passwords_are_refused(password):
    assert password_policy.password_problems(password)


def test_password_may_not_contain_email_name_or_full_name():
    assert password_policy.password_problems(
        "janedoe-2024-x", email="janedoe@example.com"
    )
    assert password_policy.password_problems(
        "Jane Doe Jane", full_name="jane doe jane"
    )


def test_a_good_passphrase_is_accepted():
    assert password_policy.password_problems(
        NEW, email="a@example.com", full_name="Some One"
    ) == []


# ----------------------------------------------------------
# Change own password
# ----------------------------------------------------------

def test_change_password_and_sign_in_with_the_new_one(client, users):
    email = users["analyst"].email
    headers = _bearer(client, email)

    response = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": GOOD, "new_password": NEW},
    )

    assert response.status_code == 200, response.text
    assert response.json()["access_token"]

    assert _login(client, email, GOOD).status_code == 401
    assert _login(client, email, NEW).status_code == 200


def test_change_password_returns_a_working_fresh_token(client, users):
    headers = _bearer(client, users["analyst"].email)

    fresh = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": GOOD, "new_password": NEW},
    ).json()["access_token"]

    assert _me(
        client, {"Authorization": f"Bearer {fresh}"}
    ).status_code == 200


def test_change_password_revokes_older_tokens(client, users):
    headers = _bearer(client, users["analyst"].email)

    client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": GOOD, "new_password": NEW},
    )

    assert _me(client, headers).status_code == 401


def test_wrong_current_password_is_refused(client, users):
    headers = _bearer(client, users["analyst"].email)

    response = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": "WrongPassword123!", "new_password": NEW},
    )

    assert response.status_code == 400
    assert _login(client, users["analyst"].email, GOOD).status_code == 200


def test_weak_or_unchanged_new_password_is_refused(client, users):
    headers = _bearer(client, users["analyst"].email)

    for new in ("short", GOOD):
        response = client.post(
            "/api/v1/auth/change-password",
            headers=headers,
            json={"current_password": GOOD, "new_password": new},
        )

        assert response.status_code == 400


def test_change_password_requires_authentication(client, users):
    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": GOOD, "new_password": NEW},
    )

    assert response.status_code in (401, 403)


# ----------------------------------------------------------
# Tokens without a version still work (older sessions)
# ----------------------------------------------------------

def test_token_without_version_claim_is_accepted(client, users, auth_headers):
    assert _me(client, auth_headers(users["analyst"])).status_code == 200


def test_token_with_a_stale_version_is_rejected(client, users):
    token = create_access_token(
        data={"sub": users["analyst"].email, "ver": 5}
    )

    response = _me(client, {"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


# ----------------------------------------------------------
# Logout
# ----------------------------------------------------------

def test_logout_revokes_the_token(client, users):
    headers = _bearer(client, users["analyst"].email)

    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert _me(client, headers).status_code == 401


def test_logout_without_a_session_still_succeeds(client):
    assert client.post("/api/v1/auth/logout").status_code == 200


# ----------------------------------------------------------
# Admin reset
# ----------------------------------------------------------

def test_admin_can_reset_a_password(client, users):
    admin = _bearer(client, users["admin"].email)
    target = users["employee"]
    old_headers = _bearer(client, target.email)

    response = client.post(
        f"/api/v1/users/{target.id}/reset-password",
        headers=admin,
        json={"new_password": NEW},
    )

    assert response.status_code == 200, response.text
    assert _me(client, old_headers).status_code == 401
    assert _login(client, target.email, GOOD).status_code == 401
    assert _login(client, target.email, NEW).status_code == 200


def test_admin_cannot_reset_their_own_password_this_way(client, users):
    admin = _bearer(client, users["admin"].email)

    response = client.post(
        f"/api/v1/users/{users['admin'].id}/reset-password",
        headers=admin,
        json={"new_password": NEW},
    )

    assert response.status_code == 400


def test_reset_applies_the_password_policy(client, users):
    admin = _bearer(client, users["admin"].email)

    response = client.post(
        f"/api/v1/users/{users['employee'].id}/reset-password",
        headers=admin,
        json={"new_password": "short"},
    )

    assert response.status_code == 400


def test_reset_cannot_cross_organizations(client, users, second_organization):
    admin = _bearer(client, users["admin"].email)

    response = client.post(
        f"/api/v1/users/{second_organization['user'].id}/reset-password",
        headers=admin,
        json={"new_password": NEW},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("action", ["reset-password", "deactivate", "activate"])
def test_only_admins_can_manage_accounts(client, users, action):
    headers = _bearer(client, users["manager"].email)

    response = client.post(
        f"/api/v1/users/{users['employee'].id}/{action}",
        headers=headers,
        json={"new_password": NEW},
    )

    assert response.status_code == 403


# ----------------------------------------------------------
# Deactivate / activate
# ----------------------------------------------------------

def test_deactivated_user_loses_access_immediately(client, users):
    admin = _bearer(client, users["admin"].email)
    target = users["employee"]
    headers = _bearer(client, target.email)

    response = client.post(
        f"/api/v1/users/{target.id}/deactivate", headers=admin
    )

    assert response.status_code == 200, response.text
    assert response.json()["user"]["is_active"] is False
    assert _me(client, headers).status_code == 401

    blocked = _login(client, target.email)

    assert blocked.status_code == 401
    assert blocked.json()["detail"] == "Invalid email or password."


def test_reactivated_user_can_sign_in_again(client, users):
    admin = _bearer(client, users["admin"].email)
    target = users["employee"]

    client.post(f"/api/v1/users/{target.id}/deactivate", headers=admin)

    response = client.post(
        f"/api/v1/users/{target.id}/activate", headers=admin
    )

    assert response.status_code == 200
    assert response.json()["user"]["is_active"] is True
    assert _login(client, target.email).status_code == 200


def test_admin_cannot_deactivate_themselves(client, users):
    admin = _bearer(client, users["admin"].email)

    response = client.post(
        f"/api/v1/users/{users['admin'].id}/deactivate", headers=admin
    )

    assert response.status_code == 400


def test_last_active_admin_cannot_be_deactivated(db, users):
    from app.auth.hashing import hash_password
    from app.models.user import User
    from app.services import account_service

    first = users["admin"]
    second = User(
        full_name="Second Admin",
        email="second.admin.local@example.com",
        hashed_password=hash_password(GOOD),
        role="admin",
        organization_id=first.organization_id,
    )
    db.add(second)
    db.commit()

    # Two active admins: one may be deactivated.
    account_service.set_user_active(db, first, second, False)

    # Now `first` is the only active admin; another admin account
    # (even a stale one) must not be able to remove them.
    with pytest.raises(ValueError, match="last active administrator"):
        account_service.set_user_active(db, second, first, False)


def test_deactivate_cannot_cross_organizations(client, users, second_organization):
    admin = _bearer(client, users["admin"].email)

    response = client.post(
        f"/api/v1/users/{second_organization['user'].id}/deactivate",
        headers=admin,
    )

    assert response.status_code == 404