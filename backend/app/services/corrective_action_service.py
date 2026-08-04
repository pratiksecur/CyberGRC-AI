from sqlalchemy.orm import Session

from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.user import User

from app.schemas.corrective_action import (
    CorrectiveActionCreate,
    CorrectiveActionUpdate,
)


def create_corrective_action(
    db: Session,
    action_data: CorrectiveActionCreate
):
    """
    Create a new corrective action.
    """

    finding = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.id == action_data.finding_id
        )
        .first()
    )

    if finding is None:
        return "FINDING_NOT_FOUND"

    assignee = (
        db.query(User)
        .filter(
            User.id == action_data.assigned_to
        )
        .first()
    )

    if assignee is None:
        return "USER_NOT_FOUND"

    if (
        action_data.completed_at is not None
        and action_data.completed_at < action_data.due_date
    ):
        return "INVALID_DATES"

    action = CorrectiveAction(
        finding_id=action_data.finding_id,
        assigned_to=action_data.assigned_to,
        title=action_data.title,
        description=action_data.description,
        priority=action_data.priority.value,
        status=action_data.status.value,
        due_date=action_data.due_date,
        completed_at=action_data.completed_at,
        comments=action_data.comments,
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    return action


def get_all_corrective_actions(db: Session):
    """
    Get all corrective actions.
    """

    return db.query(CorrectiveAction).all()


def get_corrective_action_by_id(
    db: Session,
    action_id: int
):
    """
    Get corrective action by ID.
    """

    return (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.id == action_id
        )
        .first()
    )


def update_corrective_action(
    db: Session,
    action_id: int,
    action_data: CorrectiveActionUpdate
):
    """
    Update a corrective action.
    """

    action = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.id == action_id
        )
        .first()
    )

    if action is None:
        return None

    if action_data.title is not None:
        action.title = action_data.title

    if action_data.description is not None:
        action.description = action_data.description

    if action_data.priority is not None:
        action.priority = action_data.priority.value

    if action_data.status is not None:
        action.status = action_data.status.value

    if action_data.due_date is not None:
        action.due_date = action_data.due_date

    if action_data.completed_at is not None:
        action.completed_at = action_data.completed_at

    if action_data.comments is not None:
        action.comments = action_data.comments

    if (
        action.completed_at is not None
        and action.completed_at < action.due_date
    ):
        return "INVALID_DATES"

    db.commit()
    db.refresh(action)

    return action


def delete_corrective_action(
    db: Session,
    action_id: int
):
    """
    Delete a corrective action.
    """

    action = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.id == action_id
        )
        .first()
    )

    if action is None:
        return None

    db.delete(action)
    db.commit()

    return True