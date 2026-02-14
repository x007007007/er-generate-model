"""Model definition for POST."""
from django.db import models
from .post_manager import POSTManager

class POST(models.Model):
    """Post entity - blog posts written by users"""
    id = models.UUIDField(primary_key=True, help_text="Primary key")
    author = models.ForeignKey(
        'USER',
        on_delete=models.CASCADE,
        related_name='post_set',
        help_text="Foreign key to User"
    )
    title = models.CharField(max_length=255, help_text="Post title")
    content = models.TextField(help_text="Post content")
    created_at = models.DateField(help_text="Post creation timestamp")
    
    objects = POSTManager()
    
    class Meta:
        app_label = 'input'
        db_table = 'input_post'
        verbose_name = "Post entity - blog posts written by users"
        verbose_name_plural = "Post entity - blog posts written by users"
    
    def __str__(self):
        return f"POST(id={self.pk})"