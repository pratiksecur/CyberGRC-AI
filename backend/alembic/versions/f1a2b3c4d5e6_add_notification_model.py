"""Add notification model

Revision ID: add_notifications
Revises: e1319b9ef186
Create Date: 2026-08-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_notifications"

down_revision: Union[str, Sequence[str], None] = "e1319b9ef186"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "notifications",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "source_type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "source_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "user_id",
            "type",
            "source_type",
            "source_id",
            name="uq_notification_user_type_source",
        ),
    )

    op.create_index(
        op.f("ix_notifications_id"),
        "notifications",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_notifications_user_id"),
        table_name="notifications",
    )

    op.drop_index(
        op.f("ix_notifications_id"),
        table_name="notifications",
    )

    op.drop_table("notifications")