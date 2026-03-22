from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class RedemptionLog(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_redemption_log'


    id = Column(BigInteger, primary_key=True, autoincrement=True)

    event_type = Column(String(50), nullable=False, comment="事件类型")

    source = Column(String(30), nullable=False, comment="来源端")

    request_id = Column(String(128), nullable=False, unique=True, comment="幂等键（终端/客户端生成；用于防重复扣减/重复兑换）")

    visitor = Column(String(255), comment="关联游客主体（可空场景：未登录的券兑换）")

    poi = Column(String(255), comment="核销点")



    sell_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_sell_item.id'), nullable=True, comment="关联售卖项（权益核销/购买相关事件）")



    entitlement_id = Column(BigInteger, ForeignKey('kkt_rfc_order_entitlement.id'), nullable=True, comment="关联权益单据")



    voucher_id = Column(BigInteger, ForeignKey('kkt_rfc_order_voucher.id'), nullable=True, comment="关联券（兑换事件）")

    user = Column(String(255), comment="终端登录的商户账号（执行者）")

    pos = Column(String(255), comment="执行核销的 POS 设备")

    result = Column(String(20), nullable=False, comment="结果")

    meta = Column(JSON, nullable=False)


    sell_item = relationship("SellItem", back_populates="redemptionlog_set", foreign_keys=[sell_item_id])


    entitlement = relationship("Entitlement", back_populates="redemptionlog_set", foreign_keys=[entitlement_id])


    voucher = relationship("Voucher", back_populates="redemptionlog_set", foreign_keys=[voucher_id])