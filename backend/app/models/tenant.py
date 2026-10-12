"""Shared helper that keeps tenant-owned rows tied to an organization."""

from sqlalchemy import select

from app.database.database import Base


def inherit_organization(connection, target, *sources):
    """
    Fill ``target.organization_id`` from the first source that has one.

    Each source is a ``(table_name, row_id)`` pair, for example
    ``("users", target.owner_id)`` or ``("audits", target.audit_id)``.
    Sources are tried in order. A row that already has an organization is
    left alone.

    If no source resolves, the column stays empty and the database rejects
    the insert (NOT NULL), so a tenant-owned row can never be stored
    without an organization.
    """

    if target.organization_id is not None:
        return

    tables = Base.metadata.tables

    for table_name, row_id in sources:
        if row_id is None:
            continue

        table = tables[table_name]

        organization_id = connection.execute(
            select(table.c.organization_id).where(
                table.c.id == row_id
            )
        ).scalar_one_or_none()

        if organization_id is not None:
            target.organization_id = organization_id
            return