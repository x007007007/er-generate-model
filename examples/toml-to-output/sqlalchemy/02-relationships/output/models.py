from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class USER(Base):
    __tablename__ = 'input_user'
    id = Column(UUID, primary_key=True, comment="Primary key")
    username = Column(String(255), comment="Unique username")
    email = Column(String(255), comment="User email address")
    age = Column(Integer, comment="User age")
    is_active = Column(Boolean, comment="Whether the user account is active")
    created_at = Column(Date, comment="Account creation timestamp")
    post_set = relationship("POST", back_populates="user_rel")

class POST(Base):
    __tablename__ = 'input_post'
    id = Column(UUID, primary_key=True, comment="Primary key")
    author_id = Column(UUID, ForeignKey('input_user.id'), comment="Foreign key to User")
    title = Column(String(255), comment="Post title")
    content = Column(Text, comment="Post content")
    created_at = Column(Date, comment="Post creation timestamp")
    user_rel = relationship("USER", back_populates="post_set")