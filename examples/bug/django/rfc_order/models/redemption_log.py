from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class RedemptionLogModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class RedemptionLogModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    核销日志模型
    """
    objects = RedemptionLogModelQuerySet.as_manager()

    event_type = models.CharField(
        max_length=50,
        choices=[
            ('VOUCHER_REDEEM', 'Voucher Redeem'),
            ('CHALLENGE_CHECKIN', 'Challenge Checkin'),
        ],
        help_text='事件类型'
    )
    
    source = models.CharField(
        max_length=30,
        choices=[
            ('TERMINAL', 'Terminal'),
            ('MINIPROGRAM', 'MiniProgram'),
            ('ADMIN', 'Admin'),
        ],
        help_text='来源端'
    )
    
    request_id = models.CharField(
        max_length=128,
        unique=True,
        help_text='幂等键（终端/客户端生成；用于防重复扣减/重复兑换）'
    )
    
    visitor = models.ForeignKey(
        to='kkt_rfc_login.VisitorModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='关联游客主体（可空场景：未登录的券兑换）'
    )

    poi = models.ForeignKey(
        to='kkt_rfc_tour_guide.POIModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='核销点'
    )

    sell_item = models.ForeignKey(
        to='kkt_rfc_order.SellItemModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='关联售卖项（权益核销/购买相关事件）'
    )
    
    entitlement = models.ForeignKey(
        to='kkt_rfc_order.EntitlementModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='关联权益单据'
    )
    
    voucher = models.ForeignKey(
        to='kkt_rfc_order.VoucherModel',
        on_delete=models.SET_NULL,
        related_name='redemption_events',
        null=True,
        blank=True,
        help_text='关联券（兑换事件）'
    )


    user = models.ForeignKey(
        to='kinkotech_com_account.AccountModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='终端登录的商户账号（执行者）'
    )
    
    pos = models.ForeignKey(
        to='kkt_rfc_pos_config.PointOfSaleTerminalModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='执行核销的 POS 设备'
    )
    
    result = models.CharField(
        max_length=20,
        choices=[
            ('SUCCESS', 'Success'),
            ('FAIL', 'Fail'),
        ],
        help_text='结果'
    )
    
    meta = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = 'kkt_rfc_order_redemption_log'
