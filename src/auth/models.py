from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.auth.database import Base


class Url(Base):
    __tablename__ = 'url'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_date: Mapped[str] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )
    expires_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    click_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)