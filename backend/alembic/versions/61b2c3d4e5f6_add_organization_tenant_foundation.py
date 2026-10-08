"""Add organization tenant foundation.

Revision ID: 61b2c3d4e5f6
Revises: 60b1c2d3e4f5
Create Date: 2026-10-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "61b2c3d4e5f6"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "60b1c2d3e4f5"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    # ======================================================
    # 1. Create organizations
    # ======================================================

    op.create_table(
        "organizations",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "slug",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "name",
            name="uq_organizations_name",
        ),

        sa.UniqueConstraint(
            "slug",
            name="uq_organizations_slug",
        ),
    )

    op.create_index(
        "ix_organizations_id",
        "organizations",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_organizations_slug",
        "organizations",
        ["slug"],
        unique=False,
    )

    op.create_index(
        "ix_organizations_is_active",
        "organizations",
        ["is_active"],
        unique=False,
    )

    # ======================================================
    # 2. Create default organization
    # ======================================================

    op.execute(
        sa.text(
            """
            INSERT INTO organizations
                (id, name, slug, is_active)
            VALUES
                (
                    1,
                    'Default Organization',
                    'default-organization',
                    true
                )
            """
        )
    )

    # ======================================================
    # 3. Add organization_id to users
    # ======================================================

    op.add_column(
        "users",
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_organization_id",
        "users",
        ["organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_users_organization_id",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    # ======================================================
    # 4. Backfill existing users
    # ======================================================

    op.execute(
        sa.text(
            """
            UPDATE users
            SET organization_id = 1
            WHERE organization_id IS NULL
            """
        )
    )

    # ======================================================
    # 5. Enforce tenant membership
    # ======================================================

    op.alter_column(
        "users",
        "organization_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_users_organization_id",
        "users",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_users_organization_id",
        table_name="users",
    )

    op.drop_column(
        "users",
        "organization_id",
    )

    op.drop_index(
        "ix_organizations_is_active",
        table_name="organizations",
    )

    op.drop_index(
        "ix_organizations_slug",
        table_name="organizations",
    )

    op.drop_index(
        "ix_organizations_id",
        table_name="organizations",
    )

    op.drop_table(
        "organizations",
    )