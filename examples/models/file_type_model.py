from django.db import models


# Custom QuerySet for FileTypeModel
class FileTypeModelQuerySet(models.QuerySet):
    """Custom QuerySet for FileTypeModel."""
    pass


# Custom Manager for FileTypeModel
class FileTypeModelManager(models.Manager):
    """Custom Manager for FileTypeModel."""
    
    def get_queryset(self):
        return FileTypeModelQuerySet(self.model, using=self._db)

class FileTypeModel(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    "文件类型名称"string = models.CharField(max_length=255)
    UK = models.CharField(max_length=255, help_text="MIME类型")
    created_at = models.DateField()
    updated_at = models.DateField()
    
    objects = FileTypeModelManager()
    
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_filetypemodel'
    
    def __str__(self):
        return f"FileTypeModel(id={self.pk})"