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
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    objects = USERManager()
    class Meta:
        app_label = 'input'
        db_table = 'input_user'