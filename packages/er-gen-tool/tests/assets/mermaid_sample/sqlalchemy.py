from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class USER(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), comment="User Name")
    email = Column(String(255))
    post_set = relationship("POST", back_populates="user_rel")

class POST(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    user_id = Column(Integer)
    user_rel = relationship("USER", back_populates="post_set")