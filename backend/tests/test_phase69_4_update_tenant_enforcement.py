"""
Phase 69.4 — Tenant-Aware Update & Ownership Enforcement

Security goals:
    - organization_id is immutable
    - cross-tenant ownership changes are blocked
    - cross-tenant parent relationships are blocked
    - resources cannot be moved between organizations
    - legitimate same-tenant updates continue to work
"""

from datetime import date

from app.models.organization import Organization
from app.models.risk import Risk
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.user import User


# ==========================================================
# HELPERS
# ==========================================================


def create_second_organization(db, users):
    foreign_org = Organization(
        name="Phase 69.4 Foreign Organization",
        slug="phase-69-4-foreign-organization",
        is_active=True,
    )

    db.add(foreign_org)
    db.commit()
    db.refresh(foreign_org)

    foreign_admin = User(
        email="phase69_4_foreign_admin@example.com",
        full_name="Phase 69.4 Foreign Admin",
        role="Admin",
        organization_id=foreign_org.id,
    )

    # Preserve the password fields expected by the current User model.
    foreign_admin.hashed_password = "test-password"

    db.add(foreign_admin)
    db.commit()
    db.refresh(foreign_admin)

    return foreign_org, foreign_admin


def add_foreign_resources(
    db,
    foreign_org,
    foreign_admin,
    resource_data,
):
    foreign_risk = Risk(
        title="Foreign Tenant Risk",
        description="Risk belonging to another organization.",
        likelihood=3,
        impact=3,
        risk_score=9,
        status="Open",
        owner_id=foreign_admin.id,
        created_by_id=foreign_admin.id,
        organization_id=foreign_org.id,
    )

    foreign_control = Control(
        title="Foreign Tenant Control",
        description="Control belonging to another organization.",
        control_type="Preventive",
        status="Active",
        effectiveness=80,
        owner_id=foreign_admin.id,
        created_by_id=foreign_admin.id,
        organization_id=foreign_org.id,
    )

    db.add_all(
        [
            foreign_risk,
            foreign_control,
        ]
    )
    db.commit()

    db.refresh(foreign_risk)
    db.refresh(foreign_control)

    foreign_evidence = Evidence(
        title="Foreign Tenant Evidence",
        description="Evidence belonging to another organization.",
        control_id=foreign_control.id,
        file_name="foreign.pdf",
        file_path="/tmp/foreign.pdf",
        uploaded_by=foreign_admin.id,
        organization_id=foreign_org.id,
    )

    db.add(foreign_evidence)
    db.commit()
    db.refresh(foreign_evidence)

    framework_id = resource_data["audits"]["admin"].framework_id

    foreign_audit = Audit(
        name="Foreign Tenant Audit",
        framework_id=framework_id,
        auditor_id=foreign_admin.id,
        created_by_id=foreign_admin.id,
        scope="Foreign tenant audit scope",
        status="Planned",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 31),
        organization_id=foreign_org.id,
    )

    db.add(foreign_audit)
    db.commit()
    db.refresh(foreign_audit)

    foreign_finding = AuditFinding(
        audit_id=foreign_audit.id,
        control_id=foreign_control.id,
        title="Foreign Tenant Finding",
        description="Finding belonging to another organization.",
        severity="High",
        recommendation="Resolve the foreign tenant finding.",
        status="Open",
        organization_id=foreign_org.id,
    )

    db.add(foreign_finding)
    db.commit()
    db.refresh(foreign_finding)

    foreign_action = CorrectiveAction(
        finding_id=foreign_finding.id,
        assigned_to=foreign_admin.id,
        title="Foreign Tenant Action",
        description="Corrective action belonging to another organization.",
        priority="High",
        status="Open",
        due_date=date(2026, 11, 1),
        organization_id=foreign_org.id,
    )

    db.add(foreign_action)
    db.commit()
    db.refresh(foreign_action)

    return {
        "risk": foreign_risk,
        "control": foreign_control,
        "evidence": foreign_evidence,
        "audit": foreign_audit,
        "finding": foreign_finding,
        "action": foreign_action,
    }


# ==========================================================
# 1. ORGANIZATION ID MUST BE IMMUTABLE
# ==========================================================


def test_risk_organization_id_cannot_be_changed(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    risk = resource_data["risks"]["admin"]
    risk.organization_id = admin.organization_id
    db.commit()

    foreign_org, _ = create_second_organization(
        db,
        users,
    )

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(admin),
        json={
            "organization_id": foreign_org.id,
            "title": "Attempted Cross Tenant Risk",
        },
    )

    assert response.status_code in (200, 422)

    db.refresh(risk)

    assert risk.organization_id == admin.organization_id


# ==========================================================
# 2. RISK OWNER CANNOT BE MOVED TO ANOTHER TENANT
# ==========================================================


def test_risk_owner_cannot_be_changed_to_foreign_tenant(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_second_organization(
        db,
        users,
    )

    risk = resource_data["risks"]["admin"]
    risk.organization_id = admin.organization_id
    db.commit()

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(admin),
        json={
            "owner_id": foreign_admin.id,
        },
    )

    assert response.status_code in (403, 404)

    db.refresh(risk)

    assert risk.owner_id != foreign_admin.id
    assert risk.organization_id == admin.organization_id


# ==========================================================
# 3. CONTROL OWNER CANNOT BE MOVED TO ANOTHER TENANT
# ==========================================================


