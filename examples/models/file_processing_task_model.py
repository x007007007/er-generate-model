from django.db import models


# Custom QuerySet for FileProcessingTaskModel
class FileProcessingTaskModelQuerySet(models.QuerySet):
    """Custom QuerySet for FileProcessingTaskModel."""
    pass


# Custom Manager for FileProcessingTaskModel
class FileProcessingTaskModelManager(models.Manager):
    """Custom Manager for FileProcessingTaskModel."""
    
    def get_queryset(self):
        return FileProcessingTaskModelQuerySet(self.model, using=self._db)

class FileProcessingTaskModel(models.Model):
    id = models.UUIDField(primary_key=True)
    uploaded_file = models.OneToOneField(
        'UploadedFileModel',
        on_delete=models.CASCADE,
        related_name='fileprocessingtaskmodel_rel',
        help_text="上传文件(一对一)"
    )
    status = models.CharField(max_length=255, help_text="处理状态: pending/processing/completed/failed/cancelled")
    progress = models.IntegerField(help_text="处理进度(0-100)")
    started_at = models.DateField(help_text="开始时间")
    completed_at = models.DateField(help_text="完成时间")
    error_message = models.TextField(help_text="错误信息")
    processing_config = models.JSONField(help_text="处理配置")
    created_at = models.DateField()
    updated_at = models.DateField()
    
    objects = FileProcessingTaskModelManager()
    
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_fileprocessingtaskmodel'
    
    def __str__(self):
        return f"FileProcessingTaskModel(id={self.pk})"