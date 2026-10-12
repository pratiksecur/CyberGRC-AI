"""Brute-force protection and security logging for sign-in.

Every attempt is stored in ``login_attempts``. Before the password is even
checked, the guard looks at recent failures:

  * the same email failed LOGIN_MAX_FAILED_ATTEMPTS times in the last
    LOGIN_LOCKOUT_MINUTES (counted since the last successful sign-in), or
  * the same IP address failed LOGIN_MAX_FAILED_PER_IP times in that window

and refuses the attempt with a "try again later" answer. Nothing is kept in
memory, so it works with several workers or containers and survives restarts.

Unknown emails are counted too, so the answer never reveals whether an
account exists. The trade-off is that someone who knows an email can lock
that account for a few minutes; that is the usual cost of account lockout.

Environment variables (all optional):

    LOGIN_MAX_FAILED_ATTEMPTS   default 5
    LOGIN_MAX_FAILED_PER_IP     default 20
    LOGIN_LOCKOUT_MINUTES       default 15
"""

import logging
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.login_attempt import LoginAttempt


logger = logging.getLogger("cybergrc.security")

# The app has no logging set-up of its own, and Python only prints warnings
# by default. Give the security log a handler and INFO level so successful
# sign-ins show up in `docker compose logs backend` too.
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

RETENTION_DAYS = 30


def _int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name, "").strip()

    if not raw_value:
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a whole number.") from exc

    if value < 1:
        raise RuntimeError(f"{name} must be at least 1.")

    return value


MAX_FAILED_PER_EMAIL = _int_env("LOGIN_MAX_FAILED_ATTEMPTS", 5)
MAX_FAILED_PER_IP = _int_env("LOGIN_MAX_FAILED_PER_IP", 20)
LOCKOUT_MINUTES = _int_env("LOGIN_LOCKOUT_MINUTES", 15)


class LoginBlocked(Exception):
    """Too many recent failures. Carries how long to wait, in seconds."""

    def __init__(self, retry_after_seconds: int):
        self.retry_after_seconds = max(1, int(retry_after_seconds))
        super().__init__("Too many failed sign-in attempts.")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime) -> datetime:
    # SQLite hands back naive datetimes; they are always UTC here.
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def _seconds_until_unblocked(oldest_failure: datetime, now: datetime) -> int:
    release = _aware(oldest_failure) + timedelta(minutes=LOCKOUT_MINUTES)

    return int((release - now).total_seconds()) + 1


def check_login_allowed(
    db: Session,
    email: str,
    ip_address: str | None,
) -> None:
    """Raise LoginBlocked if this email or IP has failed too often."""

    now = _now()
    window_start = now - timedelta(minutes=LOCKOUT_MINUTES)

    # Failures before the last successful sign-in no longer count.
    last_success = (
        db.query(func.max(LoginAttempt.created_at))
        .filter(
            LoginAttempt.email == email,
            LoginAttempt.success.is_(True),
        )
        .scalar()
    )

    email_start = window_start

    if last_success is not None:
        email_start = max(window_start, _aware(last_success))

    email_failures = (
        db.query(
            func.count(LoginAttempt.id),
            func.min(LoginAttempt.created_at),
        )
        .filter(
            LoginAttempt.email == email,
            LoginAttempt.success.is_(False),
            LoginAttempt.created_at > email_start,
        )
        .one()
    )

    if email_failures[0] >= MAX_FAILED_PER_EMAIL:
        logger.warning(
            "login_blocked reason=email email=%r ip=%s",
            email,
            ip_address,
        )
        raise LoginBlocked(
            _seconds_until_unblocked(email_failures[1], now)
        )

    if ip_address:
        ip_failures = (
            db.query(
                func.count(LoginAttempt.id),
                func.min(LoginAttempt.created_at),
            )
            .filter(
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.success.is_(False),
                LoginAttempt.created_at > window_start,
            )
            .one()
        )

        if ip_failures[0] >= MAX_FAILED_PER_IP:
            logger.warning(
                "login_blocked reason=ip email=%r ip=%s",
                email,
                ip_address,
            )
            raise LoginBlocked(
                _seconds_until_unblocked(ip_failures[1], now)
            )


def record_login_attempt(
    db: Session,
    email: str,
    ip_address: str | None,
    *,
    success: bool,
    reason: str = "",
) -> None:
    """Store one attempt and write it to the security log."""

    now = _now()

    db.add(
        LoginAttempt(
            email=email[:255],
            ip_address=(ip_address or None),
            success=success,
            created_at=now,
        )
    )

    if success:
        # Housekeeping: old rows are of no use to the lockout counters.
        db.query(LoginAttempt).filter(
            LoginAttempt.created_at < now - timedelta(days=RETENTION_DAYS)
        ).delete(synchronize_session=False)

        logger.info(
            "login_success email=%r ip=%s",
            email,
            ip_address,
        )
    else:
        logger.warning(
            "login_failed email=%r ip=%s reason=%s",
            email,
            ip_address,
            reason or "invalid_credentials",
        )

    db.commit()