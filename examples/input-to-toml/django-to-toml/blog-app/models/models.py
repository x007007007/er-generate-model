"""
Simplified Blog models for Django to TOML conversion example
"""
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=100, unique=True, help_text="分类名称")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL别名")
    description = models.TextField(blank=True, help_text="分类描述")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blog_category'
        ordering = ['name']


class Post(models.Model):
    """博客文章"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]
    
    title = models.CharField(max_length=200, help_text="文章标题")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL别名")
    content = models.TextField(help_text="文章内容")
    excerpt = models.TextField(max_length=500, blank=True, help_text="文章摘要")
    
    # 关系字段
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="作者"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        help_text="分类"
    )
    
    # 状态字段
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="文章状态"
    )
    
    # 统计字段
    view_count = models.PositiveIntegerField(default=0, help_text="浏览次数")
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    published_at = models.DateTimeField(null=True, blank=True, help_text="发布时间")
    
    class Meta:
        db_table = 'blog_post'
        ordering = ['-created_at']


class Comment(models.Model):
    """文章评论"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="所属文章"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="评论者"
    )
    
    content = models.TextField(help_text="评论内容")
    is_approved = models.BooleanField(default=True, help_text="是否已审核")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    
    class Meta:
        db_table = 'blog_comment'
        ordering = ['-created_at']
