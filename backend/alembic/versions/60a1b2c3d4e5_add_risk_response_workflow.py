"""Add governed risk response workflow records.

Revision ID: 60a1b2c3d4e5
Revises: 59b1b2c3d4e5
Create Date: 2026-10-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "60a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "59b1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_response_workflows",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "execution_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "decision_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "risk_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "workflow_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "target_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "target_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_by_id",
            sa.Integer(),
            nullable=False,
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
        sa.ForeignKeyConstraint(
            ["execution_id"],
            ["risk_response_executions.id"],
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
            ["created_by_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "execution_id",
            name="uq_risk_response_workflows_execution_id",
        ),
    )

    op.create_index(
        op.f("ix_risk_response_workflows_id"),
        "risk_response_workflows",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_workflows_execution_id"),
        "risk_response_workflows",
        ["execution_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_risk_response_workflows_decision_id"),
        "risk_response_workflows",
        ["decision_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_workflows_risk_id"),
        "risk_response_workflows",
        ["risk_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_workflows_workflow_type"),
        "risk_response_workflows",
        ["workflow_type"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_workflows_status"),
        "risk_response_workflows",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_workflows_target_id"),
        "risk_response_workflows",
        ["target_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_risk_response_workflows_created_by_id"),
        "risk_response_workflows",
        ["created_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_risk_response_workflows_created_by_id"),
        table_name="risk_response_workflows",
    )

    op.drop_index(
        op.f("ix_risk_response_workflows_target_id"),
        table_name="risk_response_workflows",
    )

    op.drop_index(
        op.f("ix_risk_response_workflows_status"),
        table_name="risk_response_workflows",
    )

    op.drop_index(
        op.f("ix_risk_response_workflows_workflow_type"),
        table_name="risk_response_workflows",
    )

    op.drop_index(
        op.f("ix_risk_response_workflows_risk_id"),
        table_name="risk_response_workflows",
    )

    op.drop_index(
        op.f("ix_risk_response_workflows_decision_id"),
        table_name="risk_response_workflows",
    )

    op.drop_index(
        op.f("ix_risk_response_workflows_execution_id"),
        table_name="risk_response_workflows",
    )

    op.drop_index(
        op.f("ix_risk_response_workflows_id"),
        table_name="risk_response_workflows",
    )

    op.drop_table("risk_response_workflows")