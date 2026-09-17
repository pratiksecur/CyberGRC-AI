from app.services.dashboard_service import (
    get_dashboard_data,
)


def test_admin_dashboard_is_organization_wide(
    db,
    users,
    resource_data,
):
    dashboard = get_dashboard_data(
        db,
        users["admin"],
    )

    # Admin has organization-wide risk visibility.
    assert dashboard["totalRisks"] == 5

    # Admin has organization-wide control visibility.
    # Derive the expected value from the shared fixture
    # rather than relying on a stale hard-coded count.
    assert dashboard["controls"] == len(
        resource_data["controls"]
    )


def test_grc_manager_dashboard_contains_subordinates(
    db,
    users,
    resource_data,
):
    dashboard = get_dashboard_data(
        db,
        users["manager"],
    )

    # Manager sees manager + subordinate-owned risks.
    # Admin-owned risk is outside the manager's scope.
    assert dashboard["totalRisks"] == 4


def test_risk_analyst_dashboard_is_own_scope(
    db,
    users,
    resource_data,
):
    dashboard = get_dashboard_data(
        db,
        users["analyst"],
    )

    assert dashboard["totalRisks"] == 1
    assert dashboard["criticalRisks"] == 1


def test_employee_dashboard_is_own_risk_scope(
    db,
    users,
    resource_data,
):
    dashboard = get_dashboard_data(
        db,
        users["employee"],
    )

    assert dashboard["totalRisks"] == 1
    assert dashboard["criticalRisks"] == 0


def test_auditor_dashboard_risk_scope_is_organization_wide(
    db,
    users,
    resource_data,
):
    dashboard = get_dashboard_data(
        db,
        users["auditor"],
    )

    assert dashboard["totalRisks"] == 5