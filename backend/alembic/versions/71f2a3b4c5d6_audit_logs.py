"""Audit trail: audit_logs

Revision ID: 71f2a3b4c5d6
Revises: 70e1f2a3b4c5
Create Date: 2026-10-13 09:00:00.000000

Append-only record of who created, changed or deleted which record. Entries
are written automatically by the application; existing data is not
back-filled, so the trail starts from the moment this migration is applied.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "71f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "70e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if "audit_logs" in inspector.get_table_names():
        return

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=True),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index(
        "ix_audit_logs_org_created",
        "audit_logs",
        ["organization_id", "created_at"],
    )
    op.create_index(
        "ix_audit_logs_entity",
        "audit_logs",
        ["entity_type", "entity_id"],
    )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if "audit_logs" in inspector.get_table_names():
        op.drop_table("audit_logs")