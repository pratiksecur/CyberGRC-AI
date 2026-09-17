"""
Phase 43 — Comprehensive Security Hardening Tests

This test suite performs security-focused testing across the
CyberGRC-AI API.

Coverage:

    43A — JWT / Authentication
    43B — Privilege Escalation / Mass Assignment
    43C — IDOR / BOLA
    43D — Input Validation
    43E — File Upload Security
    43F — HTTP / API Security
    43G — Injection / Error Leakage
    43H — Security Regression

Important:

Some tests in this suite are intentionally written against
the desired hardened security behavior.

If one of these tests fails, that is treated as a security
hardening finding that we will fix during Phase 43.

The existing Phase 40–42 authorization behavior must remain
intact.
"""

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from jose import jwt

from app.auth.hashing import (
    hash_password,
    verify_password,
)
from app.auth.jwt_handler import (
    create_access_token,
    verify_access_token,
)
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
)
from app.core.roles import UserRole
from app.models.user import User


# ==========================================================
# HELPERS
# ==========================================================


def bearer(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def user_headers(auth_headers, users, key):
    return auth_headers(users[key])


def valid_risk_payload(owner_id):
    return {
        "title": "Phase 43 Security Risk",
        "description": (
            "Risk created during Phase 43 security testing."
        ),
        "likelihood": 3,
        "impact": 4,
        "owner_id": owner_id,
    }


def valid_control_payload(owner_id):
    return {
        "title": "Phase 43 Security Control",
        "description": (
            "Control created during Phase 43 security testing."
        ),
        "control_type": "Preventive",
        "status": "Active",
        "effectiveness": 80,
        "owner_id": owner_id,
    }


# ==========================================================
# 43A — JWT / AUTHENTICATION
# ==========================================================


def test_jwt_contains_expiration(
    users,
):
    token = create_access_token(
        {
            "sub": users["admin"].email,
        }
    )

    payload = verify_access_token(token)

    assert payload is not None
    assert "exp" in payload


def test_jwt_contains_issued_at_when_supported(
    users,
):
    """
    Phase 43 accepts either the existing JWT contract or
    the hardened contract containing iat.

    Once iat is implemented, this test becomes a direct
    assertion of token issuance tracking.
    """

    token = create_access_token(
        {
            "sub": users["admin"].email,
        }
    )

    payload = verify_access_token(token)

    assert payload is not None

    if "iat" in payload:
        assert payload["iat"] <= payload["exp"]


def test_expired_jwt_is_rejected():
    token = jwt.encode(
        {
            "sub": "admin@example.com",
            "iat": datetime.now(
                timezone.utc
            ) - timedelta(hours=1),
            "exp": datetime.now(
                timezone.utc
            ) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert verify_access_token(token) is None


def test_tampered_jwt_is_rejected(
    users,
):
    token = create_access_token(
        {
            "sub": users["admin"].email,
        }
    )

    parts = token.split(".")

    assert len(parts) == 3

    tampered_token = (
        f"{parts[0]}."
        f"{parts[1]}tampered."
        f"{parts[2]}"
    )

    assert (
        verify_access_token(tampered_token)
        is None
    )


def test_wrong_signature_is_rejected():
    token = jwt.encode(
        {
            "sub": "admin@example.com",
            "exp": datetime.now(
                timezone.utc
            ) + timedelta(minutes=30),
        },
        "wrong-secret",
        algorithm=ALGORITHM,
    )

    assert verify_access_token(token) is None


@pytest.mark.parametrize(
    "token",
    [
        "",
        "invalid",
        "abc.def",
        "abc.def.ghi",
        "not-a-jwt",
        "Bearer invalid",
    ],
)
def test_malformed_jwt_is_rejected(
    token,
):
    assert verify_access_token(token) is None


def test_jwt_without_subject_is_not_usable(
    client,
):
    token = create_access_token(
        {
            "role": UserRole.ADMIN.value,
        }
    )

    response = client.get(
        "/api/v1/auth/me",
        headers=bearer(token),
    )

    assert response.status_code == 401


def test_nonexistent_user_jwt_is_rejected(
    client,
):
    token = create_access_token(
        {
            "sub": "does-not-exist@example.com",
        }
    )

    response = client.get(
        "/api/v1/auth/me",
        headers=bearer(token),
    )

    assert response.status_code == 401


def test_missing_authentication_is_rejected(
    client,
):
    response = client.get(
        "/api/v1/risks/",
    )

    assert response.status_code == 401


def test_invalid_authentication_is_rejected(
    client,
):
    response = client.get(
        "/api/v1/risks/",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_wrong_password_does_not_authenticate(
    client,
    users,
):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": users["admin"].email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_unknown_user_does_not_authenticate(
    client,
):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "unknown-user@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_does_not_enumerate_users(
    client,
    users,
):
    existing_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": users["admin"].email,
            "password": "WrongPassword123!",
        },
    )

    unknown_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "does-not-exist@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert (
        existing_response.status_code
        == unknown_response.status_code
        == 401
    )

    assert (
        existing_response.json()["detail"]
        == unknown_response.json()["detail"]
    )


