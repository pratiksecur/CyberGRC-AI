"""The audit trail: automatic entries, secrecy, access and tenant isolation."""

import json

import pytest

from app.models.audit_log import AuditLog
from app.models.control import Control

GOOD = "Password123!"
NEW = "a-brand-new-passphrase"


def _bearer(client, email, password=GOOD):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )

    assert response.status_code == 200, response.text

    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _entries(db, **filters):
    return (
        db.query(AuditLog)
        .filter_by(**filters)
        .order_by(AuditLog.id)
        .all()
    )


def _make_control(db, users):
    control = Control(
        organization_id=users["admin"].organization_id,
        title="Audit Trail Control",
        description="Control used by the audit trail tests.",
        control_type="Preventive",
        status="Active",
        effectiveness=70,
        owner_id=users["admin"].id,
        created_by_id=users["admin"].id,
    )

    db.add(control)
    db.commit()

    return control


# ----------------------------------------------------------
# Entries are written automatically
# ----------------------------------------------------------

def test_creating_a_record_is_logged(db, users):
    control = _make_control(db, users)

    entry = _entries(
        db, entity_type="controls", entity_id=str(control.id)
    )[0]

    assert entry.action == "created"
    assert entry.organization_id == users["admin"].organization_id
    assert "Audit Trail Control" in entry.summary
    assert entry.details["values"]["title"] == "Audit Trail Control"


def test_changes_record_old_and_new_values(db, users):
    control = _make_control(db, users)

    control.title = "Renamed Control"
    control.effectiveness = 95
    db.commit()

    entry = _entries(
        db,
        entity_type="controls",
        entity_id=str(control.id),
        action="updated",
    )[0]

    changes = entry.details["changes"]

    assert changes["title"] == {
        "from": "Audit Trail Control",
        "to": "Renamed Control",
    }
    assert changes["effectiveness"] == {"from": 70, "to": 95}


def test_saving_without_changes_writes_nothing(db, users):
    control = _make_control(db, users)
    before = len(_entries(db, entity_type="controls", action="updated"))

    control.title = control.title
    db.commit()

    assert len(
        _entries(db, entity_type="controls", action="updated")
    ) == before


def test_deleting_a_record_is_logged(db, users):
    control = _make_control(db, users)
    control_id = control.id

    db.delete(control)
    db.commit()

    entry = _entries(
        db,
        entity_type="controls",
        entity_id=str(control_id),
        action="deleted",
    )[0]

    assert entry.details["values"]["title"] == "Audit Trail Control"


def test_work_without_a_signed_in_user_has_no_actor(db, users):
    control = _make_control(db, users)

    entry = _entries(
        db, entity_type="controls", entity_id=str(control.id)
    )[0]

    assert entry.actor_id is None
    assert entry.actor_email is None


# ----------------------------------------------------------
# Who did it
# ----------------------------------------------------------

def test_requests_record_the_signed_in_user(client, db, users):
    admin = _bearer(client, users["admin"].email)

    response = client.post(
        "/api/v1/auth/register",
        headers=admin,
        json={
            "full_name": "Audited Person",
            "email": "audited.person@example.com",
            "password": "a-long-password",
        },
    )

    assert response.status_code == 201

    entry = _entries(
        db,
        entity_type="users",
        entity_id=str(response.json()["id"]),
        action="created",
    )[0]

    assert entry.actor_id == users["admin"].id
    assert entry.actor_email == users["admin"].email
    assert entry.ip_address
    assert entry.details["values"]["email"] == "audited.person@example.com"


def test_role_change_is_logged_with_old_and_new_role(client, db, users):
    admin = _bearer(client, users["admin"].email)
    target = users["employee"]

    response = client.patch(
        f"/api/v1/users/{target.id}/role",
        headers=admin,
        json={"role": "Risk Analyst"},
    )

    assert response.status_code == 200, response.text

    entry = _entries(
        db,
        entity_type="users",
        entity_id=str(target.id),
        action="role_changed",
    )[0]

    assert entry.details["changes"]["role"]["from"] == "Employee"
    assert entry.details["changes"]["role"]["to"] == "Risk Analyst"
    assert entry.actor_email == users["admin"].email


def test_deactivate_and_activate_are_logged(client, db, users):
    admin = _bearer(client, users["admin"].email)
    target = users["employee"]

    client.post(f"/api/v1/users/{target.id}/deactivate", headers=admin)
    client.post(f"/api/v1/users/{target.id}/activate", headers=admin)

    actions = [
        entry.action
        for entry in _entries(
            db, entity_type="users", entity_id=str(target.id)
        )
    ]

    assert "deactivated" in actions
    assert "activated" in actions


# ----------------------------------------------------------
# Secrets never reach the log
# ----------------------------------------------------------

