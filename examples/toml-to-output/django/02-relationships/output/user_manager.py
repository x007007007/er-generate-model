"""Manager for USER model."""
from django.db import models
from .user_queryset import USERQuerySet


class USERManager(models.Manager):
    """Custom Manager for USER."""
    
    def get_queryset(self):
        return USERQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()