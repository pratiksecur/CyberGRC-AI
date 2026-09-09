"""add user organizational hierarchy

Revision ID: 40436fbc19af
Revises: add_notifications
Create Date: 2026-08-31 17:57:51.391594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40436fbc19af'
down_revision: Union[str, Sequence[str], None] = 'add_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Columns already exist in the database.
    # This migration is kept as the schema-history record.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Organizational hierarchy columns are managed separately.
    pass