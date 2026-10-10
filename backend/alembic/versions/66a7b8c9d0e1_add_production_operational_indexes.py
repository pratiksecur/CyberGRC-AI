"""add production operational indexes

Revision ID: 66a7b8c9d0e1
Revises: 65f6a7b8c9d0
Create Date: 2026-10-08
"""

from alembic import op


revision = "66a7b8c9d0e1"
down_revision = "65f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_corrective_actions_status_due_date",
        "corrective_actions",
        ["status", "due_date"],
        unique=False,
    )

    op.create_index(
        "ix_risks_status",
        "risks",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_notifications_user_read_created",
        "notifications",
        ["user_id", "is_read", "created_at"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_notifications_user_read_created",
        table_name="notifications",
    )
    op.drop_index(
        "ix_risks_status",
        table_name="risks",
    )
    op.drop_index(
        "ix_corrective_actions_status_due_date",
        table_name="corrective_actions",
    )
