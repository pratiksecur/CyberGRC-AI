"""Harden tenant enterprise configuration."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "64e5f6a7b8c9"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "63d4e5f6a7b8"

branch_labels = None

depends_on = None


def upgrade() -> None:

    # ======================================================
    # ADD TENANT CONFIGURATION FIELDS
    # ======================================================

    op.add_column(
        "enterprise_configurations",
        sa.Column(
            "critical_risk_notification_threshold",
            sa.Integer(),
            nullable=False,
            server_default="20",
        ),
    )

    op.add_column(
        "enterprise_configurations",
        sa.Column(
            "ineffective_control_threshold",
            sa.Integer(),
            nullable=False,
            server_default="50",
        ),
    )

    op.add_column(
        "enterprise_configurations",
        sa.Column(
            "treatment_residual_threshold",
            sa.Integer(),
            nullable=False,
            server_default="15",
        ),
    )

    op.add_column(
        "enterprise_configurations",
        sa.Column(
            "continuous_risk_reassessment_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    # ------------------------------------------------------
    # Remove server defaults after existing rows have been
    # safely populated.
    # ------------------------------------------------------

    op.alter_column(
        "enterprise_configurations",
        "critical_risk_notification_threshold",
        server_default=None,
    )

    op.alter_column(
        "enterprise_configurations",
        "ineffective_control_threshold",
        server_default=None,
    )

    op.alter_column(
        "enterprise_configurations",
        "treatment_residual_threshold",
        server_default=None,
    )

    op.alter_column(
        "enterprise_configurations",
        "continuous_risk_reassessment_enabled",
        server_default=None,
    )


def downgrade() -> None:

    op.drop_column(
        "enterprise_configurations",
        "continuous_risk_reassessment_enabled",
    )

    op.drop_column(
        "enterprise_configurations",
        "treatment_residual_threshold",
    )

    op.drop_column(
        "enterprise_configurations",
        "ineffective_control_threshold",
    )

    op.drop_column(
        "enterprise_configurations",
        "critical_risk_notification_threshold",
    )