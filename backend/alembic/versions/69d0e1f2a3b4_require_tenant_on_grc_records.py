"""Require an organization on every control, audit, finding, action and evidence

Revision ID: 69d0e1f2a3b4
Revises: 68c9d0e1f2a3
Create Date: 2026-10-12 21:00:00.000000

These tables were created with a nullable organization_id so older rows could
be backfilled. The backfill has long been done, and the models now declare the
column NOT NULL so a record can never exist without a tenant.

Any row that still has no organization takes it from its parent record, in
this order of preference:

  controls            owner, then creator
  audits              auditor, then creator
  audit_findings      audit, then control
  corrective_actions  finding, then assignee
  evidence            control, then uploader

If a row still cannot be resolved, the migration stops before changing
anything, and lists how many rows are affected per table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "69d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "68c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, [(parent table, column on this table that points at the parent)])
# The order matters: a parent table is always filled in before its children.
TABLES = [
    ("controls", [("users", "owner_id"), ("users", "created_by_id")]),
    ("audits", [("users", "auditor_id"), ("users", "created_by_id")]),
    ("audit_findings", [("audits", "audit_id"), ("controls", "control_id")]),
    (
        "corrective_actions",
        [("audit_findings", "finding_id"), ("users", "assigned_to")],
    ),
    ("evidence", [("controls", "control_id"), ("users", "uploaded_by")]),
]


def _is_nullable(table: str) -> bool:
    inspector = sa.inspect(op.get_bind())

    for column in inspector.get_columns(table):
        if column["name"] == "organization_id":
            return bool(column["nullable"])

    raise RuntimeError(f"{table}.organization_id does not exist.")


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing = set(inspector.get_table_names())

    pending = [
        (table, parents)
        for table, parents in TABLES
        if table in existing and _is_nullable(table)
    ]

    if not pending:
        return

    for table, parents in pending:
        for parent, column in parents:
            op.execute(
                sa.text(
                    f"""
                    UPDATE {table} AS child
                    SET organization_id = parent.organization_id
                    FROM {parent} AS parent
                    WHERE parent.id = child.{column}
                      AND child.organization_id IS NULL
                      AND parent.organization_id IS NOT NULL
                    """
                )
            )

    unresolved = []

    for table, _ in pending:
        remaining = op.get_bind().execute(
            sa.text(
                f"SELECT COUNT(*) FROM {table} WHERE organization_id IS NULL"
            )
        ).scalar_one()

        if remaining:
            unresolved.append(f"{table}: {remaining}")

    if unresolved:
        raise RuntimeError(
            "Some rows have no organization and no parent record to take "
            "one from (" + ", ".join(unresolved) + "). Assign an "
            "organization to them, then run the migration again."
        )

    for table, _ in pending:
        op.alter_column(
            table,
            "organization_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:
    for table, _ in reversed(TABLES):
        op.alter_column(
            table,
            "organization_id",
            existing_type=sa.Integer(),
            nullable=True,
        )