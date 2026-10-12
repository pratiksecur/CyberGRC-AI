"""Initial migration

Revision ID: 506d57a2f2bf
Revises:
Create Date: 2026-07-31 10:48:33.980233

Creates the base ``users`` table as it existed before any later revision.

Earlier versions of this revision were empty because the first tables were
created with ``Base.metadata.create_all``. That made it impossible to build
the schema from an empty database with ``alembic upgrade head``. Databases
that already hold a ``users`` table are left untouched.

Columns added by later revisions (updated_at, organization_id, the
enterprise structure ids, ...) are intentionally NOT created here.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '506d57a2f2bf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    inspector = sa.inspect(op.get_bind())

    if inspector.has_table("users"):
        return

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=True),
        # Hierarchy columns; revision 40436fbc19af documents that they
        # already existed in the original schema.
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")