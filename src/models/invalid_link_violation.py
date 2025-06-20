import sqlalchemy as sa

from .base import Base


class InvalidLinkViolation(Base):
    __tablename__ = "invalid_link_violation"
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey("chat.id"), nullable=False)
    count = sa.Column(sa.Integer)
    suspended_until = sa.Column(sa.DateTime)
