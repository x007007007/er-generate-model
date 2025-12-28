from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class EMPTY(Base):
    __tablename__ = 'empty'