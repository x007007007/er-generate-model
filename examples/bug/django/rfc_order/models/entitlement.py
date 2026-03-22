from django.conf import settings
from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class EntitlementModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class EntitlementModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    权益模型

    来源三选一（数据库约束互斥）：
      1. order     — 订单购买产生
      2. challenge — 挑战奖励产生
      3. created_by — 管理员手动创建（此时 order / order_item / challenge 均为空）
    """
    objects = EntitlementModelQuerySet.as_manager()

    visitor = models.ForeignKey(
        to='kkt_rfc_login.VisitorModel',
        on_delete=models.CASCADE,
        help_text='权益归属的游客主体'
    )

    sell_item = models.ForeignKey(
        to='kkt_rfc_order.SellItemModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='对应售卖项'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('ACTIVE', 'Active'),
            ('USED_UP', 'Used Up'),
            ('EXPIRED', 'Expired'),
        ],
        default='PENDING',
        help_text='权益状态'
    )

    remaining_qty = models.IntegerField(
        null=True,
        blank=True,
    )

    order = models.ForeignKey(
        to='kkt_rfc_order.OrderModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='来源订单（奖励/管理员手动创建 可为空）'
    )

    order_item = models.ForeignKey(
        to='kkt_rfc_order.OrderItemModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='用于套餐/多行订单的精确追溯与对账；奖励/补发/管理员手动创建 可为空'
    )

    challenge = models.ForeignKey(
        to='kkt_rfc_challenge.ChallengeModel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='来源挑战'
    )

    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_created_entitlements',
        help_text='管理员手动创建时的操作人（不为空 = 管理员操作，order/order_item 可为空）'
    )

    start_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='生效开始时间（用于有效期窗口）'
    )

    end_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='生效结束时间（过期时间）'
    )

    meta = models.JSONField(
        default=dict,
        blank=True,
        help_text='扩展信息（规则快照、核销限制、配额明细等）'
    )

    class Meta:
        db_table = 'kkt_rfc_order_entitlement'
        constraints = [
            # 来源三选一：订单 / 挑战 / 管理员手动，互斥
            models.CheckConstraint(
                check=(
                    # 1. 来自订单：order 非空，challenge & created_by 为空
                    models.Q(
                        order__isnull=False,
                        challenge__isnull=True,
                        created_by__isnull=True,
                    )
                    # 2. 来自挑战：challenge 非空，order & created_by 为空
                    | models.Q(
                        challenge__isnull=False,
                        order__isnull=True,
                        created_by__isnull=True,
                    )
                    # 3. 管理员手动创建：created_by 非空，order & challenge 为空
                    | models.Q(
                        created_by__isnull=False,
                        order__isnull=True,
                        challenge__isnull=True,
                    )
                ),
                name='entitlement_source_mutually_exclusive'
            ),
            # order_item 只能在 order 存在时才有值
            models.CheckConstraint(
                check=models.Q(order_item__isnull=True) | models.Q(order__isnull=False),
                name='order_item_requires_order'
            ),
        ]
        indexes = [
            models.Index(fields=['visitor', 'status']),
            models.Index(fields=['visitor', 'sell_item']),
            models.Index(fields=['challenge']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        identifier = f"visitor_{self.visitor.pk}" if self.visitor else "no_visitor"
        sell_item_code = self.sell_item.code if self.sell_item else "no_sell_item"
        return f"{self.__class__.__name__}_{self.pk}__{identifier}_sell_item_{sell_item_code}"
