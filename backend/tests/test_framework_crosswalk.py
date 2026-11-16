"""Cross-framework crosswalk: data, matching rules and API."""

import pytest

from app.models.control import Control
from app.models.control_framework_control import ControlFrameworkControl
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.seed.catalog.crosswalk import (
    CROSSWALK,
    NOT_IN_CROSSWALK,
    THEMES,
)
from app.seed.frameworks import load_catalog, seed_organization
from app.services.framework_crosswalk_service import (
    is_umbrella,
    link_confidence,
    themes_for,
)

ISO = "ISO/IEC 27001:2022"
NIST = "NIST CSF 2.0"
NIS2 = "NIS2 Directive"


# ----------------------------------------------------------
# The crosswalk data stays consistent with the catalogs
# ----------------------------------------------------------

def test_every_catalog_requirement_is_tagged_or_explicitly_left_out():
    for entry in load_catalog():
        name = entry["name"]
        catalog_codes = {control["code"] for control in entry["controls"]}

        tagged = set(CROSSWALK.get(name, {}))
        left_out = set(NOT_IN_CROSSWALK.get(name, ()))

        assert not tagged & left_out, f"{name}: tagged and left out"
        assert tagged | left_out == catalog_codes, (
            f"{name}: missing {sorted(catalog_codes - tagged - left_out)}, "
            f"unknown {sorted((tagged | left_out) - catalog_codes)}"
        )


def test_crosswalk_only_names_catalog_frameworks_and_known_themes():
    catalog_names = {entry["name"] for entry in load_catalog()}

    assert set(CROSSWALK) == catalog_names
    assert set(NOT_IN_CROSSWALK) <= catalog_names

    for name, requirements in CROSSWALK.items():
        for code, themes in requirements.items():
            assert themes, f"{name} {code} has no themes"
            assert len(themes) == len(set(themes)), f"{name} {code} repeats a theme"
            assert set(themes) <= set(THEMES), f"{name} {code} uses an unknown theme"


def test_every_theme_links_at_least_two_frameworks():
    for theme in THEMES:
        frameworks = {
            name
            for name, requirements in CROSSWALK.items()
            if any(theme in themes for themes in requirements.values())
        }

        assert len(frameworks) >= 2, f"Theme {theme} links nothing"


# ----------------------------------------------------------
# Matching rules
# ----------------------------------------------------------

def test_focused_requirements_with_a_shared_theme_link_directly():
    iso_crypto = themes_for(ISO, "8.24")
    nis2_crypto = themes_for(NIS2, "Art. 21(2)(h)")

    assert link_confidence(iso_crypto, nis2_crypto) == "direct"


def test_a_broad_requirement_gives_a_broad_link():
    iso_crypto = themes_for(ISO, "8.24")
    gdpr_security = themes_for("GDPR", "Art. 32")

    assert is_umbrella(gdpr_security)
    assert link_confidence(iso_crypto, gdpr_security) == "broad"


def test_requirements_without_a_shared_theme_do_not_link():
    assert link_confidence(themes_for(ISO, "8.24"), themes_for(ISO, "7.1")) is None
    assert link_confidence(themes_for("GDPR", "Art. 15"), themes_for(ISO, "5.34")) is None


def test_unknown_frameworks_and_codes_have_no_themes():
    assert themes_for("My Own Framework", "X.1") == frozenset()
    assert themes_for(ISO, "99.99") == frozenset()


# ----------------------------------------------------------
# API
# ----------------------------------------------------------

@pytest.fixture()
def catalog(db, users):
    """The five catalogs seeded into the default organization."""

    organization_id = users["admin"].organization_id

    seed_organization(db, organization_id)
    db.commit()

    def _find(framework_name, code):
        return (
            db.query(FrameworkControl)
            .join(Framework, Framework.id == FrameworkControl.framework_id)
            .filter(
                Framework.organization_id == organization_id,
                Framework.name == framework_name,
                FrameworkControl.control_code == code,
            )
            .one()
        )

    return _find


def _map(db, control, requirement):
    db.add(
        ControlFrameworkControl(
            control_id=control.id,
            framework_control_id=requirement.id,
        )
    )
    db.commit()


def _codes(items, framework_name):
    return {
        item["control_code"]
        for item in items
        if item["framework_name"] == framework_name
    }


