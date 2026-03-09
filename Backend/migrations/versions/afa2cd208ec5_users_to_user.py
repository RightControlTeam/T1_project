"""users to user

Revision ID: afa2cd208ec5
Revises: 56e9deea2ab0
Create Date: 2026-03-09 12:11:10.149419

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'afa2cd208ec5'
down_revision: Union[str, Sequence[str], None] = '56e9deea2ab0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('users', 'user')



def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('user', 'users')

