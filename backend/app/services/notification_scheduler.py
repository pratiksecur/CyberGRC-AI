"""
Background scheduler for time-based GRC notifications.

This module handles notifications that depend on the passage
of time rather than on a database mutation.

Examples:

- Corrective actions due within 7 days
- Corrective actions that are overdue

Event-driven notifications remain handled by
notification_events.py.
"""

import asyncio
import logging

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.corrective_action import CorrectiveAction
from app.services.notification_service import (
    notify_corrective_action_event,
)


logger = logging.getLogger(
    "cybergrc.notifications.scheduler"
)

logger.setLevel(logging.INFO)


# ==========================================================
# CONFIGURATION
# ==========================================================

SCHEDULER_INTERVAL_SECONDS = 15 * 60


# ==========================================================
# SINGLE SCHEDULER RUN
# ==========================================================


def run_notification_scheduler():
    """
    Execute one time-based notification scan.

    A new database session is created specifically for the
    scheduler run and closed when processing is complete.
    """

    db: Session = SessionLocal()

    try:
        actions = (
            db.query(CorrectiveAction)
            .all()
        )

        for action in actions:
            try:
                notify_corrective_action_event(
                    db,
                    action,
                )

            except Exception as exc:
                logger.error(
                    "scheduled_notification_failed "
                    "corrective_action_id=%s "
                    "exception_type=%s",
                    action.id,
                    type(exc).__name__,
                )

        db.commit()

        logger.info(
            "notification_scheduler_completed "
            "processed_corrective_actions=%s",
            len(actions),
        )

    except Exception as exc:
        db.rollback()

        logger.error(
            "notification_scheduler_run_failed "
            "exception_type=%s",
            type(exc).__name__,
        )

    finally:
        db.close()


# ==========================================================
# BACKGROUND LOOP
# ==========================================================


async def notification_scheduler_loop():
    """
    Run the notification scheduler continuously.

    The synchronous database work is executed in a worker
    thread so that it does not block FastAPI's async event loop.
    """

    logger.info(
        "notification_scheduler_started "
        "interval_seconds=%s",
        SCHEDULER_INTERVAL_SECONDS,
    )

    while True:
        try:
            await asyncio.to_thread(
                run_notification_scheduler
            )

        except asyncio.CancelledError:
            logger.info(
                "notification_scheduler_stopped"
            )
            raise

        except Exception as exc:
            logger.error(
                "notification_scheduler_unexpected_error "
                "exception_type=%s",
                type(exc).__name__,
            )

        await asyncio.sleep(
            SCHEDULER_INTERVAL_SECONDS
        )