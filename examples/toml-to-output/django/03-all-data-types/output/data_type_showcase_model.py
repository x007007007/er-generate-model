"""Model definition for DATA_TYPE_SHOWCASE."""
from django.db import models
from .data_type_showcase_manager import DATA_TYPE_SHOWCASEManager

class DATA_TYPE_SHOWCASE(models.Model):
    """Comprehensive showcase of all supported data types"""
    id = models.UUIDField(primary_key=True, help_text="主键-UUID类型")
    name = models.CharField(max_length=255, help_text="字符串-可变长度")
    description = models.CharField(max_length=255, help_text="可变字符-同string")
    code = models.CharField(max_length=255, help_text="固定长度字符")
    content = models.TextField(help_text="大文本内容")
    count = models.IntegerField(help_text="整数-32位")
    quantity = models.IntegerField(help_text="整数-同int")
    big_number = models.IntegerField(help_text="大整数-64位")
    small_number = models.IntegerField(help_text="小整数-16位")
    tiny_number = models.IntegerField(help_text="微整数-8位")
    rating = models.FloatField(help_text="浮点数-单精度")
    weight = models.FloatField(help_text="浮点数-同float")
    score = models.FloatField(help_text="浮点数-双精度")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="精确小数-货币")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="精确小数-同decimal")
    is_active = models.BooleanField(help_text="布尔值-真假")
    is_enabled = models.BooleanField(help_text="布尔值-同boolean")
    birth_date = models.DateField(help_text="日期-年月日")
    start_time = models.TimeField(help_text="时间-时分秒")
    created_at = models.DateField(help_text="日期时间-完整")
    updated_at = models.TimeField(help_text="时间戳-Unix")
    metadata = models.JSONField(help_text="JSON对象")
    settings = models.JSONField(help_text="二进制JSON")
    
    objects = DATA_TYPE_SHOWCASEManager()
    
    class Meta:
        app_label = 'input'
        db_table = 'input_data_type_showcase'
        verbose_name = "Comprehensive showcase of all supported data types"
        verbose_name_plural = "Comprehensive showcase of all supported data types"
    
    def __str__(self):
        return f"DATA_TYPE_SHOWCASE(id={self.pk})"