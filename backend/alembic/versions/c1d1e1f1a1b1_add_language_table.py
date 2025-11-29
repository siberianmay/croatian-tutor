"""add_language_table

Revision ID: c1d1e1f1a1b1
Revises: b2c3d4e5f6a7
Create Date: 2025-11-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d1e1f1a1b1'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create language table
    op.create_table(
        'language',
        sa.Column('code', sa.String(length=8), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('native_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('code')
    )
    op.create_index(op.f('ix_language_code'), 'language', ['code'], unique=True)

    # Seed Croatian language with id=1
    op.execute(
        "INSERT INTO language (code, name, native_name, is_active) "
        "VALUES ('hr', 'Croatian', 'Hrvatski', true)"
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_language_code'), table_name='language')
    op.drop_table('language')
