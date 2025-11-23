"""scale_topic_mastery_to_1000

Revision ID: a1b2c3d4e5f6
Revises: 6f2fb341c2b4
Create Date: 2025-11-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6f2fb341c2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Scale existing mastery_score from 0-10 to 0-1000 (multiply by 100)
    op.execute("UPDATE topic_progress SET mastery_score = mastery_score * 100")


def downgrade() -> None:
    # Scale back from 0-1000 to 0-10 (divide by 100)
    op.execute("UPDATE topic_progress SET mastery_score = mastery_score / 100")
