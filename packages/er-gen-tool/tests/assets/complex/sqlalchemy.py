from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class USER(Base):
    __tablename__ = 'complex_user'
    id = Column(Integer, primary_key=True, comment="Primary key for user")
    username = Column(String(255), comment="Unique username")
    password = Column(String(255), comment="Encrypted password")
    email = Column(String(255), comment="User email address")
    last_login = Column(Date, comment="Last login timestamp")
    is_active = Column(Boolean, comment="Whether user is active")
    profile_rel = relationship("PROFILE", uselist=False, back_populates="user_rel")
    post_set = relationship("POST", back_populates="user_rel")

class PROFILE(Base):
    __tablename__ = 'complex_profile'
    id = Column(Integer, primary_key=True, comment="Profile primary key")
    user_id = Column(Integer, comment="Foreign key to USER")
    bio = Column(String(255), comment="User biography")
    avatar_url = Column(String(255), comment="Avatar image URL")
    user_rel = relationship("USER", uselist=False, back_populates="profile_rel")

class POST(Base):
    __tablename__ = 'complex_post'
    id = Column(Integer, primary_key=True, comment="Post primary key")
    author_id = Column(Integer, comment="Foreign key to USER (author)")
    title = Column(String(255), comment="Post title")
    content = Column(String(255), comment="Post content")
    created_at = Column(Date, comment="Post creation time")
    status = Column(String(255), comment="enum:draft,published,archived - Post status")
    user_rel = relationship("USER", back_populates="post_set")
    tag_set = relationship("TAG", secondary="complex_post_tag_association", back_populates="post_set")

class TAG(Base):
    __tablename__ = 'complex_tag'
    id = Column(Integer, primary_key=True, comment="Tag primary key")
    name = Column(String(255), comment="Tag name")
    post_set = relationship("POST", secondary="complex_post_tag_association", back_populates="tag_set")

class POST_TAGS(Base):
    __tablename__ = 'complex_post_tags'
    post_id = Column(Integer, comment="Foreign key to POST")
    tag_id = Column(Integer, comment="Foreign key to TAG")
complex_post_tag_association = Table(
    'complex_post_tag_association',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('complex_post.id')),
    Column('tag_id', Integer, ForeignKey('complex_tag.id'))
)