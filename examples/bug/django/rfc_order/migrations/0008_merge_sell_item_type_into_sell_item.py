"""
合并 SellItemTypeModel 到 SellItemModel

步骤：
1. 在 sell_item 表新增 sell_item_type_code / activation_mode 字段
2. 数据迁移：从关联的 sell_item_type 行拷贝 code → sell_item_type_code, activation_mode → activation_mode
3. 移除 sell_item 表上的 sell_item_type FK 及旧索引
4. 添加新索引
5. 删除 sell_item_type 表
"""

from django.db import migrations, models


def copy_type_fields(apps, schema_editor):
    """将 sell_item_type 的 code/activation_mode 拷贝到 sell_item 自身字段"""
    SellItemModel = apps.get_model('kkt_rfc_order', 'SellItemModel')

    for sell_item in SellItemModel.objects.select_related('sell_item_type').all():
        if sell_item.sell_item_type:
            sell_item.sell_item_type_code = sell_item.sell_item_type.code
            sell_item.activation_mode = sell_item.sell_item_type.activation_mode
            sell_item.save(update_fields=['sell_item_type_code', 'activation_mode'])


def reverse_copy_type_fields(apps, schema_editor):
    """反向：无法自动还原，仅做占位"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('kkt_rfc_order', '0007_rename_buyer_email_sales_poi_add_original_amount_remove_both'),
    ]

    operations = [
        # ── 1. 新增字段 ──
        migrations.AddField(
            model_name='sellitemmodel',
            name='sell_item_type_code',
            field=models.CharField(
                blank=True,
                choices=[
                    ('MEMORY', 'Memory'),
                    ('TICKET', 'Ticket'),
                    ('FOOD', 'Food'),
                    ('ACTIVATION_CODE', 'Activation Code'),
                    ('CHALLENGE_PRIZE', 'Challenge Prize'),
                ],
                db_index=True,
                help_text='售卖项类型编码（MEMORY/TICKET/FOOD/ACTIVATION_CODE/CHALLENGE_PRIZE）',
                max_length=64,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='sellitemmodel',
            name='activation_mode',
            field=models.CharField(
                choices=[
                    ('REDEEM_REQUIRED', 'Redeem Required'),
                    ('IMMEDIATE', 'Immediate'),
                    ('NONE', 'None'),
                ],
                default='NONE',
                help_text='激活/履约方式（REDEEM_REQUIRED=需核销；IMMEDIATE=立即生效；NONE=无需履约）',
                max_length=20,
            ),
        ),

        # ── 2. 数据迁移 ──
        migrations.RunPython(copy_type_fields, reverse_copy_type_fields),

        # ── 3. 移除旧索引 + FK ──
        migrations.RemoveIndex(
            model_name='sellitemmodel',
            name='kkt_rfc_ord_sell_it_a5ab39_idx',  # sell_item_type FK 索引
        ),
        migrations.RemoveField(
            model_name='sellitemmodel',
            name='sell_item_type',
        ),

        # ── 4. 添加新索引 ──
        migrations.AddIndex(
            model_name='sellitemmodel',
            index=models.Index(fields=['sell_item_type_code'], name='kkt_rfc_ord_sell_it_bcaad6_idx'),
        ),

        # ── 5. 删除 SellItemTypeModel 表 ──
        migrations.DeleteModel(
            name='SellItemTypeModel',
        ),
    ]

