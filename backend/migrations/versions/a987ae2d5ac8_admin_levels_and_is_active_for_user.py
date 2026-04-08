"""admin levels and is_active for user

Revision ID: a987ae2d5ac8
Revises: c1b22390801c
Create Date: 2026-03-31 22:07:55.872834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a987ae2d5ac8'
down_revision: Union[str, Sequence[str], None] = 'c1b22390801c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('admin_level', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('is_active', sa.Boolean(), nullable=True))

    # 1. is_deleted -> is_active (инвертируем: is_active = NOT is_deleted)
    op.execute("""
        UPDATE "user" 
        SET is_active = NOT is_deleted
    """)

    # 2. is_admin -> admin_level (true -> 1, false -> 0)
    op.execute("""
        UPDATE "user" 
        SET admin_level = CASE 
            WHEN is_admin = true THEN 1 
            ELSE 0 
        END
    """)

    op.alter_column('user', 'admin_level', nullable=False)
    op.alter_column('user', 'is_active', nullable=False)

    op.drop_column('user', 'is_deleted')
    op.drop_column('user', 'is_admin')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('user', sa.Column('is_admin', sa.BOOLEAN(), nullable=True))
    op.add_column('user', sa.Column('is_deleted', sa.BOOLEAN(), nullable=True))

    # 1. is_active -> is_deleted (инвертируем обратно)
    op.execute("""
        UPDATE "user" 
        SET is_deleted = NOT is_active
    """)

    # 2. admin_level -> is_admin (1 -> true, 0 -> false)
    op.execute("""
        UPDATE "user" 
        SET is_admin = CASE 
            WHEN admin_level >= 1 THEN true 
            ELSE false 
        END
    """)

    op.alter_column('user', 'is_admin', nullable=False)
    op.alter_column('user', 'is_deleted', nullable=False)

    op.drop_column('user', 'is_active')
    op.drop_column('user', 'admin_level')