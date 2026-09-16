from datetime import date

from sqlalchemy.orm import Session

from app.models.corrective_action import CorrectiveAction
from app.models.audit_finding import AuditFinding
from app.models.audit import Audit
from app.models.user import User


def get_corrective_action_report(
    db: Session,
    visible_user_ids: list[int],
):
    """
    Generate a corrective actions report using
    live database data limited to corrective actions
    assigned to users within the authenticated user's
    report visibility scope.
    """

    actions = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id
            == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id
            == Audit.id,
        )
        .join(
            User,
            CorrectiveAction.assigned_to
            == User.id,
        )
        .filter(
            CorrectiveAction.assigned_to.in_(
                visible_user_ids
            ),
            Audit.auditor_id.in_(
                visible_user_ids
            ),
        )
        .order_by(
            CorrectiveAction.due_date.asc(),
            CorrectiveAction.priority.desc(),
        )
        .all()
    )

    today = date.today()

    total_actions = len(actions)

    open_actions = sum(
        1
        for action in actions
        if action.status == "Open"
    )

    in_progress_actions = sum(
        1
        for action in actions
        if action.status == "In Progress"
    )

    completed_actions = sum(
        1
        for action in actions
        if action.status == "Completed"
    )

    closed_actions = sum(
        1
        for action in actions
        if action.status == "Closed"
    )

    overdue_actions = sum(
        1
        for action in actions
        if (
            action.status
            not in (
                "Completed",
                "Closed",
            )
            and action.due_date is not None
            and action.due_date < today
        )
    )

    critical_actions = sum(
        1
        for action in actions
        if action.priority == "Critical"
    )

    high_actions = sum(
        1
        for action in actions
        if action.priority == "High"
    )

    action_items = []

    for action in actions:

        is_overdue = (
            action.status
            not in (
                "Completed",
                "Closed",
            )
            and action.due_date is not None
            and action.due_date < today
        )

        action_items.append(
            {
                "id": action.id,

                "finding_id": action.finding_id,

                "finding_title": (
                    action.finding.title
                ),

                "assigned_to": action.assigned_to,

                "assignee_name": (
                    action.assignee.full_name
                ),

                "title": action.title,

                "description": action.description,

                "priority": action.priority,

                "status": action.status,

                "due_date": action.due_date,

                "completed_at": (
                    action.completed_at
                ),

                "comments": action.comments,

                "created_at": action.created_at,

                "updated_at": action.updated_at,

                "overdue": is_overdue,
            }
        )

    return {
        "summary": {
            "total_actions": total_actions,

            "open_actions": open_actions,

            "in_progress_actions": (
                in_progress_actions
            ),

            "completed_actions": (
                completed_actions
            ),

            "closed_actions": closed_actions,

            "overdue_actions": overdue_actions,

            "critical_actions": critical_actions,

            "high_actions": high_actions,
        },

        "actions": action_items,
    }