"""add risk response workflow lifecycle

Revision ID: 60b1c2d3e4f5
Revises: 60a1b2c3d4e5
Create Date: 2026-10-01
"""

from alembic import op
import sqlalchemy as sa


revision = "60b1c2d3e4f5"
down_revision = "60a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "risk_response_workflows",
        sa.Column(
            "updated_by_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "risk_response_workflows",
        sa.Column(
            "resolution_reason",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "risk_response_workflows",
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "risk_response_workflows",
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "risk_response_workflows",
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_risk_response_workflows_updated_by_id_users",
        "risk_response_workflows",
        "users",
        ["updated_by_id"],
        ["id"],
    )

    op.create_index(
        "ix_risk_response_workflows_updated_by_id",
        "risk_response_workflows",
        ["updated_by_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_risk_response_workflows_updated_by_id",
        table_name="risk_response_workflows",
    )

    op.drop_constraint(
        "fk_risk_response_workflows_updated_by_id_users",
        "risk_response_workflows",
        type_="foreignkey",
    )

    op.drop_column(
        "risk_response_workflows",
        "cancelled_at",
    )

    op.drop_column(
        "risk_response_workflows",
        "completed_at",
    )

    op.drop_column(
        "risk_response_workflows",
        "started_at",
    )

    op.drop_column(
        "risk_response_workflows",
        "resolution_reason",
    )

    op.drop_column(
        "risk_response_workflows",
        "updated_by_id",
    )