from django.db import models

# Custom QuerySet for User
class UserQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for User
class UserManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    objects = UserManager()
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_user'

# Custom QuerySet for ConversationSessionModel
class ConversationSessionModelQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for ConversationSessionModel
class ConversationSessionModelManager(models.Manager):
    def get_queryset(self):
        return ConversationSessionModelQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class ConversationSessionModel(models.Model):
    session_uuid = models.CharField(max_length=255, primary_key=True)
    user_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    is_active = models.BooleanField()
    objects = ConversationSessionModelManager()
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_conversationsessionmodel'

# Custom QuerySet for FileTypeModel
class FileTypeModelQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for FileTypeModel
class FileTypeModelManager(models.Manager):
    def get_queryset(self):
        return FileTypeModelQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class FileTypeModel(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    "文件类型名称"string = models.CharField(max_length=255)
    UK = models.CharField(max_length=255, help_text="MIME类型")
    created_at = models.DateField()
    updated_at = models.DateField()
    objects = FileTypeModelManager()
    class Meta:
        app_label = 'file_upload_models'
        db_table = 'file_upload_models_filetypemodel'

# Custom QuerySet for UploadedFileModel
class UploadedFileModelQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for UploadedFileModel
class UploadedFileModelManager(models.Manager):
    def get_queryset(self):
        return UploadedFileModelQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class UploadedFileModel(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey('UploadedFileModel', on_delete=models.CASCADE, related_name='uploadedfilemodel_set', help_text="用户(必须)")
    session_id = models.CharField(max_length=255, help_text="会话(可选)")
    parent_file_id = models.CharField(max_length=255, help_text="父文件(层级关系)")
    file_type_id = models.CharField(max_length=255, help_text="文件类型")
    file = models.CharField(max_length=255, help_text="文件存储(S3)")
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

# Custom QuerySet for FileProcessingTaskModel
class FileProcessingTaskModelQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for FileProcessingTaskModel
class FileProcessingTaskModelManager(models.Manager):
    def get_queryset(self):
        return FileProcessingTaskModelQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class FileProcessingTaskModel(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    uploaded_file = models.OneToOneField('UploadedFileModel', on_delete=models.CASCADE, related_name='fileprocessingtaskmodel_rel', help_text="上传文件(一对一)")
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

# Custom QuerySet for FileProcessingResultModel
class FileProcessingResultModelQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for FileProcessingResultModel
class FileProcessingResultModelManager(models.Manager):
    def get_queryset(self):
        return FileProcessingResultModelQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class FileProcessingResultModel(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    processing_task = models.ForeignKey('FileProcessingTaskModel', on_delete=models.CASCADE, related_name='fileprocessingresultmodel_set', help_text="处理任务")
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