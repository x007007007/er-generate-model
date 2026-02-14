"""Model definition for USER."""
from django.db import models
from .user_manager import USERManager

class USER(models.Model):
    """User entity with basic fields"""
    id = models.IntegerField(primary_key=True, help_text="Primary key")
    username = models.CharField(max_length=255, unique=True, help_text="Unique username")
    email = models.CharField(max_length=255, help_text="User email address")
    created_at = models.DateField(help_text="Account creation timestamp")
    
    objects = USERManager()
    
    class Meta:
        app_label = 'input'
        db_table = 'input_user'
        verbose_name = "User entity with basic fields"
        verbose_name_plural = "User entity with basic fields"
    
    def __str__(self):
        return f"USER(id={self.pk})"