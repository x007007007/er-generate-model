from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class USER(Base):
    __tablename__ = 'input_user'
    id = Column(Integer, primary_key=True, comment="Primary key")
    username = Column(String(255), comment="Unique username")
    email = Column(String(255), comment="User email address")
    created_at = Column(Date, comment="Account creation timestamp")