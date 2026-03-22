from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class Entitlement(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_entitlement'




    id_id = Column(BigInteger, ForeignKey('kkt_rfc_order_voucher.entitlement_id'), primary_key=True, autoincrement=True)

    visitor = Column(String(255), nullable=False, comment="权益归属的游客主体")



    sell_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_sell_item.id'), nullable=True, comment="对应售卖项")

    status = Column(String(20), nullable=False, default="PENDING", comment="权益状态")

    remaining_qty = Column(Integer)



    order_id = Column(BigInteger, ForeignKey('kkt_rfc_order_order.id'), nullable=True, comment="来源订单（奖励/管理员手动创建 可为空）")



    order_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_order_item.id'), nullable=True, comment="用于套餐/多行订单的精确追溯与对账；奖励/补发/管理员手动创建 可为空")

    challenge = Column(String(255), comment="来源挑战")

    created_by = Column(String(255), comment="管理员手动创建时的操作人（不为空 = 管理员操作，order/order_item 可为空）")

    start_at = Column(Date, comment="生效开始时间（用于有效期窗口）")

    end_at = Column(Date, comment="生效结束时间（过期时间）")

    meta = Column(JSON, nullable=False, comment="扩展信息（规则快照、核销限制、配额明细等）")


    sell_item = relationship("SellItem", back_populates="entitlement_set", foreign_keys=[sell_item_id])


    order = relationship("Order", back_populates="entitlement_set", foreign_keys=[order_id])


    order_item = relationship("OrderItem", back_populates="entitlement_set", foreign_keys=[order_item_id])

    redemptionlog_set = relationship("RedemptionLog", back_populates="entitlement")

    voucher_set = relationship("Voucher", back_populates="entitlement")


    id = relationship("Voucher", uselist=False, back_populates="entitlement_rel", foreign_keys=[id_id])