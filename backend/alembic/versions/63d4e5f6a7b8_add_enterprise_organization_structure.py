"""Add enterprise organizational structure."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "63d4e5f6a7b8"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "62c3d4e5f6a7"

branch_labels = None
depends_on = None


def upgrade() -> None:

    # ======================================================
    # BUSINESS UNITS
    # ======================================================

    op.create_table(
        "business_units",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "organization_id",
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
            "description",
            sa.Text(),
            nullable=True,
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

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_business_units_organization_name",
        ),

        sa.UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_business_units_organization_slug",
        ),
    )

    op.create_index(
        "ix_business_units_id",
        "business_units",
        ["id"],
    )

    op.create_index(
        "ix_business_units_organization_id",
        "business_units",
        ["organization_id"],
    )

    op.create_index(
        "ix_business_units_is_active",
        "business_units",
        ["is_active"],
    )

    # ======================================================
    # DEPARTMENTS
    # ======================================================

    op.create_table(
        "departments",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "business_unit_id",
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
            "description",
            sa.Text(),
            nullable=True,
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

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["business_unit_id"],
            ["business_units.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_departments_organization_name",
        ),

        sa.UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_departments_organization_slug",
        ),
    )

    op.create_index(
        "ix_departments_id",
        "departments",
        ["id"],
    )

    op.create_index(
        "ix_departments_organization_id",
        "departments",
        ["organization_id"],
    )

    op.create_index(
        "ix_departments_business_unit_id",
        "departments",
        ["business_unit_id"],
    )

    op.create_index(
        "ix_departments_is_active",
        "departments",
        ["is_active"],
    )

    # ======================================================
    # GRC TEAMS
    # ======================================================

    op.create_table(
        "grc_teams",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "business_unit_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "department_id",
            sa.Integer(),
            nullable=True,
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
            "description",
            sa.Text(),
            nullable=True,
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

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["business_unit_id"],
            ["business_units.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_grc_teams_organization_name",
        ),

        sa.UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_grc_teams_organization_slug",
        ),
    )

    op.create_index(
        "ix_grc_teams_id",
        "grc_teams",
        ["id"],
    )

    op.create_index(
        "ix_grc_teams_organization_id",
        "grc_teams",
        ["organization_id"],
    )

    op.create_index(
        "ix_grc_teams_business_unit_id",
        "grc_teams",
        ["business_unit_id"],
    )

    op.create_index(
        "ix_grc_teams_department_id",
        "grc_teams",
        ["department_id"],
    )

    op.create_index(
        "ix_grc_teams_is_active",
        "grc_teams",
        ["is_active"],
    )

    # ======================================================
    # ENTERPRISE CONFIGURATION
    # ======================================================

    op.create_table(
        "enterprise_configurations",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "timezone",
            sa.String(length=100),
            nullable=False,
            server_default="UTC",
        ),

        sa.Column(
            "default_risk_threshold",
            sa.Integer(),
            nullable=False,
            server_default="15",
        ),

        sa.Column(
            "critical_risk_threshold",
            sa.Integer(),
            nullable=False,
            server_default="20",
        ),

        sa.Column(
            "stale_evidence_days",
            sa.Integer(),
            nullable=False,
            server_default="90",
        ),

        sa.Column(
            "treatment_stuck_days",
            sa.Integer(),
            nullable=False,
            server_default="30",
        ),

        sa.Column(
            "notifications_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),

        sa.Column(
            "ai_enabled",
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

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "organization_id",
            name="uq_enterprise_configurations_organization",
        ),
    )

    op.create_index(
        "ix_enterprise_configurations_id",
        "enterprise_configurations",
        ["id"],
    )

    op.create_index(
        "ix_enterprise_configurations_organization_id",
        "enterprise_configurations",
        ["organization_id"],
    )

    # ======================================================
    # USER STRUCTURE COLUMNS
    # ======================================================

    op.add_column(
        "users",
        sa.Column(
            "business_unit_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "department_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "team_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_business_unit_id",
        "users",
        ["business_unit_id"],
    )

    op.create_index(
        "ix_users_department_id",
        "users",
        ["department_id"],
    )

    op.create_index(
        "ix_users_team_id",
        "users",
        ["team_id"],
    )

    op.create_foreign_key(
        "fk_users_business_unit_id",
        "users",
        "business_units",
        ["business_unit_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_users_department_id",
        "users",
        "departments",
        ["department_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_users_team_id",
        "users",
        "grc_teams",
        ["team_id"],
        ["id"],
    )

    # ======================================================
    # BACKFILL ENTERPRISE STRUCTURE
    # ======================================================

    connection = op.get_bind()

    organizations = connection.execute(
        sa.text(
            """
            SELECT id
            FROM organizations
            ORDER BY id
            """
        )
    ).fetchall()

    for row in organizations:

        organization_id = row[0]

        connection.execute(
            sa.text(
                """
                INSERT INTO business_units
                    (
                        organization_id,
                        name,
                        slug,
                        description,
                        is_active
                    )
                VALUES
                    (
                        :organization_id,
                        'General Business Unit',
                        'general',
                        'Default business unit created during enterprise architecture migration.',
                        true
                    )
                """
            ),
            {
                "organization_id": organization_id,
            },
        )

        business_unit_id = connection.execute(
            sa.text(
                """
                SELECT id
                FROM business_units
                WHERE organization_id = :organization_id
                  AND slug = 'general'
                """
            ),
            {
                "organization_id": organization_id,
            },
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                INSERT INTO departments
                    (
                        organization_id,
                        business_unit_id,
                        name,
                        slug,
                        description,
                        is_active
                    )
                VALUES
                    (
                        :organization_id,
                        :business_unit_id,
                        'General',
                        'general',
                        'Default department created during enterprise architecture migration.',
                        true
                    )
                """
            ),
            {
                "organization_id": organization_id,
                "business_unit_id": business_unit_id,
            },
        )

        department_id = connection.execute(
            sa.text(
                """
                SELECT id
                FROM departments
                WHERE organization_id = :organization_id
                  AND slug = 'general'
                """
            ),
            {
                "organization_id": organization_id,
            },
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                INSERT INTO grc_teams
                    (
                        organization_id,
                        business_unit_id,
                        department_id,
                        name,
                        slug,
                        description,
                        is_active
                    )
                VALUES
                    (
                        :organization_id,
                        :business_unit_id,
                        :department_id,
                        'Core GRC Team',
                        'core-grc',
                        'Default GRC team created during enterprise architecture migration.',
                        true
                    )
                """
            ),
            {
                "organization_id": organization_id,
                "business_unit_id": business_unit_id,
                "department_id": department_id,
            },
        )

        team_id = connection.execute(
            sa.text(
                """
                SELECT id
                FROM grc_teams
                WHERE organization_id = :organization_id
                  AND slug = 'core-grc'
                """
            ),
            {
                "organization_id": organization_id,
            },
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                INSERT INTO enterprise_configurations
                    (
                        organization_id,
                        timezone,
                        default_risk_threshold,
                        critical_risk_threshold,
                        stale_evidence_days,
                        treatment_stuck_days,
                        notifications_enabled,
                        ai_enabled
                    )
                VALUES
                    (
                        :organization_id,
                        'UTC',
                        15,
                        20,
                        90,
                        30,
                        true,
                        true
                    )
                """
            ),
            {
                "organization_id": organization_id,
            },
        )

        connection.execute(
            sa.text(
                """
                UPDATE users
                SET
                    business_unit_id = :business_unit_id,
                    department_id = :department_id,
                    team_id = :team_id
                WHERE organization_id = :organization_id
                """
            ),
            {
                "organization_id": organization_id,
                "business_unit_id": business_unit_id,
                "department_id": department_id,
                "team_id": team_id,
            },
        )


