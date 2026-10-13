"""Reliable, governance-safe background notification scheduler."""

import asyncio
import logging

from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.core.config import (
    SCHEDULER_BATCH_SIZE,
    SCHEDULER_INTERVAL_SECONDS as CONFIG_SCHEDULER_INTERVAL_SECONDS,
    SCHEDULER_LOCK_KEY,
)
from app.database.database import SessionLocal
from app.models.corrective_action import CorrectiveAction
from app.models.risk import Risk
from app.services.continuous_risk_response_notification_service import (
    notify_continuous_risk_response,
)
from app.services.notification_service import notify_corrective_action_event


logger = logging.getLogger("cybergrc.notifications.scheduler")
logger.setLevel(logging.INFO)

# Backward-compatible public constant used by existing tests.
SCHEDULER_INTERVAL_SECONDS = CONFIG_SCHEDULER_INTERVAL_SECONDS

# The advisory lock prevents multiple workers from executing a scan at the
# same time. These cursors keep each run bounded while allowing the active
# scheduler to rotate through the complete candidate set over successive runs.
_last_corrective_action_id = 0
_last_risk_id = 0


def _try_acquire_scheduler_lock(db: Session) -> bool:
    """Acquire a PostgreSQL advisory lock so multiple workers cannot duplicate a run."""
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return True

    result = db.execute(
        text("SELECT pg_try_advisory_lock(:lock_key)"),
        {"lock_key": SCHEDULER_LOCK_KEY},
    )
    return bool(result.scalar())


def _release_scheduler_lock(db: Session) -> None:
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT pg_advisory_unlock(:lock_key)"),
            {"lock_key": SCHEDULER_LOCK_KEY},
        )


def _next_corrective_action_batch(db: Session):
    """Return one bounded batch of notification-relevant corrective actions."""
    global _last_corrective_action_id

    query = (
        db.query(CorrectiveAction)
        .filter(
            or_(
                CorrectiveAction.status.is_(None),
                CorrectiveAction.status.notin_(["Completed", "Closed"]),
            )
        )
        .order_by(CorrectiveAction.id)
    )

    batch = (
        query
        .filter(CorrectiveAction.id > _last_corrective_action_id)
        .limit(SCHEDULER_BATCH_SIZE)
        .all()
    )

    if not batch and _last_corrective_action_id:
        batch = query.limit(SCHEDULER_BATCH_SIZE).all()

    if batch:
        _last_corrective_action_id = batch[-1].id

    return batch


def _next_risk_batch(db: Session):
    """Return one bounded batch of active risks for response evaluation."""
    global _last_risk_id

    query = (
        db.query(Risk)
        .filter(or_(Risk.status.is_(None), Risk.status != "Closed"))
        .order_by(Risk.id)
    )

    batch = (
        query
        .filter(Risk.id > _last_risk_id)
        .limit(SCHEDULER_BATCH_SIZE)
        .all()
    )

    if not batch and _last_risk_id:
        batch = query.limit(SCHEDULER_BATCH_SIZE).all()

    if batch:
        _last_risk_id = batch[-1].id

    return batch


def run_notification_scheduler():
    """Execute one bounded notification batch with transaction-safe locking."""
    db: Session = SessionLocal()
    processed_corrective_actions = 0
    processed_risks = 0
    lock_acquired = False

    try:
        lock_acquired = _try_acquire_scheduler_lock(db)
        if not lock_acquired:
            logger.info("notification_scheduler_skipped lock_not_acquired=true")
            db.rollback()
            return

        actions = _next_corrective_action_batch(db)

        for action in actions:
            try:
                with db.begin_nested():
                    notify_corrective_action_event(db, action)
                processed_corrective_actions += 1
            except Exception as exc:
                logger.error(
                    "scheduled_notification_failed corrective_action_id=%s exception_type=%s",
                    action.id,
                    type(exc).__name__,
                )

        risks = _next_risk_batch(db)

        for risk in risks:
            try:
                with db.begin_nested():
                    notify_continuous_risk_response(db, risk)
                processed_risks += 1
            except Exception as exc:
                # The database's own message names the column or value at
                # fault. Only its first line is logged, cut to 300 characters.
                detail = str(getattr(exc, "orig", exc)).splitlines()
                logger.error(
                    "scheduled_continuous_risk_response_failed risk_id=%s exception_type=%s detail=%s",
                    risk.id,
                    type(exc).__name__,
                    (detail[0] if detail else "")[:300],
                )

        db.commit()

        logger.info(
            "notification_scheduler_completed processed_corrective_actions=%s processed_risks=%s",
            processed_corrective_actions,
            processed_risks,
        )

    except Exception as exc:
        db.rollback()
        logger.error(
            "notification_scheduler_run_failed exception_type=%s",
            type(exc).__name__,
        )
    finally:
        if lock_acquired:
            try:
                _release_scheduler_lock(db)
            except Exception as exc:
                logger.error(
                    "notification_scheduler_lock_release_failed exception_type=%s",
                    type(exc).__name__,
                )
        db.close()


async def notification_scheduler_loop():
    """Run the scheduler periodically without blocking FastAPI's event loop."""
    logger.info(
        "notification_scheduler_started interval_seconds=%s batch_size=%s",
        SCHEDULER_INTERVAL_SECONDS,
        SCHEDULER_BATCH_SIZE,
    )

    while True:
        try:
            await asyncio.to_thread(run_notification_scheduler)
        except asyncio.CancelledError:
            logger.info("notification_scheduler_stopped")
            raise
        except Exception as exc:
            logger.error(
                "notification_scheduler_unexpected_error exception_type=%s",
                type(exc).__name__,
            )

        await asyncio.sleep(SCHEDULER_INTERVAL_SECONDS)
