"""Convert timestamp columns from integer to datetime

Revision ID: convert_timestamps_to_datetime
Revises: 6f0f25d9402f
Create Date: 2024-03-19 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "convert_timestamps_to_datetime"
down_revision: Union[str, None] = "6f0f25d9402f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert blocked_users.blocked_at
    op.execute("""
        ALTER TABLE blocked_users
        ALTER COLUMN blocked_at TYPE TIMESTAMP
        USING to_timestamp(blocked_at)
    """)

    # Convert bug_reports.created_at
    op.execute("""
        ALTER TABLE bug_reports
        ALTER COLUMN created_at TYPE TIMESTAMP
        USING to_timestamp(created_at)
    """)

    # Convert download_queue timestamps
    op.execute("""
        ALTER TABLE download_queue
        ALTER COLUMN enqueued_ts TYPE TIMESTAMP
        USING to_timestamp(enqueued_ts)
    """)
    op.execute("""
        ALTER TABLE download_queue
        ALTER COLUMN processed_ts TYPE TIMESTAMP
        USING to_timestamp(processed_ts)
    """)

    # Convert invalid_link_violations.suspended_until
    op.execute("""
        ALTER TABLE invalid_link_violations
        ALTER COLUMN suspended_until TYPE TIMESTAMP
        USING to_timestamp(suspended_until)
    """)

    # Convert monitor_sent_stories.expires_at
    op.execute("""
        ALTER TABLE monitor_sent_stories
        ALTER COLUMN expires_at TYPE TIMESTAMP
        USING to_timestamp(expires_at)
    """)

    # Convert monitors timestamps
    op.execute("""
        ALTER TABLE monitors
        ALTER COLUMN last_checked TYPE TIMESTAMP
        USING to_timestamp(last_checked)
    """)
    op.execute("""
        ALTER TABLE monitors
        ALTER COLUMN created_at TYPE TIMESTAMP
        USING to_timestamp(EXTRACT(EPOCH FROM created_at))
    """)

    # Convert profile_requests.requested_at
    op.execute("""
        ALTER TABLE profile_requests
        ALTER COLUMN requested_at TYPE TIMESTAMP
        USING to_timestamp(requested_at)
    """)

    # Convert tasks timestamps
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN enqueued_ts TYPE TIMESTAMP
        USING to_timestamp(enqueued_ts)
    """)
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN created_at TYPE TIMESTAMP
        USING to_timestamp(created_at)
    """)
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN updated_at TYPE TIMESTAMP
        USING to_timestamp(updated_at)
    """)

    # Convert user_request_log.requested_at
    op.execute("""
        ALTER TABLE user_request_log
        ALTER COLUMN requested_at TYPE TIMESTAMP
        USING to_timestamp(requested_at)
    """)


def downgrade() -> None:
    # Convert blocked_users.blocked_at
    op.execute("""
        ALTER TABLE blocked_users
        ALTER COLUMN blocked_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM blocked_at)::INTEGER
    """)

    # Convert bug_reports.created_at
    op.execute("""
        ALTER TABLE bug_reports
        ALTER COLUMN created_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM created_at)::INTEGER
    """)

    # Convert download_queue timestamps
    op.execute("""
        ALTER TABLE download_queue
        ALTER COLUMN enqueued_ts TYPE INTEGER
        USING EXTRACT(EPOCH FROM enqueued_ts)::INTEGER
    """)
    op.execute("""
        ALTER TABLE download_queue
        ALTER COLUMN processed_ts TYPE INTEGER
        USING EXTRACT(EPOCH FROM processed_ts)::INTEGER
    """)

    # Convert invalid_link_violations.suspended_until
    op.execute("""
        ALTER TABLE invalid_link_violations
        ALTER COLUMN suspended_until TYPE INTEGER
        USING EXTRACT(EPOCH FROM suspended_until)::INTEGER
    """)

    # Convert monitor_sent_stories.expires_at
    op.execute("""
        ALTER TABLE monitor_sent_stories
        ALTER COLUMN expires_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM expires_at)::INTEGER
    """)

    # Convert monitors timestamps
    op.execute("""
        ALTER TABLE monitors
        ALTER COLUMN last_checked TYPE INTEGER
        USING EXTRACT(EPOCH FROM last_checked)::INTEGER
    """)
    op.execute("""
        ALTER TABLE monitors
        ALTER COLUMN created_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM created_at)::INTEGER
    """)

    # Convert profile_requests.requested_at
    op.execute("""
        ALTER TABLE profile_requests
        ALTER COLUMN requested_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM requested_at)::INTEGER
    """)

    # Convert tasks timestamps
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN enqueued_ts TYPE INTEGER
        USING EXTRACT(EPOCH FROM enqueued_ts)::INTEGER
    """)
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN created_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM created_at)::INTEGER
    """)
    op.execute("""
        ALTER TABLE tasks
        ALTER COLUMN updated_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM updated_at)::INTEGER
    """)

    # Convert user_request_log.requested_at
    op.execute("""
        ALTER TABLE user_request_log
        ALTER COLUMN requested_at TYPE INTEGER
        USING EXTRACT(EPOCH FROM requested_at)::INTEGER
    """)
