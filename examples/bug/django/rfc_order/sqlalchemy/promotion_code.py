from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base





from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel, EnabledMixinModel






class PromotionCode(KinkoTechModelBase, CreateModifyMixinModel, EnabledMixinModel):
    __tablename__ = 'kkt_rfc_order_promotioncodemodel'


    id = Column(BigInteger, primary_key=True, autoincrement=True)

    code = Column(String(128), nullable=False, unique=True, comment="促销码文本（如 HOLIDAY20）")

    discount_type = Column(String(20), nullable=False, comment="折扣类型")

    discount_value = Column(Numeric(10, 2), nullable=False, comment="PERCENT 时表示百分比（如 20=20%）；FIXED 时表示固定减免金额")

    valid_from = Column(Date, comment="有效期开始")

    valid_to = Column(Date, comment="有效期结束")

    usage_limit_total = Column(Integer, comment="全局使用次数上限")

    usage_limit_per_identity = Column(Integer, comment="每个游客主体（visitor）使用次数上限")

    meta = Column(JSON, nullable=False, comment="扩展信息（适用商品范围、备注等）")

    promotioncodeusage_set = relationship("PromotionCodeUsage", back_populates="promotion_code")