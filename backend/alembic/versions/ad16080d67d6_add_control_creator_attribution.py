"""Add control creator attribution

Revision ID: ad16080d67d6
Revises: 23d39ce150cc
Create Date: 2026-09-02 12:28:48.663985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ad16080d67d6"
down_revision: Union[str, Sequence[str], None] = "23d39ce150cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add the column as nullable so existing controls
    #    can be safely backfilled.
    op.add_column(
        "controls",
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )

    # 2. Backfill existing controls.
    #    Existing controls were created under the owner model,
    #    so use owner_id as the historical creator.
    op.execute(
        """
        UPDATE controls
        SET created_by_id = owner_id
        WHERE created_by_id IS NULL
        """
    )

    # 3. Add the foreign key relationship.
    op.create_foreign_key(
        "fk_controls_created_by_id_users",
        "controls",
        "users",
        ["created_by_id"],
        ["id"],
    )

    # 4. Require creator attribution for all controls.
    op.alter_column(
        "controls",
        "created_by_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_controls_created_by_id_users",
        "controls",
        type_="foreignkey",
    )

    op.drop_column(
        "controls",
        "created_by_id"
    )