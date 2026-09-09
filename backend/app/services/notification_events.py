"""
Event-driven notification generation.

This module listens to SQLAlchemy session flushes and generates
notifications when important GRC resources are created or changed.

The notification engine is intentionally separated from API routes
and business services so that notification behavior remains
consistent regardless of where a resource mutation originates.
"""

import logging
from datetime import date, timedelta

from sqlalchemy import event
from sqlalchemy.orm import Session, attributes

from app.models.risk import Risk
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction

from app.services.notification_service import (
    notify_risk_event,
    notify_audit_event,
    notify_finding_event,
    notify_corrective_action_event,
)


logger = logging.getLogger(__name__)


# ==========================================================
# RISK EVENTS
# ==========================================================

def _process_risk_event(
    session: Session,
    risk: Risk,
):
    """
    Generate notifications for a Risk event.

    A notification is generated when:

    - a new risk is created as critical
    - an existing risk becomes or remains critical
    """

    if risk.risk_score >= 20:

        notify_risk_event(
            session,
            risk,
        )


# ==========================================================
# AUDIT EVENTS
# ==========================================================

def _process_audit_event(
    session: Session,
    audit: Audit,
):
    """
    Generate an audit notification when an audit is created.

    Audit updates are intentionally not treated as new audits.
    """

    if audit.id is None:
        return

    state = attributes.instance_state(audit)

    if state.persistent:
        return

    notify_audit_event(
        session,
        audit,
    )


# ==========================================================
# FINDING EVENTS
# ==========================================================

def _process_finding_event(
    session: Session,
    finding: AuditFinding,
):
    """
    Generate notifications for critical findings.

    Notifications are generated when:

    - a critical finding is created
    - an existing finding becomes critical
    """

    if finding.severity != "Critical":
        return

    notify_finding_event(
        session,
        finding,
    )


# ==========================================================
# CORRECTIVE ACTION EVENTS
# ==========================================================

def _process_corrective_action_event(
    session: Session,
    action: CorrectiveAction,
):
    """
    Generate notifications for corrective-action state changes.

    This covers:

    - critical actions
    - actions due soon
    - overdue actions
    - completed actions
    """

    notify_corrective_action_event(
        session,
        action,
    )


# ==========================================================
# SESSION FLUSH EVENT
# ==========================================================

@event.listens_for(
    Session,
    "after_flush",
)
def process_notification_events(
    session: Session,
    flush_context,
):
    """
    Process GRC events after SQLAlchemy has flushed changes.

    We inspect:

    - session.new
    - session.dirty

    Notification objects themselves are ignored because they are
    not one of the monitored GRC resource models.
    """

    # ------------------------------------------------------
    # Newly created resources
    # ------------------------------------------------------

    new_objects = list(session.new)

    for obj in new_objects:

        try:

            if isinstance(obj, Risk):

                _process_risk_event(
                    session,
                    obj,
                )

            elif isinstance(obj, Audit):

                _process_audit_event(
                    session,
                    obj,
                )

            elif isinstance(obj, AuditFinding):

                _process_finding_event(
                    session,
                    obj,
                )

            elif isinstance(obj, CorrectiveAction):

                _process_corrective_action_event(
                    session,
                    obj,
                )

        except Exception:
            logger.exception(
                "Failed to generate notification for newly "
                "created %s.",
                type(obj).__name__,
            )

    # ------------------------------------------------------
    # Updated resources
    # ------------------------------------------------------

    dirty_objects = list(session.dirty)

    for obj in dirty_objects:

        try:

            if isinstance(obj, Risk):

                if session.is_modified(
                    obj,
                    include_collections=False,
                ):
                    _process_risk_event(
                        session,
                        obj,
                    )

            elif isinstance(obj, AuditFinding):

                if session.is_modified(
                    obj,
                    include_collections=False,
                ):
                    _process_finding_event(
                        session,
                        obj,
                    )

            elif isinstance(obj, CorrectiveAction):

                if session.is_modified(
                    obj,
                    include_collections=False,
                ):
                    _process_corrective_action_event(
                        session,
                        obj,
                    )

        except Exception:
            logger.exception(
                "Failed to generate notification for updated "
                "%s.",
                type(obj).__name__,
            )