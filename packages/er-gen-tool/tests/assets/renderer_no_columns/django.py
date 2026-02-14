from django.db import models

# Custom QuerySet for EMPTY
class EMPTYQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for EMPTY
class EMPTYManager(models.Manager):
    def get_queryset(self):
        return EMPTYQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class EMPTY(models.Model):
    objects = EMPTYManager()
    class Meta:
        app_label = 'app'
        db_table = 'empty'