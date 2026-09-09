"""Add risk creator attribution

Revision ID: 23d39ce150cc
Revises: 40436fbc19af
Create Date: 2026-09-02 11:47:47.877806

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "23d39ce150cc"
down_revision: Union[str, Sequence[str], None] = "40436fbc19af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the column as nullable first so existing records can be
    # populated safely.
    op.add_column(
        "risks",
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )

    # Backfill existing risks using their current owner as the
    # historical creator.
    op.execute(
        """
        UPDATE risks
        SET created_by_id = owner_id
        WHERE created_by_id IS NULL
        """
    )

    # Add the foreign key relationship.
    op.create_foreign_key(
        "fk_risks_created_by_id_users",
        "risks",
        "users",
        ["created_by_id"],
        ["id"],
    )

    # Enforce creator attribution for all future risk records.
    op.alter_column(
        "risks",
        "created_by_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_risks_created_by_id_users",
        "risks",
        type_="foreignkey",
    )

    op.drop_column("risks", "created_by_id")