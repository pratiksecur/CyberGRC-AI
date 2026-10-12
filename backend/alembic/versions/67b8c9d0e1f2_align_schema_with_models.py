"""Align schema with the models

Revision ID: 67b8c9d0e1f2
Revises: 66a7b8c9d0e1
Create Date: 2026-10-12 17:30:00.000000

A database built only from migrations differed from one built from the
models:

* controls.effectiveness was never added by a migration.
* frameworks.created_at / updated_at were created nullable, but the model
  declares them NOT NULL.

Databases created with ``create_all`` already match, so every step checks
the current state first and does nothing when it is already correct.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "67b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "66a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table: str) -> dict:
    inspector = sa.inspect(op.get_bind())
    return {c["name"]: c for c in inspector.get_columns(table)}


def upgrade() -> None:
    # ------------------------------------------------------
    # controls.effectiveness
    # ------------------------------------------------------
    if "effectiveness" not in _columns("controls"):
        op.add_column(
            "controls",
            sa.Column(
                "effectiveness",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )
        # The model sets the default in Python, not in the database.
        op.alter_column("controls", "effectiveness", server_default=None)

    # ------------------------------------------------------
    # frameworks.created_at / updated_at -> NOT NULL
    # ------------------------------------------------------
    framework_columns = _columns("frameworks")

    for name in ("created_at", "updated_at"):
        if framework_columns[name]["nullable"]:
            op.execute(
                sa.text(
                    f"UPDATE frameworks SET {name} = now() "
                    f"WHERE {name} IS NULL"
                )
            )
            op.alter_column(
                "frameworks",
                name,
                existing_type=sa.DateTime(timezone=True),
                existing_server_default=sa.text("now()"),
                nullable=False,
            )


def downgrade() -> None:
    for name in ("updated_at", "created_at"):
        op.alter_column(
            "frameworks",
            name,
            existing_type=sa.DateTime(timezone=True),
            existing_server_default=sa.text("now()"),
            nullable=True,
        )

    op.drop_column("controls", "effectiveness")