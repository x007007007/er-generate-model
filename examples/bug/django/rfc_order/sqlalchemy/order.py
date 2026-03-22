from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class Order(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_order'


    id = Column(BigInteger, primary_key=True, autoincrement=True)

    category = Column(String(20), nullable=False, comment="订单类型：PACKAGE（套餐） / ADD_ON（加购）")

    visitor = Column(String(255), comment="关联购买者（email-only 购买 Package 时也会创建 visitor）")

    status = Column(String(20), nullable=False, default="PENDING", comment="订单状态")

    original_amount = Column(Numeric(10, 2), comment="原价金额（优惠前）")

    amount = Column(Numeric(10, 2), nullable=False, comment="实付金额")

    currency = Column(String(8), nullable=False, default="CNY", comment="币种")

    sales_channel = Column(String(20), comment="销售渠道")

    poi = Column(String(255), comment="销售发生的POI（线下点位下单可填；线上可空）")

    payment_provider = Column(String(20), comment="支付渠道")

    payment_transaction_id = Column(String(128), comment="第三方支付流水号（用于退款/对账）")

    paid_at = Column(Date, comment="支付完成时间")

    email = Column(String(255), comment="收券/通知邮箱（当 visitor_id 为空（仅激活码订单）时必填；其余场景可选（用于发券通知/客服沟通））")

    meta = Column(JSON, nullable=False)

    orderitem_set = relationship("OrderItem", back_populates="order")

    promotioncodeusage_set = relationship("PromotionCodeUsage", back_populates="order")

    entitlement_set = relationship("Entitlement", back_populates="order")

    voucher_set = relationship("Voucher", back_populates="order")