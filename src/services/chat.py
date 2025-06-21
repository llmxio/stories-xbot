from config import get_logger
from db.schemas import Chat as ChatSchema
from models import Chat as ChatDB

from .base import BaseService

logger = get_logger(__name__)


class ChatService(BaseService):
    def create_chat(self, chat: ChatSchema) -> ChatSchema:
        db_chat = ChatDB(
            id=chat.id,
            type=chat.type,
            title=chat.title,
            username=chat.username,
            first_name=chat.first_name,
            last_name=chat.last_name,
            is_forum=chat.is_forum,
            created_at=chat.created_at,
        )
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return ChatSchema.model_validate(db_chat)

    def try_create_chat(self, chat: ChatSchema) -> ChatSchema:
        """Try to create or update a chat record in the database.

        Args:
            chat: The chat schema to create or update

        Returns:
            The created or updated chat schema
        """
        logger.debug("Attempting to upsert chat with id=%d", chat.id)
        existing_chat = self.db.query(ChatDB).filter_by(id=chat.id).first()

        if existing_chat:
            logger.debug("Updating existing chat with id=%d", chat.id)
            for key, value in chat.model_dump().items():
                setattr(existing_chat, key, value)
            self.db.commit()
            self.db.refresh(existing_chat)
            return ChatSchema.model_validate(existing_chat)

        logger.debug("Creating new chat with id=%d", chat.id)
        return self.create_chat(chat)
