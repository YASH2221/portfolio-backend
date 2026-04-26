from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    short_description = Column(Text)
    full_description = Column(Text)
    problem_statement = Column(Text)
    challenges = Column(Text)
    tech_stack = Column(JSON)
    category = Column(String(50))
    thumbnail_url = Column(String(500))
    screenshots = Column(JSON)
    live_url = Column(String(500))
    github_url = Column(String(500))
    featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    proficiency = Column(Integer)
    years_experience = Column(Float)
    icon_name = Column(String(50))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Journey(Base):
    __tablename__ = "journey"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    organization = Column(String(200))
    location = Column(String(100))
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20))
    description = Column(Text)
    highlights = Column(JSON)
    tech_used = Column(JSON)
    icon_name = Column(String(50))
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True)
    visitor_id = Column(String(100))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    message_count = Column(Integer, default=0)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), nullable=False)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer)
    cached_response = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    page = Column(String(100), nullable=False)
    visitor_id = Column(String(100))
    referrer = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
