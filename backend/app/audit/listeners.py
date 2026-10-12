"""Automatic audit trail.

SQLAlchemy tells us whenever a row of an audited model is inserted, updated
or deleted. For each one we add a row to ``audit_logs`` using the same
database connection, so the log entry and the change are saved together or
not at all.

Who did it comes from the database session (see app/audit/actor.py). Work
done without a signed-in user, such as the scheduler, is recorded with no
actor.

Not covered: bulk statements such as ``query.update(...)`` or
``query.delete()``, which do not go through the ORM.
"""

import enum
import logging
from datetime import date, datetime, timezone

from sqlalchemy import event, inspect, select
from sqlalchemy.orm import object_session

from app.models.audit_log import AuditLog
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.business_unit import BusinessUnit
from app.models.control import Control
from app.models.control_framework_control import ControlFrameworkControl
from app.models.corrective_action import CorrectiveAction
from app.models.department import Department
from app.models.enterprise_configuration import EnterpriseConfiguration
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.grc_team import GrcTeam
from app.models.policy import Policy
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_response_decision import RiskResponseDecisionRecord
from app.models.risk_response_execution import RiskResponseExecutionRecord
from app.models.risk_response_workflow import RiskResponseWorkflowRecord
from app.models.risk_treatment import RiskTreatment
from app.models.user import User


logger = logging.getLogger("cybergrc.audit")

AUDITED_MODELS = (
    User,
    Risk,
    RiskTreatment,
    RiskControl,
    Control,
    ControlFrameworkControl,
    Framework,
    Evidence,
    Audit,
    AuditFinding,
    CorrectiveAction,
    Policy,
    RiskResponseDecisionRecord,
    RiskResponseExecutionRecord,
    RiskResponseWorkflowRecord,
    EnterpriseConfiguration,
    BusinessUnit,
    Department,
    GrcTeam,
)

# Only the fact that it changed is logged, never the value.
SECRET_FIELDS = frozenset({"hashed_password"})

# Bookkeeping columns. A change to these alone is not worth a log entry
# (token_version moves on every logout; a password change is already
# logged through hashed_password).
IGNORED_FIELDS = frozenset(
    {
        "created_at",
        "updated_at",
        "token_version",
        "password_changed_at",
    }
)

MAX_VALUE_LENGTH = 300


