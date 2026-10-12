from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.seed.frameworks import load_catalog, seed_organization

EXPECTED_CONTROL_COUNTS = {
    "NIST CSF 2.0": 22,
    "ISO/IEC 27001:2022": 93,
    "GDPR": 31,
    "NIS2 Directive": 15,
    "DORA": 20,
}


def _count_controls(db, organization_id):
    return (
        db.query(FrameworkControl)
        .join(Framework, Framework.id == FrameworkControl.framework_id)
        .filter(Framework.organization_id == organization_id)
        .count()
    )


def test_catalog_data_fits_the_database_columns():
    catalog = load_catalog()

    assert {entry["name"] for entry in catalog} == set(EXPECTED_CONTROL_COUNTS)

    for entry in catalog:
        assert len(entry["name"]) <= 100
        assert len(entry["version"]) <= 50
        assert len(entry["description"]) >= 10
        assert len(entry["controls"]) == EXPECTED_CONTROL_COUNTS[entry["name"]]

        codes = [control["code"] for control in entry["controls"]]
        assert len(codes) == len(set(codes)), f"Duplicate codes in {entry['name']}"

        for control in entry["controls"]:
            assert 0 < len(control["code"]) <= 50
            assert 0 < len(control["title"]) <= 255
            assert control["description"].strip()


def test_seed_creates_frameworks_and_is_idempotent(db, users):
    organization_id = users["admin"].organization_id

    first = seed_organization(db, organization_id)
    db.commit()

    assert {row["status"] for row in first} == {"created"}
    assert sum(row["controls_added"] for row in first) == sum(
        EXPECTED_CONTROL_COUNTS.values()
    )
    assert _count_controls(db, organization_id) == sum(EXPECTED_CONTROL_COUNTS.values())

    second = seed_organization(db, organization_id)
    db.commit()

    assert all(row["status"].startswith("skipped") for row in second)
    assert _count_controls(db, organization_id) == sum(EXPECTED_CONTROL_COUNTS.values())


def test_merge_adds_only_missing_controls(db, users):
    organization_id = users["admin"].organization_id

    framework = Framework(
        organization_id=organization_id,
        name="DORA",
        version="custom",
        description="Existing user-created framework.",
    )
    db.add(framework)
    db.flush()

    db.add(
        FrameworkControl(
            framework_id=framework.id,
            control_code="Art. 5",
            title="User edited title",
            description="User edited description.",
        )
    )
    db.commit()

    rows = seed_organization(db, organization_id, only=["dora"], merge=True)
    db.commit()

    assert rows == [
        {
            "framework": "DORA",
            "status": "merged",
            "controls_added": EXPECTED_CONTROL_COUNTS["DORA"] - 1,
        }
    ]

    existing = (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.framework_id == framework.id,
            FrameworkControl.control_code == "Art. 5",
        )
        .one()
    )

    assert existing.title == "User edited title"
    assert db.query(Framework).filter(Framework.id == framework.id).one().version == "custom"


def test_seed_does_not_touch_other_organizations(db, users, second_organization):
    seed_organization(db, users["admin"].organization_id)
    db.commit()

    other_id = second_organization["organization"].id

    assert db.query(Framework).filter(Framework.organization_id == other_id).count() == 0