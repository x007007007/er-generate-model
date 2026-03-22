from django.contrib import admin

from ..models import SellItemBundleItemModel


@admin.register(SellItemBundleItemModel)
class SellItemBundleItemModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'bundle_sell_item',
        'component_sell_item',
        'qty',
    ]
    list_filter = [
    ]
    search_fields = [
        'bundle_sell_item__code',
        'component_sell_item__code',
    ]