def downgrade() -> None:

    op.drop_constraint(
        "fk_users_team_id",
        "users",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_users_department_id",
        "users",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_users_business_unit_id",
        "users",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_users_team_id",
        table_name="users",
    )

    op.drop_index(
        "ix_users_department_id",
        table_name="users",
    )

    op.drop_index(
        "ix_users_business_unit_id",
        table_name="users",
    )

    op.drop_column(
        "users",
        "team_id",
    )

    op.drop_column(
        "users",
        "department_id",
    )

    op.drop_column(
        "users",
        "business_unit_id",
    )

    op.drop_index(
        "ix_enterprise_configurations_organization_id",
        table_name="enterprise_configurations",
    )

    op.drop_index(
        "ix_enterprise_configurations_id",
        table_name="enterprise_configurations",
    )

    op.drop_table(
        "enterprise_configurations",
    )

    op.drop_index(
        "ix_grc_teams_is_active",
        table_name="grc_teams",
    )

    op.drop_index(
        "ix_grc_teams_department_id",
        table_name="grc_teams",
    )

    op.drop_index(
        "ix_grc_teams_business_unit_id",
        table_name="grc_teams",
    )

    op.drop_index(
        "ix_grc_teams_organization_id",
        table_name="grc_teams",
    )

    op.drop_index(
        "ix_grc_teams_id",
        table_name="grc_teams",
    )

    op.drop_table(
        "grc_teams",
    )

    op.drop_index(
        "ix_departments_is_active",
        table_name="departments",
    )

    op.drop_index(
        "ix_departments_business_unit_id",
        table_name="departments",
    )

    op.drop_index(
        "ix_departments_organization_id",
        table_name="departments",
    )

    op.drop_index(
        "ix_departments_id",
        table_name="departments",
    )

    op.drop_table(
        "departments",
    )

    op.drop_index(
        "ix_business_units_is_active",
        table_name="business_units",
    )

    op.drop_index(
        "ix_business_units_organization_id",
        table_name="business_units",
    )

    op.drop_index(
        "ix_business_units_id",
        table_name="business_units",
    )

    op.drop_table(
        "business_units",
    )