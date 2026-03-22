from django.contrib import admin

from ..models import VoucherModel


@admin.register(VoucherModel)
class VoucherModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'code',
        'voucher_type',
        'entitlement',
        'order',
        'order_item',
        'sell_item',
        'issued_seq',
        'created_at',
    ]
    list_filter = [
        'voucher_type',
        'created_at',
    ]
    search_fields = [
        'code',
        'order__pk',
        'sell_item__code',
    ]