from django.db import models


# Custom QuerySet for User
class UserQuerySet(models.QuerySet):
    """Custom QuerySet for User."""
    pass


# Custom Manager for User
class UserManager(models.Manager):
    """Custom Manager for User."""
    
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    
    objects = UserManager()
    
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_user'
    
    def __str__(self):
        return f"User(id={self.pk})"