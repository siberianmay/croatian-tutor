"""Add multi-user authentication support.

Revision ID: e3f3a3b3c3d3
Revises: d2e2f2a2b2c2
Create Date: 2025-11-29

Adds:
- email, password_hash, is_active columns to user table
- user_id foreign key to app_settings table
- Data migration for existing users
"""

import bcrypt
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e3f3a3b3c3d3"
down_revision = "d2e2f2a2b2c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new columns to user table (nullable initially for migration)
    op.add_column("user", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("user", sa.Column("password_hash", sa.String(255), nullable=True))
    op.add_column("user", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))

    # 2. Set default values for existing users
    # Default password is 'changeme' - users should change this immediately
    default_password_hash = bcrypt.hashpw(
        "changeme".encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    op.execute(
        sa.text(
            """
            UPDATE "user"
            SET email = 'admin@local.app',
                password_hash = :password_hash
            WHERE email IS NULL
            """
        ).bindparams(password_hash=default_password_hash)
    )

    # 3. Make email and password_hash non-nullable after setting defaults
    op.alter_column("user", "email", nullable=False)
    op.alter_column("user", "password_hash", nullable=False)

    # 4. Create unique index on email
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    # 5. Add user_id column to app_settings (nullable initially)
    op.add_column("app_settings", sa.Column("user_id", sa.Integer(), nullable=True))

    # 6. Link existing app_settings to user id 1 (the default user)
    op.execute(
        sa.text(
            """
            UPDATE app_settings
            SET user_id = 1
            WHERE user_id IS NULL
            """
        )
    )

    # 7. Make user_id non-nullable and add foreign key
    op.alter_column("app_settings", "user_id", nullable=False)
    op.create_foreign_key(
        "fk_app_settings_user_id",
        "app_settings",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_app_settings_user_id", "app_settings", ["user_id"], unique=True)


def downgrade() -> None:
    # Remove foreign key and index from app_settings
    op.drop_index("ix_app_settings_user_id", table_name="app_settings")
    op.drop_constraint("fk_app_settings_user_id", "app_settings", type_="foreignkey")
    op.drop_column("app_settings", "user_id")

    # Remove columns and index from user
    op.drop_index("ix_user_email", table_name="user")
    op.drop_column("user", "is_active")
    op.drop_column("user", "password_hash")
    op.drop_column("user", "email")
