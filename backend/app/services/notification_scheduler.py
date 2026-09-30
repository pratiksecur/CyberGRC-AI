"""
Background scheduler for time-based and continuous-risk GRC notifications.

This module handles notifications that depend on the passage
of time or periodic evaluation of authoritative GRC state.

Examples:

- Corrective actions due within 7 days
- Corrective actions that are overdue
- Continuous risk responses requiring human attention

The scheduler communicates governed response requirements only.

It does NOT automatically execute:

- risk reassessment
- treatment changes
- control changes
- corrective-action changes
- escalation actions

Those remain human-authorized workflows.
"""

import asyncio
import logging

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.corrective_action import CorrectiveAction
from app.models.risk import Risk

from app.services.notification_service import (
    notify_corrective_action_event,
)

from app.services.continuous_risk_response_notification_service import (
    notify_continuous_risk_response,
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
    Execute one notification scheduler scan.

    A new database session is created specifically for the
    scheduler run and closed when processing is complete.

    The scheduler evaluates:

    - Corrective-action notification conditions
    - Continuous-risk response conditions

    Continuous-risk response notifications are communication
    only. High-impact decisions remain human-authorized.
    """

    db: Session = SessionLocal()

    processed_corrective_actions = 0
    processed_risks = 0

    try:

        # --------------------------------------------------
        # CORRECTIVE ACTION NOTIFICATIONS
        # --------------------------------------------------

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

                processed_corrective_actions += 1

            except Exception as exc:

                logger.error(
                    "scheduled_notification_failed "
                    "corrective_action_id=%s "
                    "exception_type=%s",
                    action.id,
                    type(exc).__name__,
                )

        # --------------------------------------------------
        # CONTINUOUS RISK RESPONSE NOTIFICATIONS
        # --------------------------------------------------

        risks = (
            db.query(Risk)
            .all()
        )

        for risk in risks:

            try:

                notify_continuous_risk_response(
                    db,
                    risk,
                )

                processed_risks += 1

            except Exception as exc:

                logger.error(
                    "scheduled_continuous_risk_response_failed "
                    "risk_id=%s "
                    "exception_type=%s",
                    risk.id,
                    type(exc).__name__,
                )

        # --------------------------------------------------
        # COMMIT ALL NOTIFICATIONS
        # --------------------------------------------------

        db.commit()

        logger.info(
            "notification_scheduler_completed "
            "processed_corrective_actions=%s "
            "processed_risks=%s",
            processed_corrective_actions,
            processed_risks,
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