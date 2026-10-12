"""Controls, audits, findings, actions and evidence always have a tenant."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.framework import Framework


MODELS = [
    Control,
    Audit,
    AuditFinding,
    CorrectiveAction,
    Evidence,
]


def _control(owner_id, created_by_id, **extra):
    return Control(
        title="Tenant test control",
        description="Checks that a control always belongs to a tenant.",
        control_type="Preventive",
        status="Active",
        effectiveness=50,
        owner_id=owner_id,
        created_by_id=created_by_id,
        **extra,
    )


def _framework(db, organization_id):
    framework = Framework(
        organization_id=organization_id,
        name="Tenant Test Framework",
        version="1.0",
        description="Framework used by the tenant tests.",
    )

    db.add(framework)
    db.flush()

    return framework


def _audit(framework_id, auditor_id, created_by_id, **extra):
    return Audit(
        name="Tenant test audit",
        framework_id=framework_id,
        auditor_id=auditor_id,
        created_by_id=created_by_id,
        scope="Tenant test scope",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        **extra,
    )


def _finding(audit_id, control_id, **extra):
    return AuditFinding(
        audit_id=audit_id,
        control_id=control_id,
        title="Tenant test finding",
        description="Checks that a finding always belongs to a tenant.",
        severity="High",
        recommendation="Fix it.",
        **extra,
    )


def _action(finding_id, assigned_to, **extra):
    return CorrectiveAction(
        finding_id=finding_id,
        assigned_to=assigned_to,
        title="Tenant test action",
        description="Checks that an action always belongs to a tenant.",
        priority="High",
        due_date=date(2026, 2, 1),
        **extra,
    )


def _evidence(control_id, uploaded_by, **extra):
    return Evidence(
        control_id=control_id,
        title="Tenant test evidence",
        description="Checks that evidence always belongs to a tenant.",
        file_name="evidence.txt",
        file_path="uploads/evidence.txt",
        uploaded_by=uploaded_by,
        **extra,
    )


@pytest.mark.parametrize("model", MODELS)
def test_organization_column_is_not_nullable(model):
    assert model.__table__.c.organization_id.nullable is False


def test_control_takes_the_owners_organization(
    db, users, second_organization
):
    other = second_organization["user"]

    control = _control(other.id, users["admin"].id)

    db.add(control)
    db.commit()
    db.refresh(control)

    assert control.organization_id == second_organization["organization"].id


def test_control_falls_back_to_its_creator(db, users):
    control = _control(999999, users["analyst"].id)

    db.add(control)
    db.commit()
    db.refresh(control)

    assert control.organization_id == users["analyst"].organization_id


def test_audit_takes_the_auditors_organization(
    db, users, second_organization
):
    other = second_organization["user"]
    organization_id = second_organization["organization"].id

    framework = _framework(db, organization_id)

    audit = _audit(framework.id, other.id, users["admin"].id)

    db.add(audit)
    db.commit()
    db.refresh(audit)

    assert audit.organization_id == organization_id


def test_whole_chain_follows_the_parent_records(
    db, users, second_organization
):
    """
    Everything below is built without an organization. Each record must
    end up in the other organization, because its parent is there, even
    though the first record's creator belongs to organization 1.
    """

    other = second_organization["user"]
    organization_id = second_organization["organization"].id

    control = _control(other.id, users["admin"].id)
    db.add(control)
    db.flush()

    framework = _framework(db, organization_id)
    audit = _audit(framework.id, other.id, users["admin"].id)
    db.add(audit)
    db.flush()

    finding = _finding(audit.id, control.id)
    db.add(finding)
    db.flush()

    action = _action(finding.id, users["admin"].id)
    db.add(action)

    # Uploaded by a user of organization 1, but the control is in the
    # other organization. The control decides.
    evidence = _evidence(control.id, users["admin"].id)
    db.add(evidence)

    db.commit()

    for record in (control, audit, finding, action, evidence):
        db.refresh(record)
        assert record.organization_id == organization_id


def test_explicit_organization_is_kept(db, users):
    control = _control(
        users["analyst"].id,
        users["admin"].id,
        organization_id=users["analyst"].organization_id,
    )

    db.add(control)
    db.commit()

    assert control.organization_id == users["analyst"].organization_id


@pytest.mark.parametrize(
    "build",
    [
        lambda db, users: _control(999999, 999998),
        lambda db, users: _audit(
            _framework(db, users["admin"].organization_id).id,
            999999,
            999998,
        ),
        lambda db, users: _finding(999999, 999998),
        lambda db, users: _action(999999, 999998),
        lambda db, users: _evidence(999999, 999998),
    ],
    ids=["control", "audit", "finding", "action", "evidence"],
)
def test_record_without_a_resolvable_organization_is_rejected(
    db, users, build
):
    record = build(db, users)

    db.add(record)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()