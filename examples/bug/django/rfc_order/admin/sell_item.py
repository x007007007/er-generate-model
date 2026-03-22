from django.contrib import admin

from ..models import SellItemModel


@admin.register(SellItemModel)
class SellItemModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'code',
        'name',
        'is_bundle',
        'category',
        'sell_item_type_code',
        'activation_mode',
        'purchasable_identity',
    ]
    list_filter = [
        'is_bundle',
        'category',
        'sell_item_type_code',
        'activation_mode',
        'purchasable_identity',
    ]
    search_fields = [
        'code',
    ]
