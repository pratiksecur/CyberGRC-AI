"""Add notification event identity.

Revision ID: 58a1b2c3d4e5
Revises: 55a1b2c3d4e5, add_notifications
Create Date: 2026-09-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "58a1b2c3d4e5"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = (
    "55a1b2c3d4e5",
    "add_notifications",
)

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------
    # Add event identity
    # ------------------------------------------------------

    op.add_column(
        "notifications",
        sa.Column(
            "event_key",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # ------------------------------------------------------
    # Backfill existing notifications
    #
    # Existing notification behavior was effectively based on:
    #
    # user_id + type + source_type + source_id
    #
    # Preserve that identity using a deterministic legacy key.
    # ------------------------------------------------------

    notifications = sa.table(
        "notifications",
        sa.column("id", sa.Integer()),
        sa.column("type", sa.String(length=50)),
        sa.column("source_type", sa.String(length=50)),
        sa.column("source_id", sa.Integer()),
        sa.column("event_key", sa.String(length=255)),
    )

    op.execute(
        sa.text(
            """
            UPDATE notifications
            SET event_key =
                'legacy:'
                || type
                || ':'
                || source_type
                || ':'
                || source_id
            WHERE event_key IS NULL
            """
        )
    )

    # ------------------------------------------------------
    # event_key is now mandatory
    # ------------------------------------------------------

    op.alter_column(
        "notifications",
        "event_key",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    # ------------------------------------------------------
    # Remove the old notification identity constraint
    # ------------------------------------------------------

    op.drop_constraint(
        "uq_notification_user_type_source",
        "notifications",
        type_="unique",
    )

    # ------------------------------------------------------
    # New notification event identity
    #
    # A user may receive multiple events for the same resource,
    # but never the exact same event twice.
    # ------------------------------------------------------

    op.create_unique_constraint(
        "uq_notification_user_event_key",
        "notifications",
        [
            "user_id",
            "event_key",
        ],
    )

    op.create_index(
        op.f("ix_notifications_event_key"),
        "notifications",
        ["event_key"],
        unique=False,
    )


def downgrade() -> None:
    # ------------------------------------------------------
    # Remove Phase 58 index
    # ------------------------------------------------------

    op.drop_index(
        op.f("ix_notifications_event_key"),
        table_name="notifications",
    )

    # ------------------------------------------------------
    # Restore previous uniqueness model
    # ------------------------------------------------------

    op.drop_constraint(
        "uq_notification_user_event_key",
        "notifications",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_notification_user_type_source",
        "notifications",
        [
            "user_id",
            "type",
            "source_type",
            "source_id",
        ],
    )

    # ------------------------------------------------------
    # Remove event identity
    # ------------------------------------------------------

    op.drop_column(
        "notifications",
        "event_key",
    )