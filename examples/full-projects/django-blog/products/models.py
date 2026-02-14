"""
Product management models
"""
from django.db import models
from decimal import Decimal


class Category(models.Model):
    """产品分类"""
    name = models.CharField(max_length=100, unique=True, help_text="分类名称")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL别名")
    description = models.TextField(blank=True, help_text="分类描述")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="父分类"
    )
    image = models.URLField(blank=True, help_text="分类图片")
    is_active = models.BooleanField(default=True, help_text="是否激活")
    sort_order = models.PositiveIntegerField(default=0, help_text="排序")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products_category'
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    """品牌"""
    name = models.CharField(max_length=100, unique=True, help_text="品牌名称")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL别名")
    description = models.TextField(blank=True, help_text="品牌描述")
    logo = models.URLField(blank=True, help_text="品牌Logo")
    website = models.URLField(blank=True, help_text="官方网站")
    is_active = models.BooleanField(default=True, help_text="是否激活")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products_brand'
        verbose_name = '品牌'
        verbose_name_plural = '品牌'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """产品"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '上架'),
        ('inactive', '下架'),
        ('discontinued', '停产'),
    ]
    
    name = models.CharField(max_length=200, help_text="产品名称")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL别名")
    description = models.TextField(help_text="产品描述")
    short_description = models.CharField(max_length=500, blank=True, help_text="简短描述")
    
    # 分类和品牌
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        help_text="产品分类"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='products',
        help_text="品牌"
    )
    
    # 价格信息
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="价格"
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="成本价"
    )
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="对比价格"
    )
    
    # 库存信息
    sku = models.CharField(max_length=100, unique=True, help_text="SKU")
    stock_quantity = models.PositiveIntegerField(default=0, help_text="库存数量")
    track_inventory = models.BooleanField(default=True, help_text="是否跟踪库存")
    
    # 产品属性
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="重量(kg)"
    )
    dimensions = models.CharField(max_length=100, blank=True, help_text="尺寸")
    
    # 状态和设置
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="产品状态"
    )
    is_featured = models.BooleanField(default=False, help_text="是否精选")
    is_digital = models.BooleanField(default=False, help_text="是否数字产品")
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO标题")
    meta_description = models.CharField(max_length=300, blank=True, help_text="SEO描述")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    published_at = models.DateTimeField(null=True, blank=True, help_text="发布时间")
    
    class Meta:
        db_table = 'products_product'
        verbose_name = '产品'
        verbose_name_plural = '产品'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['brand', 'status']),
            models.Index(fields=['is_featured', 'status']),
        ]
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """产品图片"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="关联产品"
    )
    image_url = models.URLField(help_text="图片URL")
    alt_text = models.CharField(max_length=200, blank=True, help_text="替代文本")
    is_primary = models.BooleanField(default=False, help_text="是否主图")
    sort_order = models.PositiveIntegerField(default=0, help_text="排序")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products_productimage'
        verbose_name = '产品图片'
        verbose_name_plural = '产品图片'
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f'{self.product.name} - Image {self.id}'


class ProductVariant(models.Model):
    """产品变体"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        help_text="关联产品"
    )
    name = models.CharField(max_length=200, help_text="变体名称")
    sku = models.CharField(max_length=100, unique=True, help_text="变体SKU")
    
    # 价格（可以覆盖主产品价格）
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="变体价格"
    )
    
    # 库存
    stock_quantity = models.PositiveIntegerField(default=0, help_text="库存数量")
    
    # 变体属性
    color = models.CharField(max_length=50, blank=True, help_text="颜色")
    size = models.CharField(max_length=50, blank=True, help_text="尺寸")
    material = models.CharField(max_length=100, blank=True, help_text="材质")
    
    is_active = models.BooleanField(default=True, help_text="是否激活")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'products_productvariant'
        verbose_name = '产品变体'
        verbose_name_plural = '产品变体'
        unique_together = ['product', 'color', 'size', 'material']
    
    def __str__(self):
        return f'{self.product.name} - {self.name}'