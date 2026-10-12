"""Tells the audit trail who is making the current request.

The signed-in user is stored on the database session, which lives exactly as
long as one request. The audit listeners read it from there, so no route
needs to pass the user around.
"""

from sqlalchemy.orm import Session


def set_audit_actor(
    db: Session,
    *,
    user_id: int | None,
    email: str | None,
    organization_id: int | None,
    ip_address: str | None,
) -> None:
    db.info["audit_actor_id"] = user_id
    db.info["audit_actor_email"] = email
    db.info["audit_organization_id"] = organization_id
    db.info["audit_ip_address"] = ip_address