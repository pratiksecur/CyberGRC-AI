from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.risk import Risk
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction


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


def sync_notifications(
    db: Session,
    user_id: int,
):
    """
    Generate notifications from the current GRC state.

    The operation is idempotent. Existing notifications
    are never duplicated.
    """

    # ==================================================
    # CRITICAL RISKS
    # ==================================================

    critical_risks = (
        db.query(Risk)
        .filter(
            Risk.risk_score >= 20,
        )
        .all()
    )

    for risk in critical_risks:

        _create_notification(
            db=db,
            user_id=user_id,
            notification_type="critical_risk",
            title="Critical Risk Requires Attention",
            message=(
                f"{risk.title} has a critical risk score "
                f"of {risk.risk_score}."
            ),
            source_type="risk",
            source_id=risk.id,
        )

    # ==================================================
    # CRITICAL AUDIT FINDINGS
    # ==================================================

    critical_findings = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.severity == "Critical",
            AuditFinding.status != "Closed",
        )
        .all()
    )

    for finding in critical_findings:

        _create_notification(
            db=db,
            user_id=user_id,
            notification_type="critical_finding",
            title="Critical Audit Finding",
            message=(
                f"{finding.title} is a critical "
                "audit finding requiring attention."
            ),
            source_type="audit_finding",
            source_id=finding.id,
        )

    # ==================================================
    # AUDITS
    # ==================================================

    audits = (
        db.query(Audit)
        .order_by(
            Audit.created_at.desc()
        )
        .all()
    )

    for audit in audits:

        _create_notification(
            db=db,
            user_id=user_id,
            notification_type="audit_created",
            title="Audit Available",
            message=(
                f"{audit.name} is currently "
                f"{audit.status.lower()}."
            ),
            source_type="audit",
            source_id=audit.id,
        )

    # ==================================================
    # CORRECTIVE ACTIONS
    # ==================================================

    actions = (
        db.query(CorrectiveAction)
        .all()
    )

    today = date.today()

    due_soon_date = today + timedelta(days=7)

    for action in actions:

        # ----------------------------------------------
        # Critical action
        # ----------------------------------------------

        if (
            action.priority == "Critical"
            and action.status
            not in ("Completed", "Closed")
        ):

            _create_notification(
                db=db,
                user_id=user_id,
                notification_type="critical_action",
                title="Critical Corrective Action",
                message=(
                    f"{action.title} is a critical "
                    "remediation action."
                ),
                source_type="corrective_action",
                source_id=action.id,
            )

        # ----------------------------------------------
        # Due soon
        # ----------------------------------------------

        if (
            action.status
            not in ("Completed", "Closed")
            and action.due_date is not None
            and today <= action.due_date <= due_soon_date
        ):

            _create_notification(
                db=db,
                user_id=user_id,
                notification_type="action_due_soon",
                title="Corrective Action Due Soon",
                message=(
                    f"{action.title} is due on "
                    f"{action.due_date.isoformat()}."
                ),
                source_type="corrective_action_due",
                source_id=action.id,
            )

        # ----------------------------------------------
        # Overdue
        # ----------------------------------------------

        if (
            action.status
            not in ("Completed", "Closed")
            and action.due_date is not None
            and action.due_date < today
        ):

            _create_notification(
                db=db,
                user_id=user_id,
                notification_type="action_overdue",
                title="Corrective Action Overdue",
                message=(
                    f"{action.title} was due on "
                    f"{action.due_date.isoformat()}."
                ),
                source_type="corrective_action_overdue",
                source_id=action.id,
            )

        # ----------------------------------------------
        # Completed
        # ----------------------------------------------

        if action.status == "Completed":

            _create_notification(
                db=db,
                user_id=user_id,
                notification_type="action_completed",
                title="Corrective Action Completed",
                message=(
                    f"{action.title} has been completed."
                ),
                source_type="corrective_action_completed",
                source_id=action.id,
            )

    db.commit()


def get_notifications(
    db: Session,
    user_id: int,
):
    """
    Return the latest notifications for a user.
    """

    sync_notifications(
        db,
        user_id,
    )

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .limit(20)
        .all()
    )


def get_unread_count(
    db: Session,
    user_id: int,
):
    """
    Return unread notification count.
    """

    sync_notifications(
        db,
        user_id,
    )

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .count()
    )


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