def _plain(value):
    """Turn a column value into something JSON can store."""

    if value is None or isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, enum.Enum):
        return _plain(value.value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    text = str(value)

    if len(text) > MAX_VALUE_LENGTH:
        return text[: MAX_VALUE_LENGTH - 1] + "…"

    return text


def _label(target) -> str:
    for field in ("title", "name", "full_name", "email"):
        value = getattr(target, field, None)

        if value:
            return str(value)[:120]

    return ""


def _entity_id(target, mapper) -> str | None:
    # The identity key is not set yet while an insert is being flushed, so
    # read the primary key straight from the object.
    identity = mapper.primary_key_from_instance(target)

    if not identity or all(part is None for part in identity):
        return None

    return "-".join(str(part) for part in identity)


def _snapshot(target, mapper) -> dict:
    values = {}

    for attribute in mapper.column_attrs:
        key = attribute.key

        if key in SECRET_FIELDS or key in IGNORED_FIELDS:
            continue

        value = getattr(target, key, None)

        if value is not None:
            values[key] = _plain(value)

    return values


def _stored_values(connection, mapper, target) -> dict:
    """
    The row as it is in the database right now, before this update.

    SQLAlchemy only remembers an attribute's old value if it was loaded when
    it was changed, and after a commit it usually is not. Reading the row
    here, just before the UPDATE runs, always gives the true old value.
    """

    table = mapper.local_table

    conditions = [
        column == getattr(
            target, mapper.get_property_by_column(column).key
        )
        for column in mapper.primary_key
    ]

    row = connection.execute(
        select(table).where(*conditions)
    ).first()

    if row is None:
        return {}

    values = {}

    for attribute in mapper.column_attrs:
        column = attribute.columns[0]

        if column in row._mapping:
            values[attribute.key] = row._mapping[column]

    return values


def _changes(target, mapper, stored: dict) -> dict:
    state = inspect(target)
    changes = {}

    for attribute in mapper.column_attrs:
        key = attribute.key

        if key in IGNORED_FIELDS:
            continue

        history = state.attrs[key].history

        if not history.has_changes():
            continue

        new = history.added[0] if history.added else None

        if key in stored:
            old = stored[key]
            known = True
        elif history.deleted:
            old = history.deleted[0]
            known = True
        else:
            old = None
            known = False

        if known and old == new:
            continue

        if key in SECRET_FIELDS:
            changes[key] = {"to": "[changed]"}
            continue

        entry = {"to": _plain(new)}

        if known:
            entry["from"] = _plain(old)

        changes[key] = entry

    return changes


def _user_action(changes: dict) -> str:
    """More useful names for the account events people look for."""

    if "hashed_password" in changes:
        return "password_changed"

    if "is_active" in changes:
        return "activated" if changes["is_active"]["to"] else "deactivated"

    if "role" in changes:
        return "role_changed"

    return "updated"


def _write(
    connection,
    mapper,
    target,
    action: str,
    details: dict | None,
) -> None:
    session = object_session(target)
    info = session.info if session is not None else {}

    organization_id = getattr(target, "organization_id", None)

    if organization_id is None:
        organization_id = info.get("audit_organization_id")

    if organization_id is None:
        # Cannot be assigned to a tenant, so it cannot be shown to anyone.
        return

    table_name = target.__tablename__
    label = _label(target)
    noun = table_name.replace("_", " ")

    if action == "password_changed":
        summary = f"Password changed for {label}".strip()
    elif action in ("activated", "deactivated", "role_changed"):
        summary = f"User {label} {action.replace('_', ' ')}".strip()
    else:
        summary = f"{noun.capitalize()} {action}"

        if label:
            summary += f": {label}"

    connection.execute(
        AuditLog.__table__.insert().values(
            organization_id=organization_id,
            actor_id=info.get("audit_actor_id"),
            actor_email=info.get("audit_actor_email"),
            action=action,
            entity_type=table_name,
            entity_id=_entity_id(target, mapper),
            summary=summary[:500],
            details=details,
            ip_address=info.get("audit_ip_address"),
            created_at=datetime.now(timezone.utc),
        )
    )


def _safely(function):
    """A problem with the log must never break the request itself."""

    def wrapper(mapper, connection, target):
        try:
            function(mapper, connection, target)
        except Exception:  # pragma: no cover - defensive
            logger.exception(
                "Could not write the audit log entry for %s",
                type(target).__name__,
            )

    return wrapper


@_safely
def _after_insert(mapper, connection, target):
    _write(
        connection,
        mapper,
        target,
        "created",
        {"values": _snapshot(target, mapper)},
    )


@_safely
def _before_update(mapper, connection, target):
    state = inspect(target)

    if any(
        state.attrs[attribute.key].history.has_changes()
        for attribute in mapper.column_attrs
        if attribute.key not in IGNORED_FIELDS
    ):
        state.info["audit_stored_values"] = _stored_values(
            connection, mapper, target
        )


@_safely
def _after_update(mapper, connection, target):
    stored = inspect(target).info.pop("audit_stored_values", {})

    changes = _changes(target, mapper, stored)

    if not changes:
        return

    action = "updated"

    if isinstance(target, User):
        action = _user_action(changes)

    _write(connection, mapper, target, action, {"changes": changes})


@_safely
def _before_delete(mapper, connection, target):
    _write(
        connection,
        mapper,
        target,
        "deleted",
        {"values": _snapshot(target, mapper)},
    )


def register() -> None:
    for model in AUDITED_MODELS:
        event.listen(model, "after_insert", _after_insert)
        event.listen(model, "before_update", _before_update)
        event.listen(model, "after_update", _after_update)
        event.listen(model, "before_delete", _before_delete)


register()