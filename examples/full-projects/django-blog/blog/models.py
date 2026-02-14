"""
Blog models for demonstration
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
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """文章标签"""
    name = models.CharField(max_length=50, unique=True, help_text="标签名称")
    slug = models.SlugField(max_length=50, unique=True, help_text="URL别名")
    
    class Meta:
        db_table = 'blog_tag'
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']
    
    def __str__(self):
        return self.name


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
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='posts',
        help_text="标签"
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
    like_count = models.PositiveIntegerField(default=0, help_text="点赞次数")
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    published_at = models.DateTimeField(null=True, blank=True, help_text="发布时间")
    
    class Meta:
        db_table = 'blog_post'
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-published_at']),
        ]
    
    def __str__(self):
        return self.title


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
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="父评论（用于回复）"
    )
    
    content = models.TextField(help_text="评论内容")
    
    # 状态字段
    is_approved = models.BooleanField(default=True, help_text="是否已审核")
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    
    class Meta:
        db_table = 'blog_comment'
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.author.username} on {self.post.title}'


class UserProfile(models.Model):
    """用户资料（一对一关系示例）"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="关联用户"
    )
    bio = models.TextField(max_length=500, blank=True, help_text="个人简介")
    avatar = models.CharField(max_length=255, blank=True, help_text="头像URL")
    website = models.URLField(blank=True, help_text="个人网站")
    location = models.CharField(max_length=100, blank=True, help_text="所在地")
    
    # 社交媒体
    github = models.CharField(max_length=100, blank=True, help_text="GitHub用户名")
    twitter = models.CharField(max_length=100, blank=True, help_text="Twitter用户名")
    
    class Meta:
        db_table = 'blog_user_profile'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f'{self.user.username} Profile'