def test_related_requirements_cross_frameworks_only(
    client, auth_headers, users, catalog
):
    logging = catalog(ISO, "8.15")

    response = client.get(
        f"/api/v1/framework-crosswalk/framework-control/{logging.id}/related",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["requirement"]["control_code"] == "8.15"
    assert body["in_crosswalk"] is True
    assert body["is_umbrella"] is False
    assert [theme["key"] for theme in body["themes"]] == ["logging-monitoring"]

    related = body["related"]

    # Never the same framework, even though 8.16 shares the theme.
    assert _codes(related, ISO) == set()
    assert "DE.CM" in _codes(related, NIST)
    assert "Art. 10" in _codes(related, "DORA")

    detection = next(item for item in related if item["control_code"] == "DE.CM")
    assert detection["confidence"] == "direct"
    assert detection["mapped_control_count"] == 0


def test_requirement_outside_the_crosswalk_has_no_related_items(
    client, auth_headers, users, catalog
):
    access_right = catalog("GDPR", "Art. 15")

    response = client.get(
        f"/api/v1/framework-crosswalk/framework-control/{access_right.id}/related",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["in_crosswalk"] is False
    assert body["related"] == []


def test_control_suggestions_follow_its_existing_mappings(
    client, auth_headers, users, resource_data, catalog, db
):
    control = resource_data["controls"]["admin"]
    crypto = catalog(ISO, "8.24")

    _map(db, control, crypto)

    response = client.get(
        f"/api/v1/framework-crosswalk/control/{control.id}/suggestions",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["mapped_requirement_count"] == 1

    suggestions = body["suggestions"]

    assert _codes(suggestions, ISO) == set()
    assert "Art. 21(2)(h)" in _codes(suggestions, NIS2)
    assert "PR.DS" in _codes(suggestions, NIST)
    assert "Art. 32" in _codes(suggestions, "GDPR")

    # Direct matches are listed before broad ones.
    confidences = [item["confidence"] for item in suggestions]
    assert confidences == sorted(confidences, key=["direct", "broad"].index)

    nis2 = next(item for item in suggestions if item["control_code"] == "Art. 21(2)(h)")
    assert nis2["confidence"] == "direct"
    assert [item["control_code"] for item in nis2["because_of"]] == ["8.24"]


def test_already_mapped_requirements_are_not_suggested_again(
    client, auth_headers, users, resource_data, catalog, db
):
    control = resource_data["controls"]["admin"]

    _map(db, control, catalog(ISO, "8.24"))
    _map(db, control, catalog(NIS2, "Art. 21(2)(h)"))

    response = client.get(
        f"/api/v1/framework-crosswalk/control/{control.id}/suggestions",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    assert "Art. 21(2)(h)" not in _codes(response.json()["suggestions"], NIS2)


def test_an_umbrella_mapping_alone_suggests_nothing(
    client, auth_headers, users, resource_data, catalog, db
):
    control = resource_data["controls"]["admin"]

    _map(db, control, catalog("GDPR", "Art. 32"))

    response = client.get(
        f"/api/v1/framework-crosswalk/control/{control.id}/suggestions",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    assert response.json()["suggestions"] == []


def test_opportunities_point_unmapped_requirements_at_existing_controls(
    client, auth_headers, users, resource_data, catalog, db
):
    control = resource_data["controls"]["admin"]
    backup = catalog(ISO, "8.13")

    _map(db, control, backup)

    response = client.get(
        "/api/v1/framework-crosswalk/opportunities",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["total_requirements"] == 181
    assert body["unmapped_requirements"] == 180
    assert body["disclaimer"]

    opportunities = body["opportunities"]

    assert body["opportunity_count"] == len(opportunities)
    assert backup.id not in {item["framework_control_id"] for item in opportunities}
    assert _codes(opportunities, ISO) == set()

    dora_backup = next(
        item
        for item in opportunities
        if item["framework_name"] == "DORA" and item["control_code"] == "Art. 12"
    )

    assert dora_backup["best_confidence"] == "direct"
    assert [candidate["control_id"] for candidate in dora_backup["candidates"]] == [control.id]
    assert [via["control_code"] for via in dora_backup["candidates"][0]["via"]] == ["8.13"]

    iso_summary = next(item for item in body["frameworks"] if item["framework_name"] == ISO)
    assert iso_summary["requirement_count"] == 93
    assert iso_summary["unmapped_requirements"] == 92
    assert iso_summary["opportunities"] == 0


def test_no_mappings_means_no_opportunities(
    client, auth_headers, users, catalog
):
    response = client.get(
        "/api/v1/framework-crosswalk/opportunities",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["opportunity_count"] == 0
    assert body["opportunities"] == []
    assert body["unmapped_requirements"] == 181


def test_the_crosswalk_never_creates_mappings(
    client, auth_headers, users, resource_data, catalog, db
):
    control = resource_data["controls"]["admin"]

    _map(db, control, catalog(ISO, "8.24"))

    before = db.query(ControlFrameworkControl).count()

    for path in (
        "/api/v1/framework-crosswalk/opportunities",
        f"/api/v1/framework-crosswalk/control/{control.id}/suggestions",
        f"/api/v1/framework-crosswalk/framework-control/{catalog(ISO, '8.24').id}/related",
    ):
        assert client.get(path, headers=auth_headers(users["admin"])).status_code == 200

    assert db.query(ControlFrameworkControl).count() == before


# ----------------------------------------------------------
# Security boundaries
# ----------------------------------------------------------

@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/framework-crosswalk/opportunities",
        "/api/v1/framework-crosswalk/control/1/suggestions",
        "/api/v1/framework-crosswalk/framework-control/1/related",
    ],
)
def test_crosswalk_requires_login(client, path):
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("role", ["manager", "analyst", "auditor", "employee"])
def test_every_role_can_read_opportunities(
    client, auth_headers, users, catalog, role
):
    response = client.get(
        "/api/v1/framework-crosswalk/opportunities",
        headers=auth_headers(users[role]),
    )

    assert response.status_code == 200, response.text


def test_missing_control_and_requirement_return_404(
    client, auth_headers, users, catalog
):
    headers = auth_headers(users["admin"])

    assert client.get(
        "/api/v1/framework-crosswalk/control/999999/suggestions",
        headers=headers,
    ).status_code == 404

    assert client.get(
        "/api/v1/framework-crosswalk/framework-control/999999/related",
        headers=headers,
    ).status_code == 404


def test_another_organization_cannot_read_this_organizations_crosswalk(
    client, auth_headers, users, resource_data, catalog, db, second_organization
):
    control = resource_data["controls"]["admin"]
    crypto = catalog(ISO, "8.24")

    _map(db, control, crypto)

    outsider = auth_headers(second_organization["user"])

    assert client.get(
        f"/api/v1/framework-crosswalk/control/{control.id}/suggestions",
        headers=outsider,
    ).status_code == 404

    assert client.get(
        f"/api/v1/framework-crosswalk/framework-control/{crypto.id}/related",
        headers=outsider,
    ).status_code == 404

    response = client.get(
        "/api/v1/framework-crosswalk/opportunities",
        headers=outsider,
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["total_requirements"] == 0
    assert body["opportunities"] == []


def test_other_organizations_mappings_do_not_create_opportunities(
    client, auth_headers, users, catalog, db, second_organization
):
    """A mapping in one organization must not surface in another."""

    other = second_organization["organization"]
    other_admin = second_organization["user"]

    seed_organization(db, other.id)

    other_control = Control(
        organization_id=other.id,
        title="Other organization backup control",
        description="Backup control owned by the second organization.",
        control_type="Preventive",
        status="Active",
        effectiveness=80,
        owner_id=other_admin.id,
        created_by_id=other_admin.id,
    )
    db.add(other_control)
    db.flush()

    other_backup = (
        db.query(FrameworkControl)
        .join(Framework, Framework.id == FrameworkControl.framework_id)
        .filter(
            Framework.organization_id == other.id,
            Framework.name == ISO,
            FrameworkControl.control_code == "8.13",
        )
        .one()
    )

    _map(db, other_control, other_backup)

    response = client.get(
        "/api/v1/framework-crosswalk/opportunities",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["total_requirements"] == 181
    assert body["opportunity_count"] == 0

    theirs = client.get(
        "/api/v1/framework-crosswalk/opportunities",
        headers=auth_headers(other_admin),
    ).json()

    assert theirs["opportunity_count"] > 0
    assert {
        candidate["control_id"]
        for item in theirs["opportunities"]
        for candidate in item["candidates"]
    } == {other_control.id}
