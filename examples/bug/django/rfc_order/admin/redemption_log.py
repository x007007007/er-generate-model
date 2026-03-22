from django.contrib import admin

from ..models import RedemptionLogModel


@admin.register(RedemptionLogModel)
class RedemptionLogModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'event_type',
        'source',
        'request_id',
        'visitor',
        'poi',
        'sell_item',
        'entitlement',
        'voucher',
        'user',
        'pos',
        'result',
        'created_at',
    ]
    list_filter = [
        'event_type',
        'source',
        'result',
    ]
    search_fields = [
        'request_id',
        'visitor__nfc_uid__uid',
        'visitor__activation_code__code',
    ]