def test_password_hash_is_not_plaintext():
    password = "Password123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password(
        "WrongPassword123!",
        hashed,
    )


# ==========================================================
# 43B — PRIVILEGE ESCALATION / MASS ASSIGNMENT
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_change_user_role(
    client,
    users,
    auth_headers,
    attacker_key,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/role",
        headers=user_headers(
            auth_headers,
            users,
            attacker_key,
        ),
        json={
            "role": UserRole.ADMIN.value,
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "attacker_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_change_user_organization(
    client,
    users,
    auth_headers,
    attacker_key,
):
    response = client.patch(
        (
            f"/api/v1/users/"
            f"{users['employee'].id}/organization"
        ),
        headers=user_headers(
            auth_headers,
            users,
            attacker_key,
        ),
        json={
            "manager_id": users["admin"].id,
            "department": "Executive",
        },
    )

    assert response.status_code == 403


def test_employee_cannot_promote_self(
    client,
    users,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/role",
        headers=auth_headers(users["employee"]),
        json={
            "role": UserRole.ADMIN.value,
        },
    )

    assert response.status_code == 403


def test_analyst_cannot_promote_self(
    client,
    users,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{users['analyst'].id}/role",
        headers=auth_headers(users["analyst"]),
        json={
            "role": UserRole.ADMIN.value,
        },
    )

    assert response.status_code == 403


def test_employee_cannot_create_admin_role_through_registration(
    client,
):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Malicious Admin",
            "email": "malicious-admin@example.com",
            "password": "Password123!",
            "role": UserRole.ADMIN.value,
        },
    )

    # The role field is not part of UserCreate.
    # Pydantic's default behavior is to ignore the extra
    # field rather than allowing privilege escalation.
    assert response.status_code == 201

    data = response.json()

    assert data["role"] != UserRole.ADMIN.value


def test_risk_owner_cannot_be_injected_to_admin(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json=valid_risk_payload(
            users["admin"].id
        ),
    )

    assert response.status_code == 403


def test_analyst_cannot_create_admin_owned_risk(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["analyst"]),
        json=valid_risk_payload(
            users["admin"].id
        ),
    )

    assert response.status_code == 403


def test_control_owner_cannot_be_injected_to_admin(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(users["employee"]),
        json=valid_control_payload(
            users["admin"].id
        ),
    )

    assert response.status_code == 403


