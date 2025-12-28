from django.db import models

class USER(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, help_text="User Name")
    email = models.CharField(max_length=255)
    class Meta:
        app_label = 'app'
        db_table = 'user'

class POST(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    user = models.ForeignKey('USER', on_delete=models.CASCADE, related_name='post_set')
    class Meta:
        app_label = 'app'
        db_table = 'post'