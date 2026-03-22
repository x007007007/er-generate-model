from django.contrib import admin

from ..models import EntitlementModel


@admin.register(EntitlementModel)
class EntitlementModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'visitor',
        'sell_item',
        'status',
        'remaining_qty',
        'order',
        'order_item',
        'challenge',
        'voucher',
        'start_at',
        'end_at',
    ]
    list_filter = [
        'status',
        'start_at',
        'end_at',
    ]
    search_fields = [
    ]