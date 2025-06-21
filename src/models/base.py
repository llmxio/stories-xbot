from sqlalchemy.orm import DeclarativeBase


class BaseSqlaModel(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}
