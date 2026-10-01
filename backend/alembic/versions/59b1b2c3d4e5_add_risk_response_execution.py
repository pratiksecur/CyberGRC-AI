"""Add governed risk response execution records.

Revision ID: 59b1b2c3d4e5
Revises: 59a1b2c3d4e5
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "59b1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "59a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_response_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("decision_id", sa.Integer(), nullable=False),
        sa.Column("risk_id", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=50), nullable=False),
        sa.Column(
            "response_event_key",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "execution_action",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "human_approval_verified",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "response_event_verified",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "executed_by_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "execution_reason",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "result_message",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["decision_id"],
            ["risk_response_decisions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["risk_id"],
            ["risks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["executed_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "decision_id",
            name="uq_risk_response_executions_decision_id",
        ),
    )

    op.create_index(
        op.f("ix_risk_response_executions_id"),
        "risk_response_executions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_executions_decision_id"),
        "risk_response_executions",
        ["decision_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_risk_response_executions_risk_id"),
        "risk_response_executions",
        ["risk_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_executions_response_event_key"),
        "risk_response_executions",
        ["response_event_key"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_executions_status"),
        "risk_response_executions",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_executions_executed_by_id"),
        "risk_response_executions",
        ["executed_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_risk_response_executions_executed_by_id"),
        table_name="risk_response_executions",
    )

    op.drop_index(
        op.f("ix_risk_response_executions_status"),
        table_name="risk_response_executions",
    )

    op.drop_index(
        op.f("ix_risk_response_executions_response_event_key"),
        table_name="risk_response_executions",
    )

    op.drop_index(
        op.f("ix_risk_response_executions_risk_id"),
        table_name="risk_response_executions",
    )

    op.drop_index(
        op.f("ix_risk_response_executions_decision_id"),
        table_name="risk_response_executions",
    )

    op.drop_index(
        op.f("ix_risk_response_executions_id"),
        table_name="risk_response_executions",
    )

    op.drop_table("risk_response_executions")