"""fake missing migration

Revision ID: 7860bc8c5f87
Revises: f7861f54c1e4
Create Date: 2026-01-30 12:40:35.113063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7860bc8c5f87'
down_revision: Union[str, Sequence[str], None] = 'f7861f54c1e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
