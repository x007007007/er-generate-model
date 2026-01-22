from django.db import models


# Custom QuerySet for ConversationSessionModel
class ConversationSessionModelQuerySet(models.QuerySet):
    """Custom QuerySet for ConversationSessionModel."""
    pass


# Custom Manager for ConversationSessionModel
class ConversationSessionModelManager(models.Manager):
    """Custom Manager for ConversationSessionModel."""
    
    def get_queryset(self):
        return ConversationSessionModelQuerySet(self.model, using=self._db)

class ConversationSessionModel(models.Model):
    session_uuid = models.UUIDField(primary_key=True)
    user_id = models.UUIDField()
    title = models.CharField(max_length=255)
    is_active = models.BooleanField()
    
    objects = ConversationSessionModelManager()
    
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_conversationsessionmodel'
    
    def __str__(self):
        return f"ConversationSessionModel(id={self.pk})"