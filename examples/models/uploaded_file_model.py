from django.db import models


# Custom QuerySet for UploadedFileModel
class UploadedFileModelQuerySet(models.QuerySet):
    """Custom QuerySet for UploadedFileModel."""
    pass


# Custom Manager for UploadedFileModel
class UploadedFileModelManager(models.Manager):
    """Custom Manager for UploadedFileModel."""
    
    def get_queryset(self):
        return UploadedFileModelQuerySet(self.model, using=self._db)

class UploadedFileModel(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(
        'UploadedFileModel',
        on_delete=models.CASCADE,
        related_name='uploadedfilemodel_set',
        help_text="用户(必须)"
    )
    session_id = models.UUIDField(help_text="会话(可选)")
    parent_file_id = models.UUIDField(help_text="父文件(层级关系)")
    file_type_id = models.UUIDField(help_text="文件类型")
    file = models.FileField(help_text="文件存储(S3)")
    filename = models.CharField(max_length=255, help_text="文件名")
    file_size = models.IntegerField(help_text="文件大小")
    detected_mime_type = models.CharField(max_length=255, help_text="检测到的MIME类型")
    detected_charset = models.CharField(max_length=255, help_text="检测到的字符集(文本)")
    created_at = models.DateField()
    updated_at = models.DateField()
    
    objects = UploadedFileModelManager()
    
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_uploadedfilemodel'
    
    def __str__(self):
        return f"UploadedFileModel(id={self.pk})"