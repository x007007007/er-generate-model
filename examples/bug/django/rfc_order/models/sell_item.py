from django.db import models

from kinkotech.common.infrastructure import models as kmodel


class SellItemModelQuerySet(kmodel.KinkoTechQuerySet):
    pass


class SellItemModel(
    kmodel.KinkoTechModelBase,
    kmodel.CreateModifyMixinModel,
):
    """
    售卖项模型
    普通单品售卖项或组合套餐售卖项
    """
    objects = SellItemModelQuerySet.as_manager()

    code = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        help_text='售卖项编码（用于配置/对接/运营导入）'
    )

    name = models.ForeignKey(
        to='kkt_i18n_translations.I18nLineModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='售卖项名称（短文案，多语言）'
    )

    is_bundle = models.BooleanField(
        default=False,
        db_index=True,
        help_text='是否为"组合套餐售卖项"（false：普通单品；true：套餐，其组成由 sell_item_bundle_item 定义）'
    )

    sell_item_type_code = models.CharField(
        max_length=64,
        choices=[
            ('MEMORY', 'Memory'),
            ('TICKET', 'Ticket'),
            ('FOOD_TOUR', 'Food Tour'),
            ('CHALLENGE_PRIZE', 'Challenge Prize'),
            ('ACTIVATION_CODE', 'Activation Code'),
            ('CANVAS', 'Canvas'),
        ],
        null=True,
        blank=True,
        db_index=True,
        help_text='售卖项类型编码（MEMORY/TICKET/FOOD_TOUR/CHALLENGE_PRIZE/ACTIVATION_CODE/CANVAS）'
    )

    activation_mode = models.CharField(
        max_length=20,
        choices=[
            ('REDEEM_REQUIRED', 'Redeem Required'),
            ('IMMEDIATE', 'Immediate'),
        ],
        default='REDEEM_REQUIRED',
        help_text='激活/履约方式（REDEEM_REQUIRED=需核销；IMMEDIATE=购买/激活即生效，不生成voucher）'
    )

    category = models.CharField(
        max_length=20,
        choices=[
            ('PACKAGE', 'Package'),
            ('ADD_ON', 'Add-on'),
        ],
        default='ADD_ON',
        db_index=True,
        help_text='售卖项类别（PACKAGE=套餐包，任何人可购买；ADD_ON=附加项，需登录态）'
    )

    purchasable_identity = models.CharField(
        max_length=20,
        choices=[
            ('ANY', 'Any'),
            ('ACTIVATION_CODE_ONLY', 'Activation Code Only'),
            ('NFC_ONLY', 'NFC Only'),
            ('LOGGED_IN', 'Logged In'),
        ],
        default='LOGGED_IN',
        help_text='可购买人群（ANY=任何人含email-only；LOGGED_IN=需登录态；ACTIVATION_CODE_ONLY=仅激活码用户；NFC_ONLY=仅NFC用户）'
    )

    description = models.ForeignKey(
        to='kkt_i18n_translations.I18nBlockModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sell_item_description_i18n',
        help_text='售卖项详情描述（长文案，多语言，可选）'
    )

    route = models.ForeignKey(
        to='kkt_rfc_backend_route_plan.RouteModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='可以关联一条游览线路'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='售价（与 order 表保持一致）'
    )

    currency = models.CharField(
        max_length=8,
        default='CNY',
        help_text='币种（与 order 表保持一致）'
    )

    meta = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = 'kkt_rfc_order_sell_item'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_bundle']),
            models.Index(fields=['sell_item_type_code']),
        ]

    def __str__(self):
        return f"{self.__class__.__name__}_{self.pk}__{self.code}"
