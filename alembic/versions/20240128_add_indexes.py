"""Add database indexes

Revision ID: 20240128_add_indexes
Revises: 20240128_initial
Create Date: 2024-01-28 00:01:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20240128_add_indexes"
down_revision: str = "20240128_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table indexes
    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=True,
        postgresql_where=sa.text("username IS NOT NULL"),
    )
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_is_admin", "users", ["is_admin"])

    # Stories table indexes
    op.create_index("ix_stories_user_id", "stories", ["user_id"])
    op.create_index("ix_stories_created_at", "stories", ["created_at"])
    op.create_index("ix_stories_expires_at", "stories", ["expires_at"])
    op.create_index("ix_stories_is_viewed", "stories", ["is_viewed"])
    # Composite index for active stories
    op.create_index("ix_stories_user_active", "stories", ["user_id", "is_viewed", "created_at"])

    # Profiles table indexes
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"])
    op.create_index("ix_profiles_target_username", "profiles", ["target_username"])
    op.create_index(
        "ix_profiles_target_phone",
        "profiles",
        ["target_phone"],
        postgresql_where=sa.text("target_phone IS NOT NULL"),
    )
    op.create_index("ix_profiles_is_active", "profiles", ["is_active"])
    op.create_index("ix_profiles_last_check", "profiles", ["last_check"])
    # Composite index for active monitoring
    op.create_index("ix_profiles_active_monitoring", "profiles", ["is_active", "last_check"])

    # Payments table indexes
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_created_at", "payments", ["created_at"])
    op.create_index(
        "ix_payments_transaction_id",
        "payments",
        ["transaction_id"],
        unique=True,
        postgresql_where=sa.text("transaction_id IS NOT NULL"),
    )
    # Composite index for user payments
    op.create_index("ix_payments_user_status", "payments", ["user_id", "status", "created_at"])


def downgrade() -> None:
    # Drop payment indexes
    op.drop_index("ix_payments_user_status")
    op.drop_index("ix_payments_transaction_id")
    op.drop_index("ix_payments_created_at")
    op.drop_index("ix_payments_status")
    op.drop_index("ix_payments_user_id")

    # Drop profile indexes
    op.drop_index("ix_profiles_active_monitoring")
    op.drop_index("ix_profiles_last_check")
    op.drop_index("ix_profiles_is_active")
    op.drop_index("ix_profiles_target_phone")
    op.drop_index("ix_profiles_target_username")
    op.drop_index("ix_profiles_user_id")

    # Drop story indexes
    op.drop_index("ix_stories_user_active")
    op.drop_index("ix_stories_is_viewed")
    op.drop_index("ix_stories_expires_at")
    op.drop_index("ix_stories_created_at")
    op.drop_index("ix_stories_user_id")

    # Drop user indexes
    op.drop_index("ix_users_is_admin")
    op.drop_index("ix_users_is_active")
    op.drop_index("ix_users_username")
