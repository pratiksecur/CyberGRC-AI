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


logger = logging.getLogger("uvicorn")


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

            except Exception:
                logger.exception(
                    "Failed to process scheduled notification "
                    "for Corrective Action #%s.",
                    action.id,
                )

        db.commit()

        logger.info(
            "Notification scheduler completed. "
            "Processed %s corrective actions.",
            len(actions),
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Notification scheduler run failed."
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
        "Notification scheduler started. "
        "Interval: %s seconds.",
        SCHEDULER_INTERVAL_SECONDS,
    )

    while True:
        try:
            await asyncio.to_thread(
                run_notification_scheduler
            )

        except asyncio.CancelledError:
            logger.info(
                "Notification scheduler stopped."
            )
            raise

        except Exception:
            logger.exception(
                "Unexpected notification scheduler error."
            )

        await asyncio.sleep(
            SCHEDULER_INTERVAL_SECONDS
        )