from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class OrderModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class OrderModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    订单模型

    category 标识订单类型（PACKAGE / ADD_ON），购买明细统一由 order_item 承载。
    """
    objects = OrderModelQuerySet.as_manager()

    category = models.CharField(
        max_length=20,
        choices=[
            ('PACKAGE', 'Package'),
            ('ADD_ON', 'Add-on'),
        ],
        db_index=True,
        help_text='订单类型：PACKAGE（套餐） / ADD_ON（加购）'
    )

    visitor = models.ForeignKey(
        to='kkt_rfc_login.VisitorModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='关联购买者（email-only 购买 Package 时也会创建 visitor）'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('CANCELLED', 'Cancelled'),
            ('REFUNDED', 'Refunded'),
        ],
        default='PENDING',
        db_index=True,
        help_text='订单状态'
    )

    original_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='原价金额（优惠前）'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='实付金额'
    )

    currency = models.CharField(
        max_length=8,
        default='CNY',
        help_text='币种'
    )

    sales_channel = models.CharField(
        max_length=20,
        choices=[
            ('ONLINE_STORE', 'Online Store'),
            ('OFFLINE_POI', 'Offline POI'),
            ('OTHER', 'Other'),
        ],
        null=True,
        blank=True,
        help_text='销售渠道'
    )

    poi = models.ForeignKey(
        to='kkt_rfc_tour_guide.POIModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='销售发生的POI（线下点位下单可填；线上可空）'
    )

    payment_provider = models.CharField(
        max_length=20,
        choices=[
            ('WECHAT', 'WeChat'),
            ('ALIPAY', 'Alipay'),
            ('MOCK', 'Mock'),
        ],
        null=True,
        blank=True,
        help_text='支付渠道'
    )

    payment_transaction_id = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        db_index=True,
        help_text='第三方支付流水号（用于退款/对账）'
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='支付完成时间'
    )

    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        help_text='收券/通知邮箱（当 visitor_id 为空（仅激活码订单）时必填；其余场景可选（用于发券通知/客服沟通））'
    )

    meta = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = 'kkt_rfc_order_order'
        constraints = [
            models.CheckConstraint(
                check=models.Q(visitor__isnull=False) | models.Q(email__isnull=False),
                name='order_requires_visitor_or_email'
            ),
        ]
        indexes = [
            models.Index(fields=['paid_at']),
            models.Index(fields=['payment_transaction_id']),
        ]
