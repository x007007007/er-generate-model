from django.contrib import admin

from ..models import OrderModel


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'visitor',
        'status',
        'original_amount',
        'amount',
        'currency',
        'sales_channel',
        'poi',
        'payment_provider',
        'payment_transaction_id',
        'paid_at',
        'email',
        'created_at',
    ]
    list_filter = [
        'status',
        'sales_channel',
        'payment_provider',
        'paid_at',
        'created_at',
    ]
    search_fields = [
        'email',
        'payment_transaction_id',
        'visitor__nfc_uid__uid',
        'visitor__activation_code__code',
        'sell_item__code',
    ]