from sqlalchemy import BigInteger, Column, Integer, String, ForeignKey, Boolean, Date, DateTime, Time, Text, Float, Numeric, JSON
from sqlalchemy.orm import relationship
from kinkotech.base_sqlalchemy import Base




from kinkotech.common.infrastructure.models.base import KinkoTechModelBase, CreateModifyMixinModel





class SellItem(KinkoTechModelBase, CreateModifyMixinModel):
    __tablename__ = 'kkt_rfc_order_sell_item'


    id = Column(BigInteger, primary_key=True, autoincrement=True)

    code = Column(String(128), nullable=False, unique=True, comment="售卖项编码（用于配置/对接/运营导入）")

    name = Column(String(255), comment="售卖项名称（短文案，多语言）")

    is_bundle = Column(Boolean, nullable=False, default=False, comment='是否为"组合套餐售卖项"（false：普通单品；true：套餐，其组成由 sell_item_bundle_item 定义）')

    sell_item_type_code = Column(String(64), comment="售卖项类型编码（MEMORY/TICKET/FOOD_TOUR/CHALLENGE_PRIZE/ACTIVATION_CODE/CANVAS）")

    activation_mode = Column(String(20), nullable=False, default="REDEEM_REQUIRED", comment="激活/履约方式（REDEEM_REQUIRED=需核销；IMMEDIATE=购买/激活即生效，不生成voucher）")

    category = Column(String(20), nullable=False, default="ADD_ON", comment="售卖项类别（PACKAGE=套餐包，任何人可购买；ADD_ON=附加项，需登录态）")

    purchasable_identity = Column(String(20), nullable=False, default="LOGGED_IN", comment="可购买人群（ANY=任何人含email-only；LOGGED_IN=需登录态；ACTIVATION_CODE_ONLY=仅激活码用户；NFC_ONLY=仅NFC用户）")

    description = Column(String(255), comment="售卖项详情描述（长文案，多语言，可选）")

    route = Column(String(255), comment="可以关联一条游览线路")

    amount = Column(Numeric(10, 2), comment="售价（与 order 表保持一致）")

    currency = Column(String(8), nullable=False, default="CNY", comment="币种（与 order 表保持一致）")

    meta = Column(JSON, nullable=False)

    orderitem_set = relationship("OrderItem", back_populates="sell_item")

    entitlement_set = relationship("Entitlement", back_populates="sell_item")

    redemptionlog_set = relationship("RedemptionLog", back_populates="sell_item")

    voucher_set = relationship("Voucher", back_populates="sell_item")

    sellitembundleitem_set = relationship("SellItemBundleItem", back_populates="bundle_sell_item")

    sellitembundleitem_set = relationship("SellItemBundleItem", back_populates="component_sell_item")