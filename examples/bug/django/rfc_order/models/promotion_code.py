from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class PromotionCodeModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class PromotionCodeModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
    kmodel.EnabledMixinModel,
):
    """
    促销码模型
    """
    objects = PromotionCodeModelQuerySet.as_manager()

    code = models.CharField(
        max_length=128,
        unique=True,
        help_text='促销码文本（如 HOLIDAY20）'
    )

    discount_type = models.CharField(
        max_length=20,
        choices=[
            ('PERCENT', 'Percent'),
            ('FIXED', 'Fixed'),
        ],
        help_text='折扣类型'
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='PERCENT 时表示百分比（如 20=20%）；FIXED 时表示固定减免金额'
    )

    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text='有效期开始'
    )

    valid_to = models.DateTimeField(
        null=True,
        blank=True,
        help_text='有效期结束'
    )

    usage_limit_total = models.IntegerField(
        null=True,
        blank=True,
        help_text='全局使用次数上限'
    )

    usage_limit_per_identity = models.IntegerField(
        null=True,
        blank=True,
        help_text='每个游客主体（visitor）使用次数上限'
    )

    meta = models.JSONField(
        default=dict,
        blank=True,
        help_text='扩展信息（适用商品范围、备注等）'
    )

    def __str__(self):
        return f"{self.__class__.__name__}_{self.pk}__{self.code}"
