"""Manager for DATA_TYPE_SHOWCASE model."""
from django.db import models
from .data_type_showcase_queryset import DATA_TYPE_SHOWCASEQuerySet


class DATA_TYPE_SHOWCASEManager(models.Manager):
    """Custom Manager for DATA_TYPE_SHOWCASE."""
    
    def get_queryset(self):
        return DATA_TYPE_SHOWCASEQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()