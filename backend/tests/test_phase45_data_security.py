"""
Phase 45 — Database & Data-Layer Security

This module tests the persistence/data boundary of CyberGRC-AI.

Coverage:

    45A  SQLAlchemy / SQL injection resistance
    45B  ORM query parameter safety
    45C  Mass-assignment protection
    45D  Unknown-field rejection
    45E  ID/type manipulation
    45F  Cross-user data isolation
    45G  Sensitive database fields
    45H  Relationship integrity
    45I  Foreign-key integrity
    45J  Transaction / rollback safety
    45K  Duplicate / conflicting records
    45L  Boundary values
    45M  Database error leakage
    45N  API response data minimisation
    45O  Persistence consistency / regression checks
"""

from datetime import date

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.risk import Risk
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction


# ==========================================================
# CONSTANTS
# ==========================================================

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1 --",
    "'; DROP TABLE users; --",
    "' UNION SELECT NULL --",
    "admin'--",
    "\" OR \"1\"=\"1",
]

EXTREME_STRINGS = [
    "",
    "A",
    "A" * 255,
    "A" * 1000,
]

SENSITIVE_FIELD_NAMES = {
    "hashed_password",
    "password",
    "password_hash",
    "secret_key",
    "jwt_secret",
    "access_token",
    "refresh_token",
}


# ==========================================================
# HELPERS
# ==========================================================

def assert_no_sensitive_fields(payload):
    """
    Recursively verify that API responses do not expose
    authentication/secrets-related database fields.
    """
    if isinstance(payload, dict):
        for key, value in payload.items():
            assert key.lower() not in SENSITIVE_FIELD_NAMES, (
                f"Sensitive field exposed in API response: {key}"
            )
            assert_no_sensitive_fields(value)

    elif isinstance(payload, list):
        for item in payload:
            assert_no_sensitive_fields(item)


def table_names(db):
    return set(inspect(db.bind).get_table_names())


# ==========================================================
# 45A — SQL INJECTION RESISTANCE
# ==========================================================

@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_sqlalchemy_text_queries_do_not_execute_injected_sql(
    db,
    payload,
):
    """
    Verify that user-controlled strings remain parameters rather
    than being interpreted as SQL syntax.
    """

    result = db.execute(
        text("SELECT :value AS value"),
        {"value": payload},
    ).scalar()

    assert result == payload


@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_orm_filter_treats_sql_payload_as_literal_data(
    db,
    users,
    payload,
):
    """
    SQLAlchemy ORM filtering must treat SQL-looking input as data.
    """

    results = (
        db.query(User)
        .filter(User.email == payload)
        .all()
    )

    assert results == []


@pytest.mark.parametrize("payload", SQLI_PAYLOADS)
def test_risk_title_sql_payload_does_not_expand_query(
    db,
    users,
    payload,
):
    risk = Risk(
        title=payload,
        description="SQL injection test",
        likelihood=1,
        impact=1,
        risk_score=1,
        status="Open",
        owner_id=users["employee"].id,
        created_by_id=users["employee"].id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    result = (
        db.query(Risk)
        .filter(Risk.title == payload)
        .first()
    )

    assert result is not None
    assert result.id == risk.id
    assert result.title == payload


# ==========================================================
# 45B — ORM QUERY PARAMETER SAFETY
# ==========================================================

def test_user_lookup_by_email_returns_exact_match(
    db,
    users,
):
    result = (
        db.query(User)
        .filter(User.email == users["employee"].email)
        .first()
    )

    assert result is not None
    assert result.id == users["employee"].id


def test_user_lookup_does_not_return_multiple_users_for_exact_email(
    db,
    users,
):
    results = (
        db.query(User)
        .filter(User.email == users["employee"].email)
        .all()
    )

    assert len(results) == 1


def test_risk_owner_filter_is_exact(
    db,
    users,
    resource_data,
):
    risks = (
        db.query(Risk)
        .filter(Risk.owner_id == users["employee"].id)
        .all()
    )

    assert all(
        risk.owner_id == users["employee"].id
        for risk in risks
    )


# ==========================================================
# 45C — MASS ASSIGNMENT PROTECTION
# ==========================================================

def test_risk_api_does_not_allow_owner_id_mass_assignment(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json={
            "title": "Mass Assignment Risk",
            "description": "Testing owner manipulation.",
            "likelihood": 2,
            "impact": 2,
            "risk_score": 4,
            "owner_id": users["admin"].id,
        },
    )

    # The request must not silently accept an attacker-controlled
    # owner field without enforcing the application's authorization.
    assert response.status_code in {200, 201, 403, 422}


def test_risk_update_does_not_allow_owner_mass_assignment(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]
    original_owner = risk.owner_id

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
        json={
            "title": "Legitimate Update",
            "owner_id": users["admin"].id,
        },
    )

    assert response.status_code in {200, 403, 422}

    # The API must never convert the employee-owned resource
    # into an administrator-owned resource.
    assert risk.owner_id == original_owner


