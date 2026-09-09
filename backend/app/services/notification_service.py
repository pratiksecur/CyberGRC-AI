from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.risk import Risk
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction

from app.services.notification_recipient_service import (
    get_risk_recipients,
    get_audit_recipients,
    get_finding_recipients,
    get_corrective_action_recipients,
)


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _notification_exists(
    db: Session,
    user_id: int,
    notification_type: str,
    source_type: str,
    source_id: int,
) -> bool:

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.type == notification_type,
            Notification.source_type == source_type,
            Notification.source_id == source_id,
        )
        .first()
        is not None
    )


def _create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    source_type: str,
    source_id: int,
):
    """
    Create one notification if it does not already exist.

    This function intentionally does NOT commit.

    The notification is added to the same SQLAlchemy transaction
    as the GRC event that triggered it.
    """

    if _notification_exists(
        db,
        user_id,
        notification_type,
        source_type,
        source_id,
    ):
        return

    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        source_type=source_type,
        source_id=source_id,
        is_read=False,
    )

    db.add(notification)


def _create_for_recipients(
    db: Session,
    recipients: set[int],
    notification_type: str,
    title: str,
    message: str,
    source_type: str,
    source_id: int,
):
    """
    Create one notification for each resolved recipient.
    """

    for user_id in recipients:

        _create_notification(
            db=db,
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            source_type=source_type,
            source_id=source_id,
        )


# ==========================================================
# RISK EVENT
# ==========================================================

def notify_risk_event(
    db: Session,
    risk: Risk,
):
    """
    Generate a notification when a risk is critical.

    Recipients are determined by the notification recipient
    resolver.
    """

    if risk.risk_score < 20:
        return

    recipients = get_risk_recipients(
        db,
        risk,
    )

    _create_for_recipients(
        db=db,
        recipients=recipients,
        notification_type="critical_risk",
        title="Critical Risk Requires Attention",
        message=(
            f"{risk.title} has a critical risk score "
            f"of {risk.risk_score}."
        ),
        source_type="risk",
        source_id=risk.id,
    )


# ==========================================================
# AUDIT EVENT
# ==========================================================

def notify_audit_event(
    db: Session,
    audit: Audit,
):
    """
    Generate a notification when an audit is created.
    """

    recipients = get_audit_recipients(
        db,
        audit,
    )

    _create_for_recipients(
        db=db,
        recipients=recipients,
        notification_type="audit_created",
        title="Audit Available",
        message=(
            f"{audit.name} is currently "
            f"{audit.status.lower()}."
        ),
        source_type="audit",
        source_id=audit.id,
    )


# ==========================================================
# AUDIT FINDING EVENT
# ==========================================================

def notify_finding_event(
    db: Session,
    finding: AuditFinding,
):
    """
    Generate a notification for a critical audit finding.
    """

    if finding.severity != "Critical":
        return

    recipients = get_finding_recipients(
        db,
        finding,
    )

    _create_for_recipients(
        db=db,
        recipients=recipients,
        notification_type="critical_finding",
        title="Critical Audit Finding",
        message=(
            f"{finding.title} is a critical "
            "audit finding requiring attention."
        ),
        source_type="audit_finding",
        source_id=finding.id,
    )


# ==========================================================
# CORRECTIVE ACTION EVENT
# ==========================================================

def notify_corrective_action_event(
    db: Session,
    action: CorrectiveAction,
):
    """
    Generate notifications based on the current corrective
    action state.

    Handles:

    - critical action
    - due soon
    - overdue
    - completed
    """

    recipients = get_corrective_action_recipients(
        db,
        action,
    )

    if not recipients:
        return

    today = date.today()
    due_soon_date = today + timedelta(days=7)

    # ------------------------------------------------------
    # Critical action
    # ------------------------------------------------------

    if (
        action.priority == "Critical"
        and action.status not in (
            "Completed",
            "Closed",
        )
    ):

        _create_for_recipients(
            db=db,
            recipients=recipients,
            notification_type="critical_action",
            title="Critical Corrective Action",
            message=(
                f"{action.title} is a critical "
                "remediation action."
            ),
            source_type="corrective_action",
            source_id=action.id,
        )

    # ------------------------------------------------------
    # Due soon
    # ------------------------------------------------------

    if (
        action.status not in (
            "Completed",
            "Closed",
        )
        and action.due_date is not None
        and today <= action.due_date <= due_soon_date
    ):

        _create_for_recipients(
            db=db,
            recipients=recipients,
            notification_type="action_due_soon",
            title="Corrective Action Due Soon",
            message=(
                f"{action.title} is due on "
                f"{action.due_date.isoformat()}."
            ),
            source_type="corrective_action_due",
            source_id=action.id,
        )

    # ------------------------------------------------------
    # Overdue
    # ------------------------------------------------------

    if (
        action.status not in (
            "Completed",
            "Closed",
        )
        and action.due_date is not None
        and action.due_date < today
    ):

        _create_for_recipients(
            db=db,
            recipients=recipients,
            notification_type="action_overdue",
            title="Corrective Action Overdue",
            message=(
                f"{action.title} was due on "
                f"{action.due_date.isoformat()}."
            ),
            source_type="corrective_action_overdue",
            source_id=action.id,
        )

    # ------------------------------------------------------
    # Completed
    # ------------------------------------------------------

    if action.status == "Completed":

        _create_for_recipients(
            db=db,
            recipients=recipients,
            notification_type="action_completed",
            title="Corrective Action Completed",
            message=(
                f"{action.title} has been completed."
            ),
            source_type="corrective_action_completed",
            source_id=action.id,
        )


# ==========================================================
# READ NOTIFICATIONS
# ==========================================================

def get_notifications(
    db: Session,
    user_id: int,
):
    """
    Return notifications for a user.

    IMPORTANT:

    This function is now read-only.

    Opening the notification panel no longer scans the entire
    GRC database and does not generate notifications.
    """

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
        )
        .order_by(
            Notification.created_at.desc(),
        )
        .limit(20)
        .all()
    )


# ==========================================================
# UNREAD COUNT
# ==========================================================

def get_unread_count(
    db: Session,
    user_id: int,
):
    """
    Return the current unread notification count.

    This is also read-only.
    """

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .count()
    )


# ==========================================================
# MARK ONE AS READ
# ==========================================================

def mark_notification_read(
    db: Session,
    user_id: int,
    notification_id: int,
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )

    if notification is None:
        return None

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification


# ==========================================================
# MARK ALL AS READ
# ==========================================================

def mark_all_notifications_read(
    db: Session,
    user_id: int,
):
    (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .update(
            {
                Notification.is_read: True,
            },
            synchronize_session=False,
        )
    )

    db.commit()