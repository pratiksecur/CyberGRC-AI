"""add tenant frameworks and policies

Revision ID: 65f6a7b8c9d0
Revises: 64e5f6a7b8c9
Create Date: 2026-10-07
"""

from alembic import op
import sqlalchemy as sa


revision = "65f6a7b8c9d0"
down_revision = "64e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================
    # FRAMEWORK TENANCY
    # =========================================================

    op.add_column(
        "frameworks",
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_frameworks_organization_id",
        "frameworks",
        ["organization_id"],
        unique=False,
    )

    # Existing frameworks belong to the default organization.
    op.execute(
        """
        UPDATE frameworks
        SET organization_id = 1
        WHERE organization_id IS NULL
        """
    )

    op.alter_column(
        "frameworks",
        "organization_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_foreign_key(
        "fk_frameworks_organization_id",
        "frameworks",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Existing global uniqueness becomes tenant-scoped.
    op.drop_constraint(
        "frameworks_name_key",
        "frameworks",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_frameworks_organization_name",
        "frameworks",
        [
            "organization_id",
            "name",
        ],
    )

    # =========================================================
    # POLICIES
    # =========================================================

    op.create_table(
        "policies",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "version",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="Draft",
        ),

        sa.Column(
            "effective_date",
            sa.Date(),
            nullable=True,
        ),

        sa.Column(
            "review_date",
            sa.Date(),
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

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_policies_organization_id",
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name="fk_policies_owner_id",
            ondelete="RESTRICT",
        ),

        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_policies_organization_name",
        ),
    )

    op.create_index(
        "ix_policies_id",
        "policies",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_policies_organization_id",
        "policies",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_policies_owner_id",
        "policies",
        ["owner_id"],
        unique=False,
    )


def downgrade():

    # =========================================================
    # POLICIES
    # =========================================================

    op.drop_index(
        "ix_policies_owner_id",
        table_name="policies",
    )

    op.drop_index(
        "ix_policies_organization_id",
        table_name="policies",
    )

    op.drop_index(
        "ix_policies_id",
        table_name="policies",
    )

    op.drop_table("policies")

    # =========================================================
    # FRAMEWORKS
    # =========================================================

    op.drop_constraint(
        "uq_frameworks_organization_name",
        "frameworks",
        type_="unique",
    )

    op.create_unique_constraint(
        "frameworks_name_key",
        "frameworks",
        ["name"],
    )

    op.drop_constraint(
        "fk_frameworks_organization_id",
        "frameworks",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_frameworks_organization_id",
        table_name="frameworks",
    )

    op.drop_column(
        "frameworks",
        "organization_id",
    )