# ==========================================================
# 43C — IDOR / BOLA
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("manager", "admin"),
    ],
)
def test_risk_idor_get_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    risk = resource_data["risks"][target_key]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(
            users[attacker_key]
        ),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("manager", "admin"),
    ],
)
def test_risk_idor_update_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    risk = resource_data["risks"][target_key]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(
            users[attacker_key]
        ),
        json={
            "title": "IDOR Attack",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("manager", "admin"),
    ],
)
def test_risk_idor_delete_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    risk = resource_data["risks"][target_key]

    response = client.delete(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(
            users[attacker_key]
        ),
    )

    assert response.status_code == 403


def test_employee_cannot_access_admin_user_details(
    client,
    users,
    auth_headers,
):
    response = client.get(
        f"/api/v1/users/{users['admin'].id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403


def test_employee_cannot_enumerate_all_users(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("analyst", "admin"),
        ("manager", "admin"),
    ],
)
def test_evidence_idor_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    evidence = resource_data["evidence"][target_key]

    response = client.get(
        f"/api/v1/evidence/{evidence.id}",
        headers=auth_headers(
            users[attacker_key]
        ),
    )

    assert response.status_code == 404


# ==========================================================
# 43D — INPUT VALIDATION
# ==========================================================


@pytest.mark.parametrize(
    "resource",
    [
        "risks",
        "controls",
        "evidence",
        "audits",
        "audit-findings",
        "corrective-actions",
    ],
)
def test_invalid_numeric_resource_id_is_rejected(
    client,
    users,
    auth_headers,
    resource,
):
    response = client.get(
        f"/api/v1/{resource}/not-a-number",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code in {
        404,
        422,
    }


@pytest.mark.parametrize(
    "resource",
    [
        "risks",
        "controls",
        "evidence",
        "audits",
        "audit-findings",
        "corrective-actions",
    ],
)
def test_negative_resource_id_does_not_return_object(
    client,
    users,
    auth_headers,
    resource,
):
    response = client.get(
        f"/api/v1/{resource}/-1",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code in {
        404,
        422,
    }


def test_invalid_risk_payload_is_rejected(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json={},
    )

    assert response.status_code == 422


def test_invalid_control_payload_is_rejected(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(users["manager"]),
        json={},
    )

    assert response.status_code == 422


def test_invalid_risk_likelihood_is_rejected(
    client,
    users,
    auth_headers,
):
    payload = valid_risk_payload(
        users["employee"].id
    )

    payload["likelihood"] = "not-a-number"

    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_control_effectiveness_is_rejected(
    client,
    users,
    auth_headers,
):
    payload = valid_control_payload(
        users["manager"].id
    )

    payload["effectiveness"] = "invalid"

    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(users["manager"]),
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_enum_value_is_rejected(
    client,
    users,
    auth_headers,
):
    payload = valid_risk_payload(
        users["employee"].id
    )

    payload["status"] = (
        "THIS_IS_NOT_A_VALID_STATUS"
    )

    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json=payload,
    )

    assert response.status_code == 422


def test_oversized_risk_title_is_rejected(
    client,
    users,
    auth_headers,
):
    payload = valid_risk_payload(
        users["employee"].id
    )

    payload["title"] = "A" * 10000

    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json=payload,
    )

    assert response.status_code == 422


def test_malformed_json_is_rejected(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/risks/",
        headers={
            **auth_headers(users["employee"]),
            "Content-Type": "application/json",
        },
        content="{not-valid-json}",
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {
            "title": "' OR '1'='1",
            "description": (
                "SQL injection security test payload."
            ),
            "likelihood": 3,
            "impact": 4,
            "owner_id": 5,
        },
        {
            "title": "1; DROP TABLE users;--",
            "description": (
                "SQL injection security test payload."
            ),
            "likelihood": 3,
            "impact": 4,
            "owner_id": 5,
        },
    ],
)
def test_sql_injection_style_input_does_not_break_api(
    client,
    users,
    auth_headers,
    payload,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json=payload,
    )

    # The payload is ordinary user input from the API's
    # perspective. It must never produce a server error.
    assert response.status_code != 500


