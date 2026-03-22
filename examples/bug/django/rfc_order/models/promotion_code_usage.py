from django.db import models
from django.utils import timezone

from kinkotech.common.infrastructure import models as kmodel


class PromotionCodeUsageModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class PromotionCodeUsageModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    促销码使用记录模型
    """
    objects = PromotionCodeUsageModelQuerySet.as_manager()

    promotion_code = models.ForeignKey(
        to='kkt_rfc_order.PromotionCodeModel',
        on_delete=models.CASCADE,
        related_name='usages',
        help_text='关联促销码'
    )

    order = models.ForeignKey(
        to='kkt_rfc_order.OrderModel',
        on_delete=models.CASCADE,
        related_name='promotion_code_usages',
        help_text='关联订单'
    )

    visitor = models.ForeignKey(
        to='kkt_rfc_login.VisitorModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='关联使用者 visitor（为空场景：未登录但下单的文创购买）'
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='本次抵扣金额（便于对账与审计）'
    )

    used_at = models.DateTimeField(
        default=timezone.now,
        help_text='使用时间'
    )

    meta = models.JSONField(
        default=dict,
        blank=True,
        help_text='扩展信息'
    )

    class Meta:
        db_table = 'kkt_rfc_order_promotion_code_usage'
        constraints = [
            models.UniqueConstraint(
                fields=['promotion_code', 'order'],
                name='unique_promotion_code_order'
            ),
        ]
        indexes = [
            models.Index(fields=['promotion_code']),
            models.Index(fields=['order']),
            models.Index(fields=['visitor']),
        ]

    def __str__(self):
        return f"{self.__class__.__name__}_{self.pk}__promotion_{self.promotion_code.code}_order_{self.order.pk}"
