"""add_language_to_tables

Revision ID: d2e2f2a2b2c2
Revises: c1d1e1f1a1b1
Create Date: 2025-11-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2e2f2a2b2c2'
down_revision: Union[str, None] = 'c1d1e1f1a1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add language to word table
    op.add_column(
        'word',
        sa.Column('language', sa.String(8), nullable=False, server_default='hr')
    )
    op.create_foreign_key(
        'fk_word_language',
        'word', 'language',
        ['language'], ['code']
    )
    op.create_index('ix_word_language', 'word', ['language'])

    # Add language to grammar_topic table
    op.add_column(
        'grammar_topic',
        sa.Column('language', sa.String(8), nullable=False, server_default='hr')
    )
    op.create_foreign_key(
        'fk_grammar_topic_language',
        'grammar_topic', 'language',
        ['language'], ['code']
    )
    op.create_index('ix_grammar_topic_language', 'grammar_topic', ['language'])

    # Create unique constraint for name + language (original name-only constraint may not exist)
    op.create_unique_constraint(
        'uq_grammar_topic_name_language',
        'grammar_topic',
        ['name', 'language']
    )

    # Add language to session table
    op.add_column(
        'session',
        sa.Column('language', sa.String(8), nullable=False, server_default='hr')
    )
    op.create_foreign_key(
        'fk_session_language',
        'session', 'language',
        ['language'], ['code']
    )
    op.create_index('ix_session_language', 'session', ['language'])

    # Add language to exercise_log table
    op.add_column(
        'exercise_log',
        sa.Column('language', sa.String(8), nullable=False, server_default='hr')
    )
    op.create_foreign_key(
        'fk_exercise_log_language',
        'exercise_log', 'language',
        ['language'], ['code']
    )
    op.create_index('ix_exercise_log_language', 'exercise_log', ['language'])

    # Update exercise_log unique constraint to include language
    op.drop_constraint('uq_user_date_type', 'exercise_log', type_='unique')
    op.create_unique_constraint(
        'uq_user_date_type_language',
        'exercise_log',
        ['user_id', 'date', 'exercise_type', 'language']
    )

    # Add language to error_log table
    op.add_column(
        'error_log',
        sa.Column('language', sa.String(8), nullable=False, server_default='hr')
    )
    op.create_foreign_key(
        'fk_error_log_language',
        'error_log', 'language',
        ['language'], ['code']
    )
    op.create_index('ix_error_log_language', 'error_log', ['language'])

    # Add language to the user table
    op.add_column(
        'user',
        sa.Column('language', sa.String(8), nullable=False, server_default='hr')
    )
    op.create_foreign_key(
        'fk_user_language',
        'user', 'language',
        ['language'], ['code']
    )


def downgrade() -> None:
    # Remove from user
    op.drop_constraint('fk_user_language', 'user', type_='foreignkey')
    op.drop_column('user', 'language')

    # Remove from error_log
    op.drop_index('ix_error_log_language', 'error_log')
    op.drop_constraint('fk_error_log_language', 'error_log', type_='foreignkey')
    op.drop_column('error_log', 'language')

    # Restore exercise_log constraint and remove column
    op.drop_constraint('uq_user_date_type_language', 'exercise_log', type_='unique')
    op.create_unique_constraint('uq_user_date_type', 'exercise_log', ['user_id', 'date', 'exercise_type'])
    op.drop_index('ix_exercise_log_language', 'exercise_log')
    op.drop_constraint('fk_exercise_log_language', 'exercise_log', type_='foreignkey')
    op.drop_column('exercise_log', 'language')

    # Remove from session
    op.drop_index('ix_session_language', 'session')
    op.drop_constraint('fk_session_language', 'session', type_='foreignkey')
    op.drop_column('session', 'language')

    # Remove grammar_topic language column and constraint
    op.drop_constraint('uq_grammar_topic_name_language', 'grammar_topic', type_='unique')
    op.drop_index('ix_grammar_topic_language', 'grammar_topic')
    op.drop_constraint('fk_grammar_topic_language', 'grammar_topic', type_='foreignkey')
    op.drop_column('grammar_topic', 'language')

    # Remove from word
    op.drop_index('ix_word_language', 'word')
    op.drop_constraint('fk_word_language', 'word', type_='foreignkey')
    op.drop_column('word', 'language')
