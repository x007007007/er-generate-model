from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class Voucher(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_voucher'


    id = Column(BigInteger, primary_key=True, autoincrement=True)



    entitlement_id = Column(BigInteger, ForeignKey('kkt_rfc_order_entitlement.id'), nullable=True, unique=True)

    code = Column(String(128), nullable=False, unique=True, comment="券码（二维码内容，一次性兑换凭证）")



    order_id = Column(BigInteger, ForeignKey('kkt_rfc_order_order.id'), nullable=True, comment="来源订单（文创购买券：关联订单；挑战奖品券：可为空）")



    order_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_order_item.id'), nullable=True, comment="来源订单行,voucher_type=REDEEM 建议必填,CHALLENGE_PRIZE 可为空")

    voucher_type = Column(String(30), nullable=False)



    sell_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_sell_item.id'), nullable=True)

    issued_seq = Column(Integer, nullable=False, default=1)

    meta = Column(JSON, nullable=False, comment="扩展信息")

    redemptionlog_set = relationship("RedemptionLog", back_populates="voucher")


    entitlement = relationship("Entitlement", back_populates="voucher_set", foreign_keys=[entitlement_id])


    order = relationship("Order", back_populates="voucher_set", foreign_keys=[order_id])


    order_item = relationship("OrderItem", back_populates="voucher_set", foreign_keys=[order_item_id])


    sell_item = relationship("SellItem", back_populates="voucher_set", foreign_keys=[sell_item_id])

    entitlement_rel = relationship("Entitlement", uselist=False, back_populates="id")