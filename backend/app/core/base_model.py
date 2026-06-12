"""
ORM基类
职责：
- 提供SQLAlchemy声明式基类，供models层各模型继承
- 统一公共字段（如id、创建时间、更新时间）
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有ORM模型的基类"""
    pass


class TimestampMixin:
    """公共时间字段，需要的模型可混入使用"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class IDMixin:
    """公共自增主键，需要的模型可混入使用"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)