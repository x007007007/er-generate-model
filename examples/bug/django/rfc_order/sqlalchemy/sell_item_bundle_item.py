from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class SellItemBundleItem(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_sell_item_bundle_item'


    id = Column(BigInteger, primary_key=True, autoincrement=True)



    bundle_sell_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_sell_item.id'), nullable=False)



    component_sell_item_id = Column(BigInteger, ForeignKey('kkt_rfc_order_sell_item.id'), nullable=True, comment="子售卖项（要求 sell_item.is_bundle=false）")

    qty = Column(Integer, nullable=False, default=1)

    meta = Column(JSON, nullable=False)


    bundle_sell_item = relationship("SellItem", back_populates="sellitembundleitem_set", foreign_keys=[bundle_sell_item_id])


    component_sell_item = relationship("SellItem", back_populates="sellitembundleitem_set", foreign_keys=[component_sell_item_id])