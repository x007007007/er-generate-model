from django.contrib import admin

from ..models import PromotionCodeModel


@admin.register(PromotionCodeModel)
class PromotionCodeModelAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'code',
        'discount_type',
        'discount_value',
        'valid_from',
        'valid_to',
        'usage_limit_total',
        'usage_limit_per_identity',
        'is_enabled',
    ]
    list_filter = [
        'discount_type',
        'is_enabled',
        'valid_from',
        'valid_to',
    ]
    search_fields = [
        'code',
    ]