def test_passwords_are_never_written_to_the_log(client, db, users):
    headers = _bearer(client, users["analyst"].email)

    client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": GOOD, "new_password": NEW},
    )

    admin = _bearer(client, users["admin"].email)

    client.post(
        f"/api/v1/users/{users['employee'].id}/reset-password",
        headers=admin,
        json={"new_password": "another-long-passphrase"},
    )

    changed = _entries(
        db, entity_type="users", action="password_changed"
    )

    assert len(changed) == 2

    everything = json.dumps(
        [
            [row.summary, row.details, row.actor_email]
            for row in db.query(AuditLog).all()
        ],
        default=str,
    )

    for secret in (NEW, "another-long-passphrase", GOOD, "$2b$"):
        assert secret not in everything


def test_logout_and_login_do_not_flood_the_log(client, db, users):
    headers = _bearer(client, users["analyst"].email)
    before = db.query(AuditLog).count()

    client.post("/api/v1/auth/logout", headers=headers)

    assert db.query(AuditLog).count() == before


# ----------------------------------------------------------
# Reading the trail
# ----------------------------------------------------------

@pytest.mark.parametrize(
    "role,status",
    [
        ("admin", 200),
        ("auditor", 200),
        ("manager", 403),
        ("analyst", 403),
        ("employee", 403),
    ],
)
def test_only_admins_and_auditors_can_read_it(
    client, users, auth_headers, role, status
):
    response = client.get(
        "/api/v1/audit-logs/", headers=auth_headers(users[role])
    )

    assert response.status_code == status


def test_requires_authentication(client, users):
    assert client.get("/api/v1/audit-logs/").status_code == 401


def test_listing_is_newest_first_and_paginated(
    client, db, users, auth_headers
):
    for _ in range(3):
        _make_control(db, users)

    headers = auth_headers(users["admin"])

    page = client.get(
        "/api/v1/audit-logs/",
        headers=headers,
        params={"limit": 2, "entity_type": "controls"},
    ).json()

    assert page["limit"] == 2
    assert page["offset"] == 0
    assert page["total"] >= 3
    assert len(page["items"]) == 2

    ids = [item["id"] for item in page["items"]]

    assert ids == sorted(ids, reverse=True)

    second = client.get(
        "/api/v1/audit-logs/",
        headers=headers,
        params={"limit": 2, "offset": 2, "entity_type": "controls"},
    ).json()

    assert not set(ids) & {item["id"] for item in second["items"]}


@pytest.mark.parametrize(
    "params", [{"limit": 0}, {"limit": 1000}, {"offset": -1}]
)
def test_bad_paging_values_are_rejected(
    client, users, auth_headers, params
):
    response = client.get(
        "/api/v1/audit-logs/",
        headers=auth_headers(users["admin"]),
        params=params,
    )

    assert response.status_code == 422


def test_filters_narrow_the_results(client, db, users, auth_headers):
    control = _make_control(db, users)
    control.title = "Filtered"
    db.commit()

    headers = auth_headers(users["admin"])

    updated = client.get(
        "/api/v1/audit-logs/",
        headers=headers,
        params={
            "entity_type": "controls",
            "entity_id": str(control.id),
            "action": "updated",
        },
    ).json()

    assert updated["total"] == 1
    assert updated["items"][0]["details"]["changes"]["title"]["to"] == "Filtered"

    filters = client.get(
        "/api/v1/audit-logs/filters", headers=headers
    ).json()

    assert "controls" in filters["entity_types"]
    assert "updated" in filters["actions"]


# ----------------------------------------------------------
# Tenant isolation
# ----------------------------------------------------------

def test_other_organizations_cannot_see_each_others_entries(
    client, db, users, second_organization, auth_headers
):
    _make_control(db, users)

    other = second_organization["user"]

    mine = client.get(
        "/api/v1/audit-logs/",
        headers=auth_headers(users["admin"]),
        params={"limit": 200},
    ).json()

    theirs = client.get(
        "/api/v1/audit-logs/",
        headers=auth_headers(other),
        params={"limit": 200},
    ).json()

    assert mine["total"] > 0

    organization_ids = {
        row.organization_id
        for row in db.query(AuditLog)
        .filter(AuditLog.id.in_([i["id"] for i in theirs["items"]]))
        .all()
    }

    assert organization_ids <= {other.organization_id}
    assert not {i["id"] for i in mine["items"]} & {
        i["id"] for i in theirs["items"]
    }


def test_there_is_no_way_to_change_or_delete_entries(
    client, users, auth_headers
):
    headers = auth_headers(users["admin"])

    for method in (client.put, client.patch, client.delete):
        assert method("/api/v1/audit-logs/1", headers=headers).status_code in (
            404,
            405,
        )