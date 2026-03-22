# Generated manually for default data initialization

from django.db import migrations


def create_default_sell_item_types(apps, schema_editor):
    """创建5条默认的售卖项类型记录"""
    SellItemTypeModel = apps.get_model('kkt_rfc_order', 'SellItemTypeModel')
    I18nLineModel = apps.get_model('kkt_i18n_translations', 'I18nLineModel')
    
    # 定义默认数据
    default_types = [
        {
            'code': 'MEMORY',
            'activation_mode': 'IMMEDIATE',
            'names': {
                'zh': '记忆功能',
                'en': 'Memory Features',
                'ko': '메모리 기능',
                'es': 'Funciones de memoria'
            }
        },
        {
            'code': 'TICKET',
            'activation_mode': 'REDEEM_REQUIRED',
            'names': {
                'zh': '景点门票',
                'en': 'Attraction Ticket',
                'ko': '명소 티켓',
                'es': 'Boleto de atracción'
            }
        },
        {
            'code': 'FOOD',
            'activation_mode': 'REDEEM_REQUIRED',
            'names': {
                'zh': '食品套餐',
                'en': 'Food Package',
                'ko': '식품 패키지',
                'es': 'Paquete de comida'
            }
        },
        {
            'code': 'ACTIVATION_CODE',
            'activation_mode': 'NONE',
            'names': {
                'zh': '激活码',
                'en': 'Activation Code',
                'ko': '활성화 코드',
                'es': 'Código de activación'
            }
        },
        {
            'code': 'CHALLENGE_PRIZE',
            'activation_mode': 'REDEEM_REQUIRED',
            'names': {
                'zh': '挑战奖励',
                'en': 'Challenge Prize',
                'ko': '챌린지 보상',
                'es': 'Premio del desafío'
            }
        },
    ]
    
    # 创建记录
    for type_data in default_types:
        # 检查是否已存在
        if SellItemTypeModel.objects.filter(code=type_data['code']).exists():
            continue
        
        # 创建多语言名称
        i18n_line = I18nLineModel.objects.create(
            zh=type_data['names']['zh'],
            en=type_data['names']['en'],
            ko=type_data['names']['ko'],
            es=type_data['names']['es'],
        )
        
        # 创建售卖项类型
        SellItemTypeModel.objects.create(
            code=type_data['code'],
            activation_mode=type_data['activation_mode'],
            name=i18n_line,
            meta={}
        )


def reverse_default_sell_item_types(apps, schema_editor):
    """删除默认的售卖项类型记录"""
    SellItemTypeModel = apps.get_model('kkt_rfc_order', 'SellItemTypeModel')
    
    default_codes = ['MEMORY', 'TICKET', 'FOOD', 'ACTIVATION_CODE', 'CHALLENGE_PRIZE']
    
    # 删除记录（包括关联的i18n记录会通过SET_NULL处理）
    SellItemTypeModel.objects.filter(code__in=default_codes).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('kkt_rfc_order', '0003_add_amount_currency_to_sell_item'),
        ('kkt_i18n_translations', '__first__'),
    ]

    operations = [
        migrations.RunPython(
            create_default_sell_item_types,
            reverse_default_sell_item_types
        ),
    ]


