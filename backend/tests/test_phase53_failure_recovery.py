from datetime import date, timedelta
from io import BytesIO

import pytest

from app.models.audit import Audit
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence


def _json(response):
    return response.json()


def _headers(auth_headers, user):
    return auth_headers(user)


def _create_framework(client, headers):
    response = client.post(
        "/api/v1/frameworks/",
        headers=headers,
        json={
            "name": "Phase 53.5 Recovery Framework",
            "version": "1.0",
            "description": "Framework for failure and recovery validation.",
        },
    )
    assert response.status_code == 200
    return _json(response)["id"]


def _create_control(client, headers, manager):
    response = client.post(
        "/api/v1/controls/",
        headers=headers,
        json={
            "title": "Phase 53.5 Recovery Control",
            "description": "Control used for failure and recovery validation.",
            "control_type": "Preventive",
            "status": "Active",
            "effectiveness": 80,
            "owner_id": manager.id,
        },
    )
    assert response.status_code == 200
    return _json(response)["id"]


def _create_audit(client, headers, manager, framework_id):
    start_date = date.today()
    end_date = start_date + timedelta(days=30)

    response = client.post(
        "/api/v1/audits/",
        headers=headers,
        json={
            "name": "Phase 53.5 Recovery Audit",
            "framework_id": framework_id,
            "auditor_id": manager.id,
            "scope": "Failure and recovery validation",
            "status": "In Progress",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
    )
    assert response.status_code == 200
    return _json(response)


def _create_finding(client, headers, audit_id, control_id):
    response = client.post(
        "/api/v1/audit-findings/",
        headers=headers,
        json={
            "audit_id": audit_id,
            "control_id": control_id,
            "title": "Phase 53.5 Recovery Finding",
            "description": "Finding used for failure and recovery validation.",
            "severity": "High",
            "recommendation": "Complete the required corrective workflow and retain evidence.",
            "status": "Open",
        },
    )
    assert response.status_code == 200
    return _json(response)["id"]


def test_phase53_failure_recovery_and_transaction_safety(
    client,
    db,
    users,
    auth_headers,
    monkeypatch,
    tmp_path,
):
    """Verify rejected operations leave no unintended state and later recovery succeeds."""

    manager = users["manager"]
    headers = _headers(auth_headers, manager)

    framework_id = _create_framework(client, headers)
    control_id = _create_control(client, headers, manager)
    audit = _create_audit(client, headers, manager, framework_id)

    # ---------------------------------------------------------
    # 1. INVALID AUDIT CREATION MUST NOT PERSIST
    # ---------------------------------------------------------

    invalid_audit_response = client.post(
        "/api/v1/audits/",
        headers=headers,
        json={
            "name": "Phase 53.5 Invalid Audit",
            "framework_id": framework_id,
            "auditor_id": manager.id,
            "scope": "Invalid audit date validation",
            "status": "Planned",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )

    assert invalid_audit_response.status_code == 422

    persisted_invalid_audit = (
        db.query(Audit)
        .filter(Audit.name == "Phase 53.5 Invalid Audit")
        .first()
    )
    assert persisted_invalid_audit is None

    # ---------------------------------------------------------
    # 2. INVALID AUDIT UPDATE MUST ROLLBACK
    # ---------------------------------------------------------

    original_end_date = audit["end_date"]
    invalid_end_date = date.today() - timedelta(days=1)

    invalid_update_response = client.patch(
        f"/api/v1/audits/{audit['id']}",
        headers=headers,
        json={
            "end_date": invalid_end_date.isoformat(),
        },
    )

    assert invalid_update_response.status_code == 400

    db.rollback()

    unchanged_audit = (
        db.query(Audit)
        .filter(Audit.id == audit["id"])
        .first()
    )
    assert unchanged_audit is not None
    assert unchanged_audit.end_date.isoformat() == original_end_date

    # ---------------------------------------------------------
    # 3. VALID AUDIT UPDATE MUST RECOVER SUCCESSFULLY
    # ---------------------------------------------------------

    valid_end_date = date.today() + timedelta(days=45)

    valid_update_response = client.patch(
        f"/api/v1/audits/{audit['id']}",
        headers=headers,
        json={
            "end_date": valid_end_date.isoformat(),
        },
    )

    assert valid_update_response.status_code == 200
    assert _json(valid_update_response)["end_date"] == valid_end_date.isoformat()

    # ---------------------------------------------------------
    # 4. CREATE FINDING + CORRECTIVE ACTION
    # ---------------------------------------------------------

    finding_id = _create_finding(
        client,
        headers,
        audit["id"],
        control_id,
    )

    original_due_date = date.today() + timedelta(days=5)

    action_response = client.post(
        "/api/v1/corrective-actions/",
        headers=headers,
        json={
            "finding_id": finding_id,
            "assigned_to": manager.id,
            "title": "Phase 53.5 Recovery Action",
            "description": "Corrective action used for failure and recovery validation.",
            "priority": "High",
            "status": "Open",
            "due_date": original_due_date.isoformat(),
            "completed_at": original_due_date.isoformat(),
            "comments": "Initial valid action state.",
        },
    )

    assert action_response.status_code == 200
    action_id = _json(action_response)["id"]

    # ---------------------------------------------------------
    # 5. INVALID CORRECTIVE-ACTION UPDATE MUST ROLLBACK
    # ---------------------------------------------------------

    invalid_due_date = original_due_date + timedelta(days=10)

    invalid_action_response = client.patch(
        f"/api/v1/corrective-actions/{action_id}",
        headers=headers,
        json={
            "due_date": invalid_due_date.isoformat(),
        },
    )

    assert invalid_action_response.status_code == 400

    db.rollback()

    unchanged_action = (
        db.query(CorrectiveAction)
        .filter(CorrectiveAction.id == action_id)
        .first()
    )

    assert unchanged_action is not None
    assert unchanged_action.due_date == original_due_date
    assert unchanged_action.completed_at == original_due_date

    # ---------------------------------------------------------
    # 6. VALID CORRECTIVE-ACTION UPDATE MUST RECOVER
    # ---------------------------------------------------------

    recovered_due_date = original_due_date + timedelta(days=2)
    recovered_completed_at = recovered_due_date

    valid_action_response = client.patch(
        f"/api/v1/corrective-actions/{action_id}",
        headers=headers,
        json={
            "due_date": recovered_due_date.isoformat(),
            "completed_at": recovered_completed_at.isoformat(),
            "status": "Completed",
        },
    )

    assert valid_action_response.status_code == 200

    recovered_action = _json(valid_action_response)
    assert recovered_action["due_date"] == recovered_due_date.isoformat()
    assert recovered_action["completed_at"] == recovered_completed_at.isoformat()
    assert recovered_action["status"] == "Completed"

    # ---------------------------------------------------------
    # 7. OVERSIZED EVIDENCE MUST CLEAN UP FILE AND DB STATE
    # ---------------------------------------------------------

    from app.api.v1.routes import evidence as evidence_route

    monkeypatch.setattr(
        evidence_route,
        "UPLOAD_DIR",
        tmp_path,
    )

    original_max_upload_size = evidence_route.MAX_UPLOAD_SIZE_BYTES
    monkeypatch.setattr(
        evidence_route,
        "MAX_UPLOAD_SIZE_BYTES",
        10,
    )

    oversized_response = client.post(
        "/api/v1/evidence/",
        headers=headers,
        data={
            "control_id": str(control_id),
            "title": "Phase 53.5 Oversized Evidence",
            "description": "Evidence upload that must be rejected and cleaned up.",
        },
        files={
            "file": (
                "phase535-oversized.pdf",
                BytesIO(b"12345678901"),
                "application/pdf",
            )
        },
    )

    assert oversized_response.status_code == 413
    assert list(tmp_path.iterdir()) == []

    persisted_oversized_evidence = (
        db.query(Evidence)
        .filter(Evidence.title == "Phase 53.5 Oversized Evidence")
        .first()
    )
    assert persisted_oversized_evidence is None

    # Restore normal limit before recovery upload.
    monkeypatch.setattr(
        evidence_route,
        "MAX_UPLOAD_SIZE_BYTES",
        original_max_upload_size,
    )

    # ---------------------------------------------------------
    # 8. VALID EVIDENCE UPLOAD MUST RECOVER
    # ---------------------------------------------------------

    valid_evidence_response = client.post(
        "/api/v1/evidence/",
        headers=headers,
        data={
            "control_id": str(control_id),
            "title": "Phase 53.5 Recovery Evidence",
            "description": "Valid evidence upload after a rejected oversized upload.",
        },
        files={
            "file": (
                "phase535-recovery.pdf",
                BytesIO(b"%PDF-1.4 recovery"),
                "application/pdf",
            )
        },
    )

    assert valid_evidence_response.status_code == 200

    valid_evidence = _json(valid_evidence_response)
    assert valid_evidence["file_name"] == "phase535-recovery.pdf"

    stored_files = list(tmp_path.iterdir())
    assert len(stored_files) == 1
    assert stored_files[0].suffix == ".pdf"

    persisted_recovery_evidence = (
        db.query(Evidence)
        .filter(Evidence.id == valid_evidence["id"])
        .first()
    )
    assert persisted_recovery_evidence is not None
    assert persisted_recovery_evidence.file_name == "phase535-recovery.pdf"
