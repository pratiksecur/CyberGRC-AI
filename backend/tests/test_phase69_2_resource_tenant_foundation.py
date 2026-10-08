from app.models.risk import Risk
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction


CORE_RESOURCES = [
    Risk,
    Control,
    Evidence,
    Audit,
    AuditFinding,
    CorrectiveAction,
]


def test_all_core_resources_have_organization_id_columns():
    for model in CORE_RESOURCES:
        assert hasattr(model, "organization_id")
        assert model.organization_id is not None


def test_resource_tenant_columns_are_indexed():
    for model in CORE_RESOURCES:
        column = model.__table__.c.organization_id

        assert column.index is True


def test_resource_tenant_columns_reference_organizations():
    for model in CORE_RESOURCES:
        column = model.__table__.c.organization_id

        foreign_keys = list(column.foreign_keys)

        assert len(foreign_keys) == 1
        assert foreign_keys[0].target_fullname == "organizations.id"


def test_fixture_resources_are_assigned_to_default_organization(
    resource_data,
):
    organization = resource_data["organization"]

    resources = [
        *resource_data["risks"].values(),
        *resource_data["controls"].values(),
        *resource_data["evidence"].values(),
        *resource_data["audits"].values(),
        *resource_data["findings"].values(),
        *resource_data["corrective_actions"].values(),
    ]

    for resource in resources:
        resource.organization_id = organization.id

    for resource in resources:
        assert resource.organization_id == organization.id