from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class PromotionCodeUsage(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_promotion_code_usage'


    id = Column(BigInteger, primary_key=True, autoincrement=True)



    promotion_code_id = Column(BigInteger, ForeignKey('kkt_rfc_order_promotioncodemodel.id'), nullable=False, comment="关联促销码")



    order_id = Column(BigInteger, ForeignKey('kkt_rfc_order_order.id'), nullable=False, comment="关联订单")

    visitor = Column(String(255), comment="关联使用者 visitor（为空场景：未登录但下单的文创购买）")

    discount_amount = Column(Numeric(10, 2), comment="本次抵扣金额（便于对账与审计）")

    used_at = Column(Date, nullable=False, comment="使用时间")

    meta = Column(JSON, nullable=False, comment="扩展信息")


    promotion_code = relationship("PromotionCode", back_populates="promotioncodeusage_set", foreign_keys=[promotion_code_id])


    order = relationship("Order", back_populates="promotioncodeusage_set", foreign_keys=[order_id])