from sqlalchemy.orm import Session

from app.models.user import User
from app.models.risk import Risk
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction


# ==========================================================
# USER HIERARCHY
# ==========================================================

def _get_management_chain(
    db: Session,
    user_id: int,
) -> set[int]:
    """
    Return the user and every manager above them.

    Example:

        Risk Analyst
             ↓
        GRC Manager
             ↓
           Admin

    Result:

        {Risk Analyst, GRC Manager, Admin}
    """

    recipients: set[int] = set()

    current_user_id = user_id
    visited: set[int] = set()

    while current_user_id is not None:

        # Prevent accidental infinite loops if the hierarchy
        # contains corrupted/circular manager relationships.
        if current_user_id in visited:
            break

        visited.add(current_user_id)
        recipients.add(current_user_id)

        user = (
            db.query(User)
            .filter(
                User.id == current_user_id
            )
            .first()
        )

        if user is None:
            break

        current_user_id = user.manager_id

    return recipients


def _add_user(
    recipients: set[int],
    user_id: int | None,
):
    """
    Add a valid user ID to a recipient set.
    """

    if user_id is not None:
        recipients.add(user_id)


# ==========================================================
# RISK RECIPIENTS
# ==========================================================

def get_risk_recipients(
    db: Session,
    risk: Risk,
) -> set[int]:
    """
    Determine who should receive a notification
    for a critical risk.

    Recipients:

    - Risk owner
    - Owner's management chain
    """

    recipients: set[int] = set()

    if risk.owner_id is not None:

        recipients.update(
            _get_management_chain(
                db,
                risk.owner_id,
            )
        )

    return recipients


# ==========================================================
# AUDIT RECIPIENTS
# ==========================================================

def get_audit_recipients(
    db: Session,
    audit: Audit,
) -> set[int]:
    """
    Determine who should receive an audit notification.

    Recipients:

    - Assigned auditor
    - Audit creator
    - Creator's management chain
    """

    recipients: set[int] = set()

    # Assigned auditor
    _add_user(
        recipients,
        audit.auditor_id,
    )

    # Audit creator and management chain
    if audit.created_by_id is not None:

        recipients.update(
            _get_management_chain(
                db,
                audit.created_by_id,
            )
        )

    return recipients


# ==========================================================
# AUDIT FINDING RECIPIENTS
# ==========================================================

def get_finding_recipients(
    db: Session,
    finding: AuditFinding,
) -> set[int]:
    """
    Determine who should receive a critical finding notification.

    Recipients:

    - Assigned auditor
    - Control owner
    - Control owner's management chain
    - Audit creator
    - Audit creator's management chain

    The Audit remains the primary source of audit accountability.
    """

    recipients: set[int] = set()

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == finding.audit_id
        )
        .first()
    )

    if audit is not None:

        # Auditor responsible for the audit
        _add_user(
            recipients,
            audit.auditor_id,
        )

        # Audit creator and management chain
        if audit.created_by_id is not None:

            recipients.update(
                _get_management_chain(
                    db,
                    audit.created_by_id,
                )
            )

    # Control owner
    if finding.control_id is not None:

        from app.models.control import Control

        control = (
            db.query(Control)
            .filter(
                Control.id == finding.control_id
            )
            .first()
        )

        if control is not None:

            recipients.update(
                _get_management_chain(
                    db,
                    control.owner_id,
                )
            )

    return recipients


# ==========================================================
# CORRECTIVE ACTION RECIPIENTS
# ==========================================================

def get_corrective_action_recipients(
    db: Session,
    action: CorrectiveAction,
) -> set[int]:
    """
    Determine who should receive a corrective-action notification.

    Recipients:

    - Action assignee
    - Assignee's management chain
    - Audit auditor
    - Audit creator and their management chain
    - Control owner and their management chain

    This keeps remediation accountability visible to the
    people directly responsible for the action and its
    originating audit/finding.
    """

    recipients: set[int] = set()

    # ------------------------------------------------------
    # Assignee + management chain
    # ------------------------------------------------------

    if action.assigned_to is not None:

        recipients.update(
            _get_management_chain(
                db,
                action.assigned_to,
            )
        )

    # ------------------------------------------------------
    # Finding
    # ------------------------------------------------------

    finding = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.id == action.finding_id
        )
        .first()
    )

    if finding is None:
        return recipients

    # ------------------------------------------------------
    # Audit context
    # ------------------------------------------------------

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == finding.audit_id
        )
        .first()
    )

    if audit is not None:

        # Auditor
        _add_user(
            recipients,
            audit.auditor_id,
        )

        # Audit creator + management chain
        if audit.created_by_id is not None:

            recipients.update(
                _get_management_chain(
                    db,
                    audit.created_by_id,
                )
            )

    # ------------------------------------------------------
    # Control context
    # ------------------------------------------------------

    if finding.control_id is not None:

        from app.models.control import Control

        control = (
            db.query(Control)
            .filter(
                Control.id == finding.control_id
            )
            .first()
        )

        if control is not None:

            recipients.update(
                _get_management_chain(
                    db,
                    control.owner_id,
                )
            )

    return recipients