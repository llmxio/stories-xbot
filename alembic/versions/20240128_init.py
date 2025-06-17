"""Initial migration with tables and indexes

Revision ID: 20240128_init
Revises:
Create Date: 2024-01-28 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20240128_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_premium", sa.Boolean(), server_default="false", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create stories table
    op.create_table(
        "stories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("media_url", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_viewed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create profiles table
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("target_username", sa.String(), nullable=False),
        sa.Column("target_phone", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("last_check", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create payments table
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("transaction_id", sa.String(), nullable=True),
        sa.Column("payment_method", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create blocked_users table
    op.create_table(
        "blocked_users",
        sa.Column("telegram_id", sa.String(), nullable=False),
        sa.Column("blocked_at", sa.Integer()),
        sa.Column("is_bot", sa.Integer()),
        sa.PrimaryKeyConstraint("telegram_id"),
    )  # type: ignore[attr-defined]

    # Create bug_reports table
    op.create_table(
        "bug_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.String()),
        sa.Column("username", sa.String()),
        sa.Column("description", sa.String()),
        sa.Column("created_at", sa.Integer()),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create download_queue table
    op.create_table(
        "download_queue",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.String()),
        sa.Column("target_username", sa.String()),
        sa.Column("status", sa.String()),
        sa.Column("enqueued_ts", sa.Integer()),
        sa.Column("processed_ts", sa.Integer()),
        sa.Column("error", sa.String()),
        sa.Column("task_details", sa.String()),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create invalid_link_violations table
    op.create_table(
        "invalid_link_violations",
        sa.Column("telegram_id", sa.String(), nullable=False),
        sa.Column("count", sa.Integer()),
        sa.Column("suspended_until", sa.Integer()),
        sa.PrimaryKeyConstraint("telegram_id"),
    )  # type: ignore[attr-defined]

    # Create monitor_sent_stories table
    op.create_table(  # type: ignore
        "monitor_sent_stories",
        sa.Column("monitor_id", sa.Integer()),
        sa.Column("story_id", sa.Integer()),
        sa.Column("expires_at", sa.Integer()),
    )  # type: ignore

    # Create monitors table
    op.create_table(
        "monitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.String()),
        sa.Column("target_username", sa.String()),
        sa.Column("last_checked", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create profile_requests table
    op.create_table(
        "profile_requests",
        sa.Column("telegram_id", sa.String()),
        sa.Column("target_username", sa.String()),
        sa.Column("requested_at", sa.Integer()),
    )  # type: ignore[attr-defined]

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("telegram_id", sa.String()),
        sa.Column("status", sa.String()),
        sa.Column("task_details", sa.String()),
        sa.Column("enqueued_ts", sa.Integer()),
        sa.Column("is_premium", sa.Integer()),
        sa.Column("is_bot", sa.Integer()),
        sa.Column("username", sa.String()),
        sa.Column("target_username", sa.String()),
        sa.Column("description", sa.String()),
        sa.Column("created_at", sa.Integer()),
        sa.Column("updated_at", sa.Integer()),
        sa.PrimaryKeyConstraint("id"),
    )  # type: ignore[attr-defined]

    # Create user_request_log table
    op.create_table(
        "user_request_log",
        sa.Column("telegram_id", sa.String()),
        sa.Column("requested_at", sa.Integer()),
    )  # type: ignore[attr-defined]

    # After all tables are created, create indexes
    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=True,
        postgresql_where=sa.text("username IS NOT NULL"),
    )  # type: ignore[attr-defined]
    op.create_index("ix_users_is_active", "users", ["is_active"])  # type: ignore[attr-defined]
    op.create_index("ix_users_is_admin", "users", ["is_admin"])  # type: ignore[attr-defined]

    op.create_index("ix_stories_user_id", "stories", ["user_id"])  # type: ignore[attr-defined]
    op.create_index("ix_stories_created_at", "stories", ["created_at"])  # type: ignore[attr-defined]
    op.create_index("ix_stories_expires_at", "stories", ["expires_at"])  # type: ignore[attr-defined]
    op.create_index("ix_stories_is_viewed", "stories", ["is_viewed"])  # type: ignore[attr-defined]
    op.create_index("ix_stories_user_active", "stories", ["user_id", "is_viewed", "created_at"])  # type: ignore[attr-defined]

    op.create_index("ix_profiles_user_id", "profiles", ["user_id"])  # type: ignore[attr-defined]
    op.create_index("ix_profiles_target_username", "profiles", ["target_username"])  # type: ignore[attr-defined]
    op.create_index(
        "ix_profiles_target_phone",
        "profiles",
        ["target_phone"],
        postgresql_where=sa.text("target_phone IS NOT NULL"),
    )  # type: ignore[attr-defined]
    op.create_index("ix_profiles_is_active", "profiles", ["is_active"])  # type: ignore[attr-defined]
    op.create_index("ix_profiles_last_check", "profiles", ["last_check"])  # type: ignore[attr-defined]
    op.create_index("ix_profiles_active_monitoring", "profiles", ["is_active", "last_check"])  # type: ignore[attr-defined]

    op.create_index("ix_payments_user_id", "payments", ["user_id"])  # type: ignore[attr-defined]
    op.create_index("ix_payments_status", "payments", ["status"])  # type: ignore[attr-defined]
    op.create_index("ix_payments_created_at", "payments", ["created_at"])  # type: ignore[attr-defined]
    op.create_index(
        "ix_payments_transaction_id",
        "payments",
        ["transaction_id"],
        unique=True,
        postgresql_where=sa.text("transaction_id IS NOT NULL"),
    )  # type: ignore[attr-defined]
    op.create_index("ix_payments_user_status", "payments", ["user_id", "status", "created_at"])  # type: ignore[attr-defined]


def downgrade() -> None:
    # Drop payment indexes
    op.drop_index("ix_payments_user_status")  # type: ignore[attr-defined]
    op.drop_index("ix_payments_transaction_id")  # type: ignore[attr-defined]
    op.drop_index("ix_payments_created_at")  # type: ignore[attr-defined]
    op.drop_index("ix_payments_status")  # type: ignore[attr-defined]
    op.drop_index("ix_payments_user_id")  # type: ignore[attr-defined]

    # Drop profile indexes
    op.drop_index("ix_profiles_active_monitoring")  # type: ignore[attr-defined]
    op.drop_index("ix_profiles_last_check")  # type: ignore[attr-defined]
    op.drop_index("ix_profiles_is_active")  # type: ignore[attr-defined]
    op.drop_index("ix_profiles_target_phone")  # type: ignore[attr-defined]
    op.drop_index("ix_profiles_target_username")  # type: ignore[attr-defined]
    op.drop_index("ix_profiles_user_id")  # type: ignore[attr-defined]

    # Drop story indexes
    op.drop_index("ix_stories_user_active")  # type: ignore[attr-defined]
    op.drop_index("ix_stories_is_viewed")  # type: ignore[attr-defined]
    op.drop_index("ix_stories_expires_at")  # type: ignore[attr-defined]
    op.drop_index("ix_stories_created_at")  # type: ignore[attr-defined]
    op.drop_index("ix_stories_user_id")  # type: ignore[attr-defined]

    # Drop user indexes
    op.drop_index("ix_users_is_admin")  # type: ignore[attr-defined]
    op.drop_index("ix_users_is_active")  # type: ignore[attr-defined]
    op.drop_index("ix_users_username")  # type: ignore[attr-defined]

    # Drop new tables
    op.drop_table("user_request_log")
    op.drop_table("tasks")
    op.drop_table("profile_requests")
    op.drop_table("monitors")
    op.drop_table("monitor_sent_stories")
    op.drop_table("invalid_link_violations")
    op.drop_table("download_queue")
    op.drop_table("bug_reports")
    op.drop_table("blocked_users")

    # Drop tables
    op.drop_table("payments")
    op.drop_table("profiles")
    op.drop_table("stories")
    op.drop_table("users")
