"""add audit creator attribution

Revision ID: a33dd102e6c2
Revises: ad16080d67d6
Create Date: 2026-09-02 17:54:27.862841

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a33dd102e6c2"
down_revision: Union[str, Sequence[str], None] = "ad16080d67d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass