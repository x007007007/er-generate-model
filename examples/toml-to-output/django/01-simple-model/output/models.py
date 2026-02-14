from django.db import models

# Custom QuerySet for USER
class USERQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for USER
class USERManager(models.Manager):
    def get_queryset(self):
        return USERQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class USER(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Primary key")
    username = models.CharField(max_length=255, unique=True, help_text="Unique username")
    email = models.CharField(max_length=255, help_text="User email address")
    created_at = models.DateField(help_text="Account creation timestamp")
    objects = USERManager()
    class Meta:
        app_label = 'simple_model'
        db_table = 'user'
        verbose_name = "User entity with basic fields"