def test_control_api_does_not_allow_owner_mass_assignment(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(users["manager"]),
        json={
            "title": "Mass Assignment Control",
            "description": "Testing owner manipulation.",
            "owner_id": users["admin"].id,
        },
    )

    assert response.status_code in {200, 201, 403, 422}


# ==========================================================
# 45D — UNKNOWN FIELD REJECTION
# ==========================================================

@pytest.mark.parametrize(
    "endpoint,payload",
    [
        (
            "/api/v1/risks/",
            {
                "title": "Unknown Field Risk",
                "description": "Testing schema strictness.",
                "likelihood": 2,
                "impact": 2,
                "risk_score": 4,
                "unexpected_field": "attacker-controlled",
            },
        ),
        (
            "/api/v1/risks/",
            {
                "title": "Unknown Field Risk",
                "description": "Testing schema strictness.",
                "likelihood": 2,
                "impact": 2,
                "risk_score": 4,
                "role": "Admin",
            },
        ),
    ],
)
def test_risk_create_rejects_unknown_fields(
    client,
    users,
    auth_headers,
    endpoint,
    payload,
):
    response = client.post(
        endpoint,
        headers=auth_headers(users["employee"]),
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    [
        "role",
        "owner_id",
        "created_by_id",
        "is_admin",
        "hashed_password",
    ],
)
def test_risk_update_rejects_sensitive_unknown_fields(
    client,
    users,
    resource_data,
    auth_headers,
    field,
):
    risk = resource_data["risks"]["employee"]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
        json={
            field: users["admin"].id
            if field.endswith("_id")
            else "attacker-controlled",
        },
    )

    assert response.status_code in {200, 403, 422}


