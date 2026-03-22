from django.contrib import admin

from ..models import OrderItemModel


@admin.register(OrderItemModel)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'order',
        'sell_item',
        'qty',
        'unit_amount',
        'amount',
        'meta',
        'created_at',
    ]
    list_filter = [
        'order',
        'sell_item',
    ]
    search_fields = [
        'order',
        'sell_item',
    ]
