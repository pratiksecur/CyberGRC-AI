from app.auth.permissions import has_permission
from app.auth.ai_access import (
    get_authorized_risk,
    get_authorized_audit,
)


def test_only_grc_manager_can_use_executive_summary(
    users,
):
    allowed_user = users["manager"]

    denied_users = [
        users["admin"],
        users["analyst"],
        users["auditor"],
        users["employee"],
    ]

    assert has_permission(
        allowed_user,
        "ai_executive_summary",
        "view",
    )

    assert has_permission(
        allowed_user,
        "ai_executive_summary",
        "use",
    )

    for user in denied_users:
        assert not has_permission(
            user,
            "ai_executive_summary",
            "view",
        )

        assert not has_permission(
            user,
            "ai_executive_summary",
            "use",
        )


def test_risk_ai_respects_risk_scope(
    db,
    users,
    resource_data,
):
    manager = users["manager"]
    analyst = users["analyst"]

    analyst_risk = resource_data["risks"]["analyst"]
    admin_risk = resource_data["risks"]["admin"]

    # GRC Manager can access subordinate-owned risk.
    assert (
        get_authorized_risk(
            db,
            manager,
            analyst_risk.id,
        )
        is not None
    )

    # GRC Manager cannot access Admin-owned risk.
    assert (
        get_authorized_risk(
            db,
            manager,
            admin_risk.id,
        )
        is None
    )

    # Risk Analyst can access their own risk.
    assert (
        get_authorized_risk(
            db,
            analyst,
            analyst_risk.id,
        )
        is not None
    )

    # Risk Analyst cannot access Admin-owned risk.
    assert (
        get_authorized_risk(
            db,
            analyst,
            admin_risk.id,
        )
        is None
    )


def test_auditor_can_access_organization_risks(
    db,
    users,
    resource_data,
):
    auditor = users["auditor"]

    admin_risk = resource_data["risks"]["admin"]

    authorized_risk = get_authorized_risk(
        db,
        auditor,
        admin_risk.id,
    )

    assert authorized_risk is not None


def test_employee_cannot_access_another_users_risk(
    db,
    users,
    resource_data,
):
    employee = users["employee"]

    admin_risk = resource_data["risks"]["admin"]

    authorized_risk = get_authorized_risk(
        db,
        employee,
        admin_risk.id,
    )

    assert authorized_risk is None


def test_ai_access_never_returns_missing_risk(
    db,
    users,
):
    risk = get_authorized_risk(
        db,
        users["manager"],
        999999,
    )

    assert risk is None


def test_audit_ai_access_helper_exists_and_enforces_scope(
    db,
    users,
):
    """
    The helper must return None for an audit that does not
    exist rather than allowing downstream AI processing.
    """

    result = get_authorized_audit(
        db,
        users["manager"],
        999999,
    )

    assert result is None