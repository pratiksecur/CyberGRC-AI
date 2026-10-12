"""Account security: case-insensitive emails, account state, login attempts

Revision ID: 70e1f2a3b4c5
Revises: 69d0e1f2a3b4
Create Date: 2026-10-12 22:00:00.000000

* users.is_active, users.token_version, users.password_changed_at
* emails stored in lowercase and unique regardless of case
  (unique index on lower(email))
* login_attempts, the sign-in log used by the brute-force protection

If two accounts already differ only by capitalisation, the migration stops
and lists them. They cannot be merged automatically; rename or remove one
of each pair, then run the migration again.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "70e1f2a3b4c5"
down_revision: Union[str, Sequence[str], None] = "69d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())

    return {column["name"] for column in inspector.get_columns(table)}


def _indexes(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())

    return {index["name"] for index in inspector.get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # ------------------------------------------------------------------
    # users: account state
    # ------------------------------------------------------------------

    existing = _columns("users")

    if "is_active" not in existing:
        op.add_column(
            "users",
            sa.Column(
                "is_active",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )

    if "token_version" not in existing:
        op.add_column(
            "users",
            sa.Column(
                "token_version",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )

    if "password_changed_at" not in existing:
        op.add_column(
            "users",
            sa.Column(
                "password_changed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # ------------------------------------------------------------------
    # users: one account per email, whatever the capitalisation
    # ------------------------------------------------------------------

    duplicates = bind.execute(
        sa.text(
            """
            SELECT lower(btrim(email)) AS email, COUNT(*) AS accounts
            FROM users
            GROUP BY lower(btrim(email))
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()

    if duplicates:
        listed = ", ".join(f"{row.email} ({row.accounts})" for row in duplicates)

        raise RuntimeError(
            "Several accounts share the same email apart from capitalisation: "
            f"{listed}. Rename or remove the extra accounts, then run the "
            "migration again."
        )

    op.execute(
        sa.text(
            """
            UPDATE users
            SET email = lower(btrim(email))
            WHERE email <> lower(btrim(email))
            """
        )
    )

    if "uq_users_email_lower" not in _indexes("users"):
        op.create_index(
            "uq_users_email_lower",
            "users",
            [sa.text("lower(email)")],
            unique=True,
        )

    # ------------------------------------------------------------------
    # login_attempts
    # ------------------------------------------------------------------

    if "login_attempts" not in inspector.get_table_names():
        op.create_table(
            "login_attempts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("success", sa.Boolean(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

        op.create_index("ix_login_attempts_id", "login_attempts", ["id"])
        op.create_index(
            "ix_login_attempts_email_created",
            "login_attempts",
            ["email", "created_at"],
        )
        op.create_index(
            "ix_login_attempts_ip_created",
            "login_attempts",
            ["ip_address", "created_at"],
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if "login_attempts" in inspector.get_table_names():
        op.drop_table("login_attempts")

    if "uq_users_email_lower" in _indexes("users"):
        op.drop_index("uq_users_email_lower", table_name="users")

    existing = _columns("users")

    for column in ("password_changed_at", "token_version", "is_active"):
        if column in existing:
            op.drop_column("users", column)