from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class VoucherModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class VoucherModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    券模型
    文创兑换券/奖品券
    voucher 只负责"出示的券码"，是否已核销/是否可用以 entitlement.status 为准（避免双表状态）
    """
    objects = VoucherModelQuerySet.as_manager()

    entitlement = models.OneToOneField(
        to='kkt_rfc_order.EntitlementModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voucher'
    )

    code = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        help_text='券码（二维码内容，一次性兑换凭证）'
    )

    order = models.ForeignKey(
        to='kkt_rfc_order.OrderModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='来源订单（文创购买券：关联订单；挑战奖品券：可为空）'
    )

    order_item = models.ForeignKey(
        to='kkt_rfc_order.OrderItemModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='来源订单行,voucher_type=REDEEM 建议必填,CHALLENGE_PRIZE 可为空'
    )

    voucher_type = models.CharField(
        max_length=30,
        choices=[
            ('REDEEM', 'Redeem'),
            ('CHALLENGE_PRIZE', 'Challenge Prize'),
        ],
        db_index=True,
    )

    sell_item = models.ForeignKey(
        to='kkt_rfc_order.SellItemModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    issued_seq = models.IntegerField(
        default=1,
    )

    meta = models.JSONField(
        default=dict,
        blank=True,
        help_text='扩展信息'
    )

    class Meta:
        db_table = 'kkt_rfc_order_voucher'
        indexes = [
            models.Index(fields=['voucher_type']),
            models.Index(fields=['order']),
            models.Index(fields=['order_item']),
            models.Index(fields=['sell_item']),
            models.Index(fields=['entitlement']),
        ]

    def __str__(self):
        return f"{self.__class__.__name__}_{self.pk}__{self.code}"
