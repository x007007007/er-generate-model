from django.db import models


# Custom QuerySet for FileProcessingResultModel
class FileProcessingResultModelQuerySet(models.QuerySet):
    """Custom QuerySet for FileProcessingResultModel."""
    pass


# Custom Manager for FileProcessingResultModel
class FileProcessingResultModelManager(models.Manager):
    """Custom Manager for FileProcessingResultModel."""
    
    def get_queryset(self):
        return FileProcessingResultModelQuerySet(self.model, using=self._db)

class FileProcessingResultModel(models.Model):
    id = models.UUIDField(primary_key=True)
    processing_task = models.ForeignKey(
        'FileProcessingTaskModel',
        on_delete=models.CASCADE,
        related_name='fileprocessingresultmodel_set',
        help_text="处理任务"
    )
    result_type = models.CharField(max_length=255, help_text="结果类型: text/table/image/structured/mixed")
    content = models.JSONField(help_text="结果内容(JSON)")
    summary = models.TextField(help_text="内容摘要")
    is_indexed = models.BooleanField(help_text="是否已索引到知识库")
    index_info = models.JSONField(help_text="索引信息(向量ID/图节点ID等)")
    created_at = models.DateField()
    updated_at = models.DateField()
    
    objects = FileProcessingResultModelManager()
    
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_fileprocessingresultmodel'
    
    def __str__(self):
        return f"FileProcessingResultModel(id={self.pk})"