"""Brute-force protection and the sign-in log."""

import logging
from datetime import datetime, timedelta, timezone

from app.auth import login_guard
from app.models.login_attempt import LoginAttempt

GOOD = "Password123!"
BAD = "WrongPassword123!"


def _login(client, email, password):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def test_repeated_failures_lock_the_account(client, users):
    email = users["admin"].email

    for _ in range(login_guard.MAX_FAILED_PER_EMAIL):
        assert _login(client, email, BAD).status_code == 401

    # Even the right password is refused while the lock is on.
    blocked = _login(client, email, GOOD)

    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) >= 1
    assert "Too many" in blocked.json()["detail"]


def test_unknown_emails_are_limited_the_same_way(client, users):
    for _ in range(login_guard.MAX_FAILED_PER_EMAIL):
        response = _login(client, "ghost@example.com", BAD)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password."

    assert _login(client, "ghost@example.com", BAD).status_code == 429


def test_other_accounts_are_not_affected(client, users):
    for _ in range(login_guard.MAX_FAILED_PER_EMAIL):
        _login(client, users["admin"].email, BAD)

    assert _login(client, users["manager"].email, GOOD).status_code == 200


def test_a_successful_sign_in_resets_the_count(client, users):
    email = users["admin"].email
    almost = login_guard.MAX_FAILED_PER_EMAIL - 1

    for _ in range(almost):
        assert _login(client, email, BAD).status_code == 401

    assert _login(client, email, GOOD).status_code == 200

    for _ in range(almost):
        assert _login(client, email, BAD).status_code == 401


def test_old_failures_stop_counting(client, db, users):
    email = users["admin"].email
    long_ago = datetime.now(timezone.utc) - timedelta(
        minutes=login_guard.LOCKOUT_MINUTES + 10
    )

    for _ in range(login_guard.MAX_FAILED_PER_EMAIL + 5):
        db.add(
            LoginAttempt(
                email=email,
                ip_address="203.0.113.9",
                success=False,
                created_at=long_ago,
            )
        )

    db.commit()

    assert _login(client, email, GOOD).status_code == 200


def test_one_address_failing_across_many_emails_is_blocked(
    client, users, monkeypatch
):
    monkeypatch.setattr(login_guard, "MAX_FAILED_PER_IP", 3)

    for number in range(3):
        response = _login(client, f"nobody{number}@example.com", BAD)

        assert response.status_code == 401

    # A different, valid account from the same address is refused too.
    assert _login(client, users["admin"].email, GOOD).status_code == 429


def test_attempts_are_stored(client, db, users):
    _login(client, "Admin@Example.com", BAD)
    _login(client, users["admin"].email, GOOD)

    rows = db.query(LoginAttempt).order_by(LoginAttempt.id).all()

    assert [row.success for row in rows] == [False, True]
    assert rows[0].email == "admin@example.com"
    assert rows[0].ip_address


def test_attempts_are_written_to_the_security_log(client, users, caplog):
    with caplog.at_level(logging.INFO, logger="cybergrc.security"):
        _login(client, users["admin"].email, BAD)
        _login(client, users["admin"].email, GOOD)

    assert "login_failed" in caplog.text
    assert "login_success" in caplog.text
    assert BAD not in caplog.text
    assert GOOD not in caplog.text