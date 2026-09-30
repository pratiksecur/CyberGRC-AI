import pytest

from app.services import notification_scheduler


def test_scheduler_interval_is_15_minutes():
    assert (
        notification_scheduler.SCHEDULER_INTERVAL_SECONDS
        == 15 * 60
    )


def test_scheduler_imports_continuous_response_notification_service():
    assert hasattr(
        notification_scheduler,
        "notify_continuous_risk_response",
    )


def test_scheduler_imports_risk_model():
    assert hasattr(
        notification_scheduler,
        "Risk",
    )


def test_scheduler_imports_corrective_action_model():
    assert hasattr(
        notification_scheduler,
        "CorrectiveAction",
    )


def test_scheduler_has_single_background_loop():
    assert hasattr(
        notification_scheduler,
        "notification_scheduler_loop",
    )


def test_scheduler_has_single_run_function():
    assert hasattr(
        notification_scheduler,
        "run_notification_scheduler",
    )


def test_scheduler_does_not_define_second_scheduler_loop():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    assert source.count(
        "async def notification_scheduler_loop"
    ) == 1


def test_scheduler_does_not_execute_response_decisions():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    forbidden_patterns = [
        "REASSESS_RISK",
        "UPDATE_TREATMENT",
        "CORRECTIVE_ACTION_REVIEW",
        "CONTROL_REVIEW",
        "EVIDENCE_REVIEW",
        "ESCALATE",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in source


def test_scheduler_uses_existing_notification_service():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    assert (
        "notify_corrective_action_event"
        in source
    )


def test_scheduler_uses_continuous_response_notification():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    assert (
        "notify_continuous_risk_response"
        in source
    )


def test_scheduler_logs_failures():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    assert "logger.error" in source
    assert "scheduled_continuous_risk_response_failed" in source


def test_scheduler_commits_notifications():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    assert "db.commit()" in source


def test_scheduler_rolls_back_on_run_failure():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    assert "db.rollback()" in source


def test_scheduler_closes_database_session():
    module_source = (
        notification_scheduler.__file__
    )

    with open(
        module_source,
        "r",
        encoding="utf-8",
    ) as file:
        source = file.read()

    assert "db.close()" in source