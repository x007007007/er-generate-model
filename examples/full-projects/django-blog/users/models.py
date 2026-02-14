"""
User management models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """扩展的用户模型"""
    email = models.EmailField(unique=True, help_text="邮箱地址")
    phone = models.CharField(max_length=20, blank=True, help_text="手机号码")
    avatar = models.URLField(blank=True, help_text="头像URL")
    bio = models.TextField(max_length=500, blank=True, help_text="个人简介")
    birth_date = models.DateField(null=True, blank=True, help_text="出生日期")
    
    # 地址信息
    country = models.CharField(max_length=100, blank=True, help_text="国家")
    city = models.CharField(max_length=100, blank=True, help_text="城市")
    
    # 账户状态
    is_verified = models.BooleanField(default=False, help_text="是否已验证")
    created_at = models.DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")
    
    # 解决与 Django 内置 User 的冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_users',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_users',
        related_query_name='custom_user',
    )
    
    class Meta:
        db_table = 'users_customuser'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class UserProfile(models.Model):
    """用户资料扩展"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="关联用户"
    )
    
    # 社交媒体
    github_username = models.CharField(max_length=100, blank=True, help_text="GitHub用户名")
    twitter_username = models.CharField(max_length=100, blank=True, help_text="Twitter用户名")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn链接")
    website_url = models.URLField(blank=True, help_text="个人网站")
    
    # 偏好设置
    language = models.CharField(max_length=10, default='zh-cn', help_text="语言偏好")
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', help_text="时区")
    theme = models.CharField(
        max_length=20,
        choices=[('light', '浅色'), ('dark', '深色'), ('auto', '自动')],
        default='auto',
        help_text="主题偏好"
    )
    
    # 通知设置
    email_notifications = models.BooleanField(default=True, help_text="邮件通知")
    push_notifications = models.BooleanField(default=True, help_text="推送通知")
    
    class Meta:
        db_table = 'users_userprofile'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'


class UserFollowing(models.Model):
    """用户关注关系"""
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        help_text="关注者"
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
        help_text="被关注者"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="关注时间")
    
    class Meta:
        db_table = 'users_userfollowing'
        verbose_name = '用户关注'
        verbose_name_plural = '用户关注'
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'created_at']),
            models.Index(fields=['following', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'