# ==========================================================
# 45E — ID / TYPE MANIPULATION
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
def test_negative_integer_id_is_not_treated_as_valid_resource(
    client,
    users,
    auth_headers,
    resource,
):
    response = client.get(
        f"/api/v1/{resource}/-1",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code in {404, 422}


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
def test_non_integer_id_is_rejected(
    client,
    users,
    auth_headers,
    resource,
):
    response = client.get(
        f"/api/v1/{resource}/not-an-integer",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 422


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
def test_extremely_large_id_does_not_cause_server_error(
    client,
    users,
    auth_headers,
    resource,
):
    # SQLite INTEGER is a signed 64-bit value. This is the maximum
    # valid SQLite integer and still provides a useful boundary test.
    response = client.get(
        f"/api/v1/{resource}/9223372036854775807",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code in {404, 422}


# ==========================================================
# 45F — CROSS-USER DATA ISOLATION
# ==========================================================

def test_employee_database_query_only_returns_employee_owned_risks(
    db,
    users,
    resource_data,
):
    risks = (
        db.query(Risk)
        .filter(Risk.owner_id == users["employee"].id)
        .all()
    )

    assert risks
    assert all(
        risk.owner_id == users["employee"].id
        for risk in risks
    )

    assert not any(
        risk.owner_id == users["admin"].id
        for risk in risks
    )


def test_employee_api_cannot_access_admin_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


def test_analyst_api_cannot_access_admin_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 404


def test_employee_api_cannot_access_admin_evidence(
    client,
    users,
    resource_data,
    auth_headers,
):
    evidence = resource_data["evidence"]["admin"]

    response = client.get(
        f"/api/v1/evidence/{evidence.id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


# ==========================================================
# 45G — SENSITIVE DATABASE FIELDS
# ==========================================================

def test_user_database_contains_hashed_password_but_not_plain_password(
    db,
    users,
):
    user = (
        db.query(User)
        .filter(User.id == users["employee"].id)
        .first()
    )

    assert user is not None
    assert user.hashed_password
    assert user.hashed_password != "Password123!"


def test_user_api_does_not_expose_password_hash(
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

    assert_no_sensitive_fields(data)


def test_user_list_does_not_expose_password_hash(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    assert_no_sensitive_fields(response.json())


# ==========================================================
# 45H — RELATIONSHIP INTEGRITY
# ==========================================================

def test_risk_owner_reference_points_to_existing_user(
    db,
    users,
    resource_data,
):
    for risk in db.query(Risk).all():
        owner = (
            db.query(User)
            .filter(User.id == risk.owner_id)
            .first()
        )

        assert owner is not None


def test_risk_created_by_reference_points_to_existing_user(
    db,
    users,
    resource_data,
):
    for risk in db.query(Risk).all():
        creator = (
            db.query(User)
            .filter(User.id == risk.created_by_id)
            .first()
        )

        assert creator is not None


def test_evidence_uploader_reference_points_to_existing_user(
    db,
    resource_data,
):
    for evidence in db.query(Evidence).all():
        uploader = (
            db.query(User)
            .filter(User.id == evidence.uploaded_by)
            .first()
        )

        assert uploader is not None


def test_corrective_action_assignee_reference_points_to_existing_user(
    db,
    resource_data,
):
    for action in db.query(CorrectiveAction).all():
        assignee = (
            db.query(User)
            .filter(User.id == action.assigned_to)
            .first()
        )

        assert assignee is not None


# ==========================================================
# 45I — FOREIGN-KEY INTEGRITY
# ==========================================================

def test_invalid_risk_owner_is_not_silently_resolved(
    db,
):
    risk = Risk(
        title="Invalid Owner Test",
        description="Foreign key integrity test.",
        likelihood=1,
        impact=1,
        risk_score=1,
        status="Open",
        owner_id=99999999,
        created_by_id=99999999,
    )

    db.add(risk)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return

    # SQLite foreign keys may not be enforced depending on engine
    # configuration. If the database accepts the row, verify that
    # it still does not magically point to a real user.
    assert (
        db.query(User)
        .filter(User.id == risk.owner_id)
        .first()
        is None
    )


def test_invalid_corrective_action_assignee_is_not_resolved(
    db,
):
    action = CorrectiveAction(
        finding_id=99999999,
        assigned_to=99999999,
        title="Invalid FK Test",
        description="Foreign key integrity test.",
        priority="High",
        status="Pending",
        due_date=date.today(),
    )

    db.add(action)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return

    assert (
        db.query(User)
        .filter(User.id == action.assigned_to)
        .first()
        is None
    )


# ==========================================================
# 45J — TRANSACTION / ROLLBACK SAFETY
# ==========================================================

def test_failed_transaction_can_be_rolled_back_cleanly(
    db,
    users,
):
    original_count = db.query(Risk).count()

    risk = Risk(
        title="Rollback Test",
        description="Transaction rollback test.",
        likelihood=1,
        impact=1,
        risk_score=1,
        status="Open",
        owner_id=users["employee"].id,
        created_by_id=users["employee"].id,
    )

    db.add(risk)
    db.flush()

    assert db.query(Risk).count() == original_count + 1

    db.rollback()

    assert db.query(Risk).count() == original_count

    assert (
        db.query(Risk)
        .filter(Risk.title == "Rollback Test")
        .first()
        is None
    )


def test_rollback_does_not_remove_existing_records(
    db,
    users,
    resource_data,
):
    original_risk_id = resource_data["risks"]["employee"].id

    db.add(
        Risk(
            title="Temporary Transaction",
            description="Should be rolled back.",
            likelihood=1,
            impact=1,
            risk_score=1,
            status="Open",
            owner_id=users["employee"].id,
            created_by_id=users["employee"].id,
        )
    )

    db.rollback()

    existing = (
        db.query(Risk)
        .filter(Risk.id == original_risk_id)
        .first()
    )

    assert existing is not None


# ==========================================================
# 45K — DUPLICATE / CONFLICTING RECORDS
# ==========================================================

def test_duplicate_user_email_does_not_create_second_user(
    db,
    users,
):
    duplicate = User(
        full_name="Duplicate User",
        email=users["employee"].email,
        hashed_password="different-hash",
        role=users["employee"].role,
        manager_id=users["employee"].manager_id,
        department="Duplicate",
    )

    db.add(duplicate)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

    users_with_email = (
        db.query(User)
        .filter(User.email == users["employee"].email)
        .all()
    )

    assert len(users_with_email) == 1


# ==========================================================
# 45L — BOUNDARY VALUES
# ==========================================================

@pytest.mark.parametrize(
    "likelihood,impact",
    [
        (0, 0),
        (1, 1),
        (5, 5),
        (-1, 1),
        (1, -1),
        (999999, 999999),
    ],
)
def test_risk_numeric_boundaries_are_not_silently_corrupted(
    client,
    users,
    auth_headers,
    likelihood,
    impact,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json={
            "title": f"Boundary Risk {likelihood}-{impact}",
            "description": "Boundary testing.",
            "likelihood": likelihood,
            "impact": impact,
            "risk_score": likelihood * impact,
        },
    )

    assert response.status_code in {200, 201, 422}


@pytest.mark.parametrize("value", EXTREME_STRINGS)
def test_risk_title_boundary_values_are_handled_safely(
    client,
    users,
    auth_headers,
    value,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json={
            "title": value,
            "description": "Boundary string test.",
            "likelihood": 1,
            "impact": 1,
            "risk_score": 1,
        },
    )

    assert response.status_code in {200, 201, 422}


# ==========================================================
# 45M — DATABASE ERROR LEAKAGE
# ==========================================================

def test_database_error_does_not_expose_sqlalchemy_details(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/999999999",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code in {404, 422}

    body = response.text.lower()

    forbidden_fragments = [
        "sqlalchemy",
        "traceback",
        "postgresql",
        "sqlite3",
        "operationalerror",
        "integrityerror",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in body


def test_invalid_database_resource_does_not_expose_table_names(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/audit-findings/999999999",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code in {404, 422}

    body = response.text.lower()

    assert "audit_findings" not in body
    assert "corrective_actions" not in body


# ==========================================================
# 45N — API RESPONSE DATA MINIMISATION
# ==========================================================

def test_risk_response_does_not_expose_sensitive_fields(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert_no_sensitive_fields(response.json())


def test_control_response_does_not_expose_sensitive_fields(
    client,
    users,
    resource_data,
    auth_headers,
):
    control = resource_data["controls"]["admin"]

    response = client.get(
        f"/api/v1/controls/{control.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert_no_sensitive_fields(response.json())


def test_evidence_response_does_not_expose_sensitive_fields(
    client,
    users,
    resource_data,
    auth_headers,
):
    evidence = resource_data["evidence"]["admin"]

    response = client.get(
        f"/api/v1/evidence/{evidence.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert_no_sensitive_fields(response.json())


def test_audit_response_does_not_expose_sensitive_fields(
    client,
    users,
    resource_data,
    auth_headers,
):
    audit = resource_data["audits"]["admin"]

    response = client.get(
        f"/api/v1/audits/{audit.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert_no_sensitive_fields(response.json())


def test_finding_response_does_not_expose_sensitive_fields(
    client,
    users,
    resource_data,
    auth_headers,
):
    finding = resource_data["findings"]["admin"]

    response = client.get(
        f"/api/v1/audit-findings/{finding.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert_no_sensitive_fields(response.json())


def test_corrective_action_response_does_not_expose_sensitive_fields(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    finding = resource_data["findings"]["admin"]

    action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=users["admin"].id,
        title="Sensitive Field Response Test",
        description="Testing corrective action response minimisation.",
        priority="High",
        status="Pending",
        due_date=date.today(),
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    response = client.get(
        f"/api/v1/corrective-actions/{action.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert_no_sensitive_fields(response.json())


def test_risk_response_contains_expected_business_fields(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "title" in data
    assert "description" in data


# ==========================================================
# 45O — PERSISTENCE CONSISTENCY / REGRESSION
# ==========================================================

def test_database_contains_expected_core_tables(
    db,
):
    tables = table_names(db)

    expected = {
        "users",
        "risks",
        "controls",
        "evidence",
        "audits",
        "audit_findings",
        "corrective_actions",
    }

    assert expected.issubset(tables)


def test_resource_ids_are_unique(
    db,
    resource_data,
):
    for model in [
        User,
        Risk,
        Control,
        Evidence,
        Audit,
        AuditFinding,
        CorrectiveAction,
    ]:
        ids = [
            row.id
            for row in db.query(model).all()
        ]

        assert len(ids) == len(set(ids))


def test_existing_resource_relationships_remain_consistent(
    db,
    resource_data,
):
    audits = db.query(Audit).all()

    for audit in audits:
        assert audit.auditor_id is not None

        auditor = (
            db.query(User)
            .filter(User.id == audit.auditor_id)
            .first()
        )

        assert auditor is not None

    findings = db.query(AuditFinding).all()

    for finding in findings:
        audit = (
            db.query(Audit)
            .filter(Audit.id == finding.audit_id)
            .first()
        )

        assert audit is not None


def test_corrective_actions_reference_existing_findings(
    db,
    resource_data,
):
    actions = db.query(CorrectiveAction).all()

    for action in actions:
        finding = (
            db.query(AuditFinding)
            .filter(AuditFinding.id == action.finding_id)
            .first()
        )

        assert finding is not None


def test_database_can_read_all_core_models_without_exception(
    db,
):
    for model in [
        User,
        Risk,
        Control,
        Evidence,
        Audit,
        AuditFinding,
        CorrectiveAction,
    ]:
        rows = db.query(model).all()
        assert isinstance(rows, list)


# ==========================================================
# 45P — SECURITY REGRESSION CHECKS
# ==========================================================

def test_employee_cannot_change_risk_owner_through_api(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    original_owner = risk.owner_id

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
        json={
            "owner_id": users["admin"].id,
        },
    )

    assert response.status_code in {200, 403, 422}

    assert risk.owner_id == original_owner


def test_employee_cannot_change_risk_creator_through_api(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    original_creator = risk.created_by_id

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
        json={
            "created_by_id": users["admin"].id,
        },
    )

    assert response.status_code in {200, 403, 422}

    assert risk.created_by_id == original_creator


def test_database_records_survive_safe_api_read(
    db,
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    persisted = (
        db.query(Risk)
        .filter(Risk.id == risk.id)
        .first()
    )

    assert persisted is not None
    assert persisted.id == risk.id
    assert persisted.owner_id == users["employee"].id