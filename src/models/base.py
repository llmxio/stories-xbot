from sqlalchemy.orm import DeclarativeBase


class BaseDbModel(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}
