from django.db import models

class USER(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    class Meta:
        app_label = 'input'
        db_table = 'input_user'