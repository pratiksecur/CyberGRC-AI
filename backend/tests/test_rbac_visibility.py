from app.auth.visibility import (
    get_visible_user_ids,
    can_view_user,
)

from app.auth.scopes import AccessScope


def test_admin_can_see_entire_organization(
    db,
    users,
):
    admin = users["admin"]

    visible_ids = set(
        get_visible_user_ids(
            db,
            admin,
            "risks",
        )
    )

    assert visible_ids == {
        users["admin"].id,
        users["manager"].id,
        users["analyst"].id,
        users["auditor"].id,
        users["employee"].id,
    }


def test_grc_manager_can_see_self_and_subordinates(
    db,
    users,
):
    manager = users["manager"]

    visible_ids = set(
        get_visible_user_ids(
            db,
            manager,
            "risks",
        )
    )

    assert visible_ids == {
        users["manager"].id,
        users["analyst"].id,
        users["auditor"].id,
        users["employee"].id,
    }

    assert users["admin"].id not in visible_ids


def test_risk_analyst_owns_risk_scope(
    db,
    users,
):
    analyst = users["analyst"]

    visible_ids = set(
        get_visible_user_ids(
            db,
            analyst,
            "risks",
        )
    )

    assert visible_ids == {
        analyst.id,
    }


def test_auditor_has_organization_risk_scope(
    db,
    users,
):
    auditor = users["auditor"]

    visible_ids = set(
        get_visible_user_ids(
            db,
            auditor,
            "risks",
        )
    )

    assert visible_ids == {
        users["admin"].id,
        users["manager"].id,
        users["analyst"].id,
        users["auditor"].id,
        users["employee"].id,
    }


def test_employee_has_own_risk_scope(
    db,
    users,
):
    employee = users["employee"]

    visible_ids = set(
        get_visible_user_ids(
            db,
            employee,
            "risks",
        )
    )

    assert visible_ids == {
        employee.id,
    }


def test_can_view_user_respects_resource_scope(
    db,
    users,
):
    manager = users["manager"]

    assert can_view_user(
        db,
        manager,
        users["analyst"].id,
        "risks",
    )

    assert can_view_user(
        db,
        manager,
        users["employee"].id,
        "risks",
    )

    assert not can_view_user(
        db,
        manager,
        users["admin"].id,
        "risks",
    )


def test_recursive_subordinate_visibility(
    db,
    users,
):
    """
    Add an employee underneath the Risk Analyst.

    The GRC Manager should still see that employee because
    subordinate visibility is recursive.
    """

    from app.models.user import User

    nested_employee = User(
        full_name="Nested Employee",
        email="nested@test.local",
        hashed_password="test",
        role="Employee",
        manager_id=users["analyst"].id,
        department="Operations",
    )

    db.add(nested_employee)
    db.commit()
    db.refresh(nested_employee)

    visible_ids = set(
        get_visible_user_ids(
            db,
            users["manager"],
            "risks",
        )
    )

    assert nested_employee.id in visible_ids