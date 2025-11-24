"""add_app_settings_table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create app_settings table
    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('grammar_batch_size', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('translation_batch_size', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('reading_passage_length', sa.Integer(), nullable=False, server_default='350'),
        sa.Column('gemini_model', sa.String(50), nullable=False, server_default='gemini-2.5-flash'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Insert default settings row (singleton pattern)
    op.execute(
        "INSERT INTO app_settings (id, grammar_batch_size, translation_batch_size, reading_passage_length, gemini_model) "
        "VALUES (1, 10, 10, 350, 'gemini-2.5-flash')"
    )


def downgrade() -> None:
    op.drop_table('app_settings')
