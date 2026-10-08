"""add resource tenant foundation

Revision ID: 62c3d4e5f6a7
Revises: 61b2c3d4e5f6
Create Date: 2026-10-07
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "62c3d4e5f6a7"
down_revision = "61b2c3d4e5f6"
branch_labels = None
depends_on = None


RESOURCE_TABLES = (
    "risks",
    "controls",
    "evidence",
    "audits",
    "audit_findings",
    "corrective_actions",
)


def upgrade() -> None:
    # ======================================================
    # 1. Add tenant columns
    # ======================================================

    for table_name in RESOURCE_TABLES:
        op.add_column(
            table_name,
            sa.Column(
                "organization_id",
                sa.Integer(),
                nullable=True,
            ),
        )

        op.create_index(
            f"ix_{table_name}_organization_id",
            table_name,
            ["organization_id"],
        )

        op.create_foreign_key(
            f"fk_{table_name}_organization_id",
            table_name,
            "organizations",
            ["organization_id"],
            ["id"],
        )

    # ======================================================
    # 2. Backfill Risks
    #
    # Risk ownership is represented by owner_id.
    # ======================================================

    op.execute(
        """
        UPDATE risks AS r
        SET organization_id = u.organization_id
        FROM users AS u
        WHERE r.owner_id = u.id
          AND r.organization_id IS NULL
        """
    )

    # ======================================================
    # 3. Backfill Controls
    # ======================================================

    op.execute(
        """
        UPDATE controls AS c
        SET organization_id = u.organization_id
        FROM users AS u
        WHERE c.owner_id = u.id
          AND c.organization_id IS NULL
        """
    )

    # ======================================================
    # 4. Backfill Evidence
    #
    # Evidence belongs to the same tenant as its control.
    # ======================================================

    op.execute(
        """
        UPDATE evidence AS e
        SET organization_id = c.organization_id
        FROM controls AS c
        WHERE e.control_id = c.id
          AND e.organization_id IS NULL
        """
    )

    # ======================================================
    # 5. Backfill Audits
    #
    # Audit tenant is derived from its assigned auditor.
    # ======================================================

    op.execute(
        """
        UPDATE audits AS a
        SET organization_id = u.organization_id
        FROM users AS u
        WHERE a.auditor_id = u.id
          AND a.organization_id IS NULL
        """
    )

    # ======================================================
    # 6. Backfill Audit Findings
    #
    # Finding belongs to its parent audit tenant.
    # ======================================================

    op.execute(
        """
        UPDATE audit_findings AS af
        SET organization_id = a.organization_id
        FROM audits AS a
        WHERE af.audit_id = a.id
          AND af.organization_id IS NULL
        """
    )

    # ======================================================
    # 7. Backfill Corrective Actions
    #
    # Corrective action belongs to:
    #
    # CorrectiveAction
    #       ↓
    # AuditFinding
    #       ↓
    # Audit
    #       ↓
    # Organization
    # ======================================================

    op.execute(
        """
        UPDATE corrective_actions AS ca
        SET organization_id = af.organization_id
        FROM audit_findings AS af
        WHERE ca.finding_id = af.id
          AND ca.organization_id IS NULL
        """
    )

    # ======================================================
    # 8. Validate backfill
    #
    # We deliberately fail the migration if any existing
    # resource could not be assigned to an organization.
    # ======================================================

    for table_name in RESOURCE_TABLES:
        result = op.get_bind().execute(
            sa.text(
                f"""
                SELECT COUNT(*)
                FROM {table_name}
                WHERE organization_id IS NULL
                """
            )
        )

        remaining = result.scalar()

        if remaining and remaining > 0:
            raise RuntimeError(
                f"Tenant backfill failed for {table_name}: "
                f"{remaining} rows have no organization_id."
            )


def downgrade() -> None:
    # Reverse in dependency-safe order.
    for table_name in reversed(RESOURCE_TABLES):
        op.drop_constraint(
            f"fk_{table_name}_organization_id",
            table_name,
            type_="foreignkey",
        )

        op.drop_index(
            f"ix_{table_name}_organization_id",
            table_name=table_name,
        )

        op.drop_column(
            table_name,
            "organization_id",
        )