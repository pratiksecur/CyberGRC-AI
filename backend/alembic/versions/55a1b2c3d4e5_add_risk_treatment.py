"""add risk treatment model

Revision ID: 55a1b2c3d4e5
Revises: 60883bf121b4
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "55a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "60883bf121b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "risk_treatments",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "risk_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "strategy",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "treatment_plan",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "target_date",
            sa.Date(),
            nullable=True,
        ),

        sa.Column(
            "residual_likelihood",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "residual_impact",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "residual_risk_score",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "acceptance_status",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "acceptance_reason",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "accepted_by_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "accepted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),

        sa.CheckConstraint(
            "strategy IN "
            "('Mitigate', 'Avoid', 'Transfer', 'Accept')",
            name="ck_risk_treatments_strategy",
        ),

        sa.CheckConstraint(
            "status IN "
            "('Planned', 'In Progress', 'Completed', 'Cancelled')",
            name="ck_risk_treatments_status",
        ),

        sa.CheckConstraint(
            "acceptance_status IN "
            "('Not Required', 'Pending', 'Approved', 'Rejected')",
            name="ck_risk_treatments_acceptance_status",
        ),

        sa.CheckConstraint(
            "residual_likelihood IS NULL OR "
            "(residual_likelihood BETWEEN 1 AND 5)",
            name="ck_risk_treatments_residual_likelihood",
        ),

        sa.CheckConstraint(
            "residual_impact IS NULL OR "
            "(residual_impact BETWEEN 1 AND 5)",
            name="ck_risk_treatments_residual_impact",
        ),

        sa.CheckConstraint(
            "residual_risk_score IS NULL OR "
            "(residual_risk_score BETWEEN 1 AND 25)",
            name="ck_risk_treatments_residual_risk_score",
        ),

        sa.ForeignKeyConstraint(
            ["risk_id"],
            ["risks.id"],
            name="fk_risk_treatments_risk_id_risks",
        ),

        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name="fk_risk_treatments_owner_id_users",
        ),

        sa.ForeignKeyConstraint(
            ["accepted_by_id"],
            ["users.id"],
            name="fk_risk_treatments_accepted_by_id_users",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        "ix_risk_treatments_id",
        "risk_treatments",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_risk_treatments_risk_id",
        "risk_treatments",
        ["risk_id"],
        unique=False,
    )

    op.create_index(
        "ix_risk_treatments_owner_id",
        "risk_treatments",
        ["owner_id"],
        unique=False,
    )

    op.create_index(
        "ix_risk_treatments_accepted_by_id",
        "risk_treatments",
        ["accepted_by_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_risk_treatments_accepted_by_id",
        table_name="risk_treatments",
    )

    op.drop_index(
        "ix_risk_treatments_owner_id",
        table_name="risk_treatments",
    )

    op.drop_index(
        "ix_risk_treatments_risk_id",
        table_name="risk_treatments",
    )

    op.drop_index(
        "ix_risk_treatments_id",
        table_name="risk_treatments",
    )

    op.drop_table(
        "risk_treatments"
    )