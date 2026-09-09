"""add audit creator attribution

Revision ID: 60883bf121b4
Revises: a33dd102e6c2
Create Date: 2026-09-02 17:58:23.212283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "60883bf121b4"
down_revision: Union[str, Sequence[str], None] = "a33dd102e6c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the column temporarily as nullable so existing
    # audit records can be safely backfilled.
    op.add_column(
        "audits",
        sa.Column(
            "created_by_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Existing audits predate creator attribution.
    # Use the existing auditor as the historical creator.
    op.execute(
        """
        UPDATE audits
        SET created_by_id = auditor_id
        WHERE created_by_id IS NULL
        """
    )

    # Add the foreign key after the existing records
    # have been populated.
    op.create_foreign_key(
        "fk_audits_created_by_id_users",
        "audits",
        "users",
        ["created_by_id"],
        ["id"],
    )

    # Enforce creator attribution for all future audits.
    op.alter_column(
        "audits",
        "created_by_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_audits_created_by_id_users",
        "audits",
        type_="foreignkey",
    )

    op.drop_column(
        "audits",
        "created_by_id",
    )