"""Require an organization on every risk

Revision ID: 68c9d0e1f2a3
Revises: 67b8c9d0e1f2
Create Date: 2026-10-12 19:00:00.000000

risks.organization_id was created nullable so that older rows could be
backfilled. The backfill has long been done, and the model now declares the
column NOT NULL so a risk can never exist without a tenant.

Any row that still has no organization takes the organization of its owner
(or, failing that, of its creator). If a row still cannot be resolved the
migration stops with a clear message instead of guessing a tenant.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "68c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "67b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_nullable() -> bool:
    inspector = sa.inspect(op.get_bind())

    for column in inspector.get_columns("risks"):
        if column["name"] == "organization_id":
            return bool(column["nullable"])

    raise RuntimeError("risks.organization_id does not exist.")


def upgrade() -> None:
    if not _is_nullable():
        return

    op.execute(
        sa.text(
            """
            UPDATE risks AS r
            SET organization_id = u.organization_id
            FROM users AS u
            WHERE u.id = r.owner_id
              AND r.organization_id IS NULL
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE risks AS r
            SET organization_id = u.organization_id
            FROM users AS u
            WHERE u.id = r.created_by_id
              AND r.organization_id IS NULL
            """
        )
    )

    remaining = op.get_bind().execute(
        sa.text(
            "SELECT COUNT(*) FROM risks WHERE organization_id IS NULL"
        )
    ).scalar_one()

    if remaining:
        raise RuntimeError(
            f"{remaining} risk(s) have no organization and no owner or "
            "creator to take one from. Assign an organization to them, "
            "then run the migration again."
        )

    op.alter_column(
        "risks",
        "organization_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "risks",
        "organization_id",
        existing_type=sa.Integer(),
        nullable=True,
    )