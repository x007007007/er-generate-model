from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class OrderItemModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class OrderItemModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    订单行模型
    履约/发券/发权益的"明细源数据"
    普通单品订单：建议也创建 1 条 order_item
    套餐订单：按 sell_item_bundle_item 展开生成多条 order_item，用于后续批量发券（或发权益）
    """
    objects = OrderItemModelQuerySet.as_manager()

    order = models.ForeignKey(
        to='kkt_rfc_order.OrderModel',
        on_delete=models.CASCADE,
        related_name='items',
        help_text='关联订单'
    )

    sell_item = models.ForeignKey(
        to='kkt_rfc_order.SellItemModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='该行对应的"子售卖项"'
    )

    qty = models.IntegerField(
        default=1,
    )

    unit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='行单价'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='行小计,等于 unit_amount*qty'
    )

    meta = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = 'kkt_rfc_order_order_item'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['sell_item']),
        ]

    def __str__(self):
        return f"{self.__class__.__name__}_{self.pk}__order_{self.order.pk}_sell_item_{self.sell_item.code if self.sell_item else 'none'}"