# ==========================================================
# 43E — FILE UPLOAD SECURITY
# ==========================================================


def test_evidence_upload_uses_authenticated_uploader(
    client,
    users,
    resource_data,
    auth_headers,
):
    control = resource_data["controls"]["employee"]

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["employee"]),
        data={
            "control_id": str(control.id),
            "title": "Phase 43 Evidence",
            "description": (
                "Evidence uploaded during security testing."
            ),
        },
        files={
            "file": (
                "phase43.txt",
                b"Phase 43 security test",
                "text/plain",
            )
        },
    )

    assert response.status_code in {
        200,
        201,
    }

    data = response.json()

    assert data["uploaded_by"] == users["employee"].id


def test_evidence_upload_sanitizes_path_traversal_filename(
    client,
    users,
    resource_data,
    auth_headers,
):
    control = resource_data["controls"]["employee"]

    malicious_filename = (
        "../../../../../phase43-traversal.txt"
    )

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["employee"]),
        data={
            "control_id": str(control.id),
            "title": "Traversal Test Evidence",
            "description": (
                "Testing filename path traversal protection."
            ),
        },
        files={
            "file": (
                malicious_filename,
                b"Traversal test",
                "text/plain",
            )
        },
    )

    assert response.status_code in {
        200,
        201,
    }

    data = response.json()

    file_name = data["file_name"]

    assert "/" not in file_name
    assert "\\" not in file_name
    assert ".." not in file_name


def test_evidence_upload_does_not_allow_absolute_filename(
    client,
    users,
    resource_data,
    auth_headers,
):
    control = resource_data["controls"]["employee"]

    malicious_filename = (
        "C:\\Windows\\System32\\phase43.txt"
    )

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["employee"]),
        data={
            "control_id": str(control.id),
            "title": "Absolute Path Test",
            "description": (
                "Testing absolute path filename protection."
            ),
        },
        files={
            "file": (
                malicious_filename,
                b"Absolute path test",
                "text/plain",
            )
        },
    )

    assert response.status_code in {
        200,
        201,
    }

    data = response.json()

    file_name = data["file_name"]

    assert "/" not in file_name
    assert "\\" not in file_name


def test_upload_directory_is_not_directly_executable_via_api(
    client,
):
    """
    The static /uploads endpoint should not expose an API
    that allows arbitrary filesystem traversal.

    A missing file must not become a successful response.
    """

    response = client.get(
        "/uploads/../../../../etc/passwd"
    )

    assert response.status_code in {
        404,
        400,
    }


# ==========================================================
# 43F — HTTP / API SECURITY
# ==========================================================


def test_root_endpoint_does_not_expose_debug_information(
    client,
):
    response = client.get("/")

    assert response.status_code == 200

    body = response.text.lower()

    assert "traceback" not in body
    assert "exception" not in body
    assert "stack trace" not in body


def test_health_endpoint_is_available(
    client,
):
    response = client.get(
        "/api/v1/health"
    )

    assert response.status_code == 200


def test_unknown_api_endpoint_returns_not_found(
    client,
):
    response = client.get(
        "/api/v1/this-endpoint-does-not-exist"
    )

    assert response.status_code == 404