def test_control_owner_cannot_be_changed_to_foreign_tenant(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_second_organization(
        db,
        users,
    )

    control = resource_data["controls"]["admin"]
    control.organization_id = admin.organization_id
    db.commit()

    response = client.patch(
        f"/api/v1/controls/{control.id}",
        headers=auth_headers(admin),
        json={
            "owner_id": foreign_admin.id,
        },
    )

    assert response.status_code in (403, 404)

    db.refresh(control)

    assert control.owner_id != foreign_admin.id
    assert control.organization_id == admin.organization_id


# ==========================================================
# 4. AUDIT AUDITOR CANNOT BE MOVED TO ANOTHER TENANT
# ==========================================================


def test_audit_auditor_cannot_be_changed_to_foreign_tenant(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_second_organization(
        db,
        users,
    )

    audit = resource_data["audits"]["admin"]
    audit.organization_id = admin.organization_id
    db.commit()

    response = client.patch(
        f"/api/v1/audits/{audit.id}",
        headers=auth_headers(admin),
        json={
            "auditor_id": foreign_admin.id,
        },
    )

    assert response.status_code in (403, 404)

    db.refresh(audit)

    assert audit.auditor_id != foreign_admin.id
    assert audit.organization_id == admin.organization_id


# ==========================================================
# 5. FINDING CANNOT BE MOVED TO FOREIGN AUDIT
# ==========================================================


def test_finding_cannot_be_moved_to_foreign_audit(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_second_organization(
        db,
        users,
    )

    foreign = add_foreign_resources(
        db,
        foreign_org,
        foreign_admin,
        resource_data,
    )

    finding = resource_data["findings"]["admin"]
    finding.organization_id = admin.organization_id

    audit = resource_data["audits"]["admin"]
    audit.organization_id = admin.organization_id

    control = resource_data["controls"]["admin"]
    control.organization_id = admin.organization_id

    db.commit()

    response = client.patch(
        f"/api/v1/audit-findings/{finding.id}",
        headers=auth_headers(admin),
        json={
            "audit_id": foreign["audit"].id,
        },
    )

    assert response.status_code in (403, 404)

    db.refresh(finding)

    assert finding.audit_id != foreign["audit"].id
    assert finding.organization_id == admin.organization_id


# ==========================================================
# 6. FINDING CANNOT BE MOVED TO FOREIGN CONTROL
# ==========================================================


def test_finding_cannot_be_moved_to_foreign_control(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_second_organization(
        db,
        users,
    )

    foreign = add_foreign_resources(
        db,
        foreign_org,
        foreign_admin,
        resource_data,
    )

    finding = resource_data["findings"]["admin"]
    finding.organization_id = admin.organization_id

    audit = resource_data["audits"]["admin"]
    audit.organization_id = admin.organization_id

    control = resource_data["controls"]["admin"]
    control.organization_id = admin.organization_id

    db.commit()

    response = client.patch(
        f"/api/v1/audit-findings/{finding.id}",
        headers=auth_headers(admin),
        json={
            "control_id": foreign["control"].id,
        },
    )

    assert response.status_code in (403, 404)

    db.refresh(finding)

    assert finding.control_id != foreign["control"].id
    assert finding.organization_id == admin.organization_id


# ==========================================================
# 7. CORRECTIVE ACTION CANNOT BE MOVED TO FOREIGN FINDING
# ==========================================================


def test_corrective_action_cannot_be_moved_to_foreign_finding(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_second_organization(
        db,
        users,
    )

    foreign = add_foreign_resources(
        db,
        foreign_org,
        foreign_admin,
        resource_data,
    )

    action = resource_data["corrective_actions"]["admin"]
    action.organization_id = admin.organization_id

    finding = resource_data["findings"]["admin"]
    finding.organization_id = admin.organization_id

    db.commit()

    response = client.patch(
        f"/api/v1/corrective-actions/{action.id}",
        headers=auth_headers(admin),
        json={
            "finding_id": foreign["finding"].id,
        },
    )

    assert response.status_code in (403, 404)

    db.refresh(action)

    assert action.finding_id != foreign["finding"].id
    assert action.organization_id == admin.organization_id


# ==========================================================
# 8. CORRECTIVE ACTION ASSIGNEE CANNOT CROSS TENANT
# ==========================================================


def test_corrective_action_assignee_cannot_be_changed_to_foreign_tenant(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_second_organization(
        db,
        users,
    )

    action = resource_data["corrective_actions"]["admin"]
    action.organization_id = admin.organization_id
    db.commit()

    response = client.patch(
        f"/api/v1/corrective-actions/{action.id}",
        headers=auth_headers(admin),
        json={
            "assigned_to": foreign_admin.id,
        },
    )

    assert response.status_code in (403, 404)

    db.refresh(action)

    assert action.assigned_to != foreign_admin.id
    assert action.organization_id == admin.organization_id


# ==========================================================
# 9. LEGITIMATE SAME-TENANT UPDATE STILL WORKS
# ==========================================================


def test_legitimate_same_tenant_risk_update_still_works(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    risk = resource_data["risks"]["admin"]
    risk.organization_id = admin.organization_id
    db.commit()

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(admin),
        json={
            "title": "Legitimate Same Tenant Risk Update",
        },
    )

    assert response.status_code == 200

    db.refresh(risk)

    assert risk.title == "Legitimate Same Tenant Risk Update"
    assert risk.organization_id == admin.organization_id