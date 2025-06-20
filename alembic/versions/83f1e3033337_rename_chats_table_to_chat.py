"""rename chats table to chat

Revision ID: 83f1e3033337
Revises: 23c11b1222fb
Create Date: 2025-06-20 07:44:37.073821

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "83f1e3033337"
down_revision: Union[str, Sequence[str], None] = "23c11b1222fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("chats", "chat")
    op.drop_column("chat", "is_forum")
    op.drop_constraint("bug_reports_chat_id_fkey", "bug_report", type_="foreignkey")
    op.create_foreign_key(None, "bug_report", "chat", ["chat_id"], ["id"])
    op.drop_constraint("download_queue_chat_id_fkey", "download_queue", type_="foreignkey")
    op.create_foreign_key(None, "download_queue", "chat", ["chat_id"], ["id"])
    op.drop_constraint(
        "invalid_link_violations_chat_id_fkey", "invalid_link_violation", type_="foreignkey"
    )
    op.create_foreign_key(None, "invalid_link_violation", "chat", ["chat_id"], ["id"])
    op.drop_constraint("monitors_chat_id_fkey", "monitor", type_="foreignkey")
    op.create_foreign_key(None, "monitor", "chat", ["chat_id"], ["id"])
    op.drop_constraint("tasks_chat_id_fkey", "task", type_="foreignkey")
    op.create_foreign_key(None, "task", "chat", ["chat_id"], ["id"])
    op.drop_index("ix_users_chat_id", table_name="user")
    op.drop_index("ix_users_id", table_name="user")
    op.drop_index("ix_users_username", table_name="user")
    op.create_index(op.f("ix_user_chat_id"), "user", ["chat_id"], unique=False)
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.drop_constraint("users_chat_id_fkey", "user", type_="foreignkey")
    op.create_foreign_key(None, "user", "chat", ["chat_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("chat", "chats")
    op.add_column(
        "chats",
        sa.Column(
            "is_forum",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.drop_constraint(None, "user", type_="foreignkey")
    op.create_foreign_key("users_chat_id_fkey", "user", "chats", ["chat_id"], ["id"])
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_chat_id"), table_name="user")
    op.create_index("ix_users_username", "user", ["username"], unique=True)
    op.create_index("ix_users_id", "user", ["id"], unique=False)
    op.create_index("ix_users_chat_id", "user", ["chat_id"], unique=False)
    op.drop_constraint(None, "task", type_="foreignkey")
    op.create_foreign_key("tasks_chat_id_fkey", "task", "chats", ["chat_id"], ["id"])
    op.drop_constraint(None, "monitor", type_="foreignkey")
    op.create_foreign_key("monitors_chat_id_fkey", "monitor", "chats", ["chat_id"], ["id"])
    op.drop_constraint(None, "invalid_link_violation", type_="foreignkey")
    op.create_foreign_key(
        "invalid_link_violations_chat_id_fkey",
        "invalid_link_violation",
        "chats",
        ["chat_id"],
        ["id"],
    )
    op.drop_constraint(None, "download_queue", type_="foreignkey")
    op.create_foreign_key(
        "download_queue_chat_id_fkey", "download_queue", "chats", ["chat_id"], ["id"]
    )
    op.drop_constraint(None, "bug_report", type_="foreignkey")
    op.create_foreign_key("bug_reports_chat_id_fkey", "bug_report", "chats", ["chat_id"], ["id"])