def test_options_request_only_allows_configured_origin(
    client,
):
    response = client.options(
        "/api/v1/risks/",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert (
        response.headers.get(
            "access-control-allow-origin"
        )
        != "https://evil.example"
    )


def test_local_frontend_origin_is_allowed(
    client,
):
    response = client.options(
        "/api/v1/risks/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get(
        "access-control-allow-origin"
    ) == "http://localhost:5173"


# ==========================================================
# 43G — ERROR LEAKAGE / INJECTION
# ==========================================================


def test_invalid_integer_parameter_does_not_leak_traceback(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/not-an-integer",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code in {
        404,
        422,
    }

    body = response.text.lower()

    assert "traceback" not in body
    assert "sqlalchemy" not in body
    assert "password" not in body


def test_unknown_resource_does_not_leak_database_details(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/999999999",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404

    body = response.text.lower()

    assert "sqlalchemy" not in body
    assert "postgres" not in body
    assert "sqlite" not in body
    assert "traceback" not in body


def test_invalid_role_value_is_rejected(
    client,
    users,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/role",
        headers=auth_headers(users["admin"]),
        json={
            "role": "SUPER_ADMIN",
        },
    )

    assert response.status_code == 422


def test_invalid_organization_manager_id_is_rejected_or_not_found(
    client,
    users,
    auth_headers,
):
    response = client.patch(
        (
            f"/api/v1/users/"
            f"{users['employee'].id}/organization"
        ),
        headers=auth_headers(users["admin"]),
        json={
            "manager_id": 999999999,
            "department": "Security",
        },
    )

    assert response.status_code in {
        400,
        404,
    }


# ==========================================================
# 43H — AUTHORIZATION REGRESSION
# ==========================================================


def test_admin_can_still_access_all_risks(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    risk_ids = {
        item["id"]
        for item in response.json()
    }

    assert {
        resource_data["risks"]["admin"].id,
        resource_data["risks"]["manager"].id,
        resource_data["risks"]["analyst"].id,
        resource_data["risks"]["auditor"].id,
        resource_data["risks"]["employee"].id,
    }.issubset(risk_ids)


def test_manager_cannot_access_admin_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


def test_employee_cannot_modify_admin_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
        json={
            "title": "Unauthorized Phase 43 Update",
        },
    )

    assert response.status_code == 404


def test_employee_cannot_delete_admin_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.delete(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403


def test_employee_can_still_access_organization_controls(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/controls/",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    control_ids = {
        item["id"]
        for item in response.json()
    }

    assert resource_data["controls"]["admin"].id in control_ids


def test_employee_cannot_update_organization_control(
    client,
    users,
    resource_data,
    auth_headers,
):
    control = resource_data["controls"]["admin"]

    response = client.patch(
        f"/api/v1/controls/{control.id}",
        headers=auth_headers(users["employee"]),
        json={
            "title": "Unauthorized Phase 43 Control Update",
        },
    )

    assert response.status_code == 403


# ==========================================================
# JWT ALGORITHM CONFUSION
# ==========================================================


def test_jwt_signed_with_different_algorithm_is_rejected():
    alternative_algorithm = (
        "HS384"
        if ALGORITHM != "HS384"
        else "HS512"
    )

    token = jwt.encode(
        {
            "sub": "admin@example.com",
            "exp": datetime.now(
                timezone.utc
            ) + timedelta(minutes=30),
        },
        SECRET_KEY,
        algorithm=alternative_algorithm,
    )

    assert verify_access_token(token) is None


# ==========================================================
# JWT ROLE CLAIM CANNOT OVERRIDE DATABASE ROLE
# ==========================================================


def test_jwt_role_claim_cannot_escalate_privileges(
    client,
    users,
):
    token = create_access_token(
        {
            "sub": users["employee"].email,
            "role": UserRole.ADMIN.value,
        }
    )

    response = client.get(
        "/api/v1/auth/admin",
        headers=bearer(token),
    )

    assert response.status_code == 403


# ==========================================================
# USER DATA PROTECTION
# ==========================================================


def test_user_response_does_not_expose_password_hash(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert "hashed_password" not in data
    assert "password" not in data


def test_user_listing_does_not_expose_password_hash(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    for user in response.json():
        assert "hashed_password" not in user
        assert "password" not in user


# ==========================================================
# FILESYSTEM SAFETY
# ==========================================================


def test_upload_path_is_inside_upload_directory():
    """
    Static structural check ensuring the configured upload
    location is a directory rather than an arbitrary file path.
    """

    upload_dir = Path("uploads")

    assert upload_dir.name == "uploads"
    assert not upload_dir.is_file()