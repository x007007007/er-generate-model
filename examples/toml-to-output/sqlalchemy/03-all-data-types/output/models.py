from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DATA_TYPE_SHOWCASE(Base):
    __tablename__ = 'input_data_type_showcase'
    id = Column(UUID, primary_key=True, comment="主键-UUID类型")
    name = Column(String(255), comment="字符串-可变长度")
    description = Column(String(255), comment="可变字符-同string")
    code = Column(String(255), comment="固定长度字符")
    content = Column(Text, comment="大文本内容")
    count = Column(Integer, comment="整数-32位")
    quantity = Column(Integer, comment="整数-同int")
    big_number = Column(Integer, comment="大整数-64位")
    small_number = Column(Integer, comment="小整数-16位")
    tiny_number = Column(Integer, comment="微整数-8位")
    rating = Column(Float, comment="浮点数-单精度")
    weight = Column(Float, comment="浮点数-同float")
    score = Column(Float, comment="浮点数-双精度")
    price = Column(Numeric(10, 2), comment="精确小数-货币")
    amount = Column(Numeric(10, 2), comment="精确小数-同decimal")
    is_active = Column(Boolean, comment="布尔值-真假")
    is_enabled = Column(Boolean, comment="布尔值-同boolean")
    birth_date = Column(Date, comment="日期-年月日")
    start_time = Column(Time, comment="时间-时分秒")
    created_at = Column(Date, comment="日期时间-完整")
    updated_at = Column(Time, comment="时间戳-Unix")
    metadata = Column(JSON, comment="JSON对象")
    settings = Column(JSON, comment="二进制JSON")