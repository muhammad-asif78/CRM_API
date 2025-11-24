"""remove_is_super_admin_column

Revision ID: 66db8990684a
Revises: 9429f53cc7e9
Create Date: 2025-11-24 17:13:53.516728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66db8990684a'
down_revision: Union[str, Sequence[str], None] = '9429f53cc7e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove is_super_admin column from users table
    # This column is no longer needed as we use role-based SuperAdmin
    op.drop_column('users', 'is_super_admin')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back is_super_admin column if needed
    op.add_column('users', sa.Column('is_super_admin', sa.Boolean(), nullable=False, server_default=sa.false()))
