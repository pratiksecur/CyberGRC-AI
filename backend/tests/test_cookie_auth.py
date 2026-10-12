"""Browser sessions: httpOnly cookie authentication with CSRF protection."""

import pytest

from app.auth.cookies import ACCESS_COOKIE_NAME, CSRF_HEADER_NAME, csrf_token_for


def _login(client, users, key="admin"):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": users[key].email,
            "password": "Password123!",
        },
    )

    assert response.status_code == 200, response.text

    return response


def test_login_sets_an_httponly_session_cookie(client, users):
    response = _login(client, users)

    set_cookie = response.headers["set-cookie"].lower()

    assert f"{ACCESS_COOKIE_NAME}=" in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie
    assert "path=/" in set_cookie

    # API clients still receive the token in the body.
    assert response.json()["access_token"]


def test_cookie_alone_authenticates_safe_requests(client, users):
    _login(client, users)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == users["admin"].email


def test_no_cookie_and_no_header_is_unauthorized(client, users):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_tampered_cookie_is_rejected(client, users):
    _login(client, users)

    client.cookies.set(ACCESS_COOKIE_NAME, "not-a-valid-token")

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_cookie_authenticated_post_without_csrf_header_is_forbidden(client, users):
    _login(client, users)

    response = client.post("/api/v1/risks/", json={})

    assert response.status_code == 403
    assert response.json()["detail"] == "CSRF validation failed."


def test_cookie_authenticated_post_with_wrong_csrf_header_is_forbidden(client, users):
    _login(client, users)

    response = client.post(
        "/api/v1/risks/",
        json={},
        headers={CSRF_HEADER_NAME: "0" * 64},
    )

    assert response.status_code == 403


def test_csrf_token_from_endpoint_is_accepted(client, users):
    _login(client, users)

    csrf_response = client.get("/api/v1/auth/csrf")

    assert csrf_response.status_code == 200

    csrf_token = csrf_response.json()["csrf_token"]

    assert csrf_token == csrf_token_for(client.cookies.get(ACCESS_COOKIE_NAME))

    response = client.post(
        "/api/v1/risks/",
        json={},
        headers={CSRF_HEADER_NAME: csrf_token},
    )

    # The CSRF check passed; the empty body is then rejected by validation.
    assert response.status_code == 422


def test_csrf_token_of_another_session_is_rejected(client, users):
    _login(client, users, "admin")
    admin_csrf = client.get("/api/v1/auth/csrf").json()["csrf_token"]

    client.cookies.clear()
    _login(client, users, "manager")

    response = client.post(
        "/api/v1/risks/",
        json={},
        headers={CSRF_HEADER_NAME: admin_csrf},
    )

    assert response.status_code == 403


def test_bearer_header_requests_do_not_need_csrf(client, users, auth_headers):
    client.cookies.clear()

    response = client.post(
        "/api/v1/risks/",
        json={},
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 422


def test_authorization_header_takes_precedence_over_cookie(client, users, auth_headers):
    _login(client, users, "admin")

    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200
    assert response.json()["email"] == users["employee"].email


def test_logout_clears_the_session_cookie(client, users):
    _login(client, users)

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert "max-age=0" in response.headers["set-cookie"].lower()

    assert client.get("/api/v1/auth/me").status_code == 401


def test_failed_login_does_not_set_a_cookie(client, users):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": users["admin"].email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_other_state_changing_methods_also_require_csrf(client, users, method):
    _login(client, users)

    response = getattr(client, method)("/api/v1/risks/1")

    assert response.status_code == 403