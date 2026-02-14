"""Manager for POST model."""
from django.db import models
from .post_queryset import POSTQuerySet


class POSTManager(models.Manager):
    """Custom Manager for POST."""
    
    def get_queryset(self):
        return POSTQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()