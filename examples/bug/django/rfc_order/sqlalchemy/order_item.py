from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class OrderItem(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_order_item'


    id = Column(BigInteger, primary_key=True, autoincrement=True)



    order_id = Column(BigInteger, ForeignKey('kkt_rfc_order_order.id'), nullable=False, comment="关联订单")



    sell_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_sell_item.id'), nullable=True, comment='该行对应的"子售卖项"')

    qty = Column(Integer, nullable=False, default=1)

    unit_amount = Column(Numeric(10, 2), comment="行单价")

    amount = Column(Numeric(10, 2), comment="行小计,等于 unit_amount*qty")

    meta = Column(JSON, nullable=False)


    order = relationship("Order", back_populates="orderitem_set", foreign_keys=[order_id])


    sell_item = relationship("SellItem", back_populates="orderitem_set", foreign_keys=[sell_item_id])

    entitlement_set = relationship("Entitlement", back_populates="order_item")

    voucher_set = relationship("Voucher", back_populates="order_item")