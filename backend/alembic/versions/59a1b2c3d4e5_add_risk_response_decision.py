"""Add governed risk response decisions.

Revision ID: 59a1b2c3d4e5
Revises: 58a1b2c3d4e5
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "59a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "58a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_response_decisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("risk_id", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column(
            "governance_level",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "human_approval_required",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "response_event_key",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "reason_codes",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "risk_state",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "treatment_state",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "reassessment_required",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "response_required",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "requested_by_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "assigned_to_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "resolution_reason",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "deferred_until",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["risk_id"],
            ["risks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["assigned_to_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_risk_response_decisions_id"),
        "risk_response_decisions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_decisions_risk_id"),
        "risk_response_decisions",
        ["risk_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_decisions_status"),
        "risk_response_decisions",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_decisions_response_event_key"),
        "risk_response_decisions",
        ["response_event_key"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_decisions_requested_by_id"),
        "risk_response_decisions",
        ["requested_by_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_decisions_assigned_to_id"),
        "risk_response_decisions",
        ["assigned_to_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_risk_response_decisions_assigned_to_id"),
        table_name="risk_response_decisions",
    )

    op.drop_index(
        op.f("ix_risk_response_decisions_requested_by_id"),
        table_name="risk_response_decisions",
    )

    op.drop_index(
        op.f("ix_risk_response_decisions_response_event_key"),
        table_name="risk_response_decisions",
    )

    op.drop_index(
        op.f("ix_risk_response_decisions_status"),
        table_name="risk_response_decisions",
    )

    op.drop_index(
        op.f("ix_risk_response_decisions_risk_id"),
        table_name="risk_response_decisions",
    )

    op.drop_index(
        op.f("ix_risk_response_decisions_id"),
        table_name="risk_response_decisions",
    )

    op.drop_table("risk_response_decisions")