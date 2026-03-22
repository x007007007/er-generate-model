from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkt_rfc_order', '0011_rename_food_to_food_tour'),
    ]

    operations = [
        # migrations.RemoveIndex(
        #     model_name='ordermodel',
        #     name='kkt_rfc_ord_sell_it_8b7c3e_idx',
        # ),
        migrations.RemoveIndex(
            model_name='ordermodel',
            name='kkt_rfc_ord_sell_it_2edd1e_idx',
        ),
        migrations.RemoveField(
            model_name='ordermodel',
            name='sell_item',
        ),
        migrations.AddField(
            model_name='ordermodel',
            name='category',
            field=models.CharField(
                choices=[('PACKAGE', 'Package'), ('ADD_ON', 'Add-on')],
                db_index=True,
                default='ADD_ON',
                help_text='订单类型：PACKAGE（套餐） / ADD_ON（加购）',
                max_length=20,
            ),
            preserve_default=False,
        ),
    ]
