"""SQLAlchemy models — mirrors the 6-table Drizzle schema from the edu platform."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(JSONB, nullable=False)
    description = Column(JSONB, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    category = Column(JSONB, nullable=True)
    educator_name = Column(String(255), nullable=True)
    is_published = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    videos = relationship("Video", back_populates="course", cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(JSONB, nullable=False)
    description = Column(JSONB, nullable=True)
    video_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    duration_sec = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    course = relationship("Course", back_populates="videos")
    learning_content = relationship("LearningContent", back_populates="video", cascade="all, delete-orphan")


class LearningContent(Base):
    __tablename__ = "learning_content"
    __table_args__ = (UniqueConstraint("video_id", "content_type"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(20), nullable=False)  # quiz, flashcards, mental_map, test
    content = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    video = relationship("Video", back_populates="learning_content")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), default=utcnow)


class Progress(Base):
    __tablename__ = "progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("learning_content.id", ondelete="CASCADE"), nullable=True)
    progress_type = Column(String(20), nullable=False)  # video, quiz, test, flashcard
    data = Column(JSONB, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
