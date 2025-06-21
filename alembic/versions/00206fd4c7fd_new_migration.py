"""new migration

Revision ID: 00206fd4c7fd
Revises: bf491788b3b8
Create Date: 2025-06-21 15:38:52.862855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00206fd4c7fd'
down_revision: Union[str, Sequence[str], None] = 'bf491788b3b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
