from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class SellItemBundleItemModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class SellItemBundleItemModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    套餐售卖项组成明细模型

    """
    objects = SellItemBundleItemModelQuerySet.as_manager()

    bundle_sell_item = models.ForeignKey(
        to='kkt_rfc_order.SellItemModel',
        on_delete=models.CASCADE,
        related_name='bundle_items',
    )
    
    component_sell_item = models.ForeignKey(
        to='kkt_rfc_order.SellItemModel',
        on_delete=models.CASCADE,
        related_name='component_in_bundles',
        help_text='子售卖项（要求 sell_item.is_bundle=false）',
        blank=True,
        null=True,
    )
    
    qty = models.IntegerField(
        default=1,
    )
    
    meta = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = 'kkt_rfc_order_sell_item_bundle_item'
        constraints = [
            models.UniqueConstraint(
                fields=['bundle_sell_item', 'component_sell_item'],
                name='unique_bundle_component'
            ),
            models.CheckConstraint(
                check=models.Q(bundle_sell_item_id__isnull=False) & 
                      ~models.Q(bundle_sell_item_id=models.F('component_sell_item_id')),
                name='bundle_not_equal_component'
            ),
        ]
        indexes = [
            models.Index(fields=['bundle_sell_item']),
            models.Index(fields=['component_sell_item']),
        ]