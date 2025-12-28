from django.db import models

class EMPTY(models.Model):
    class Meta:
        app_label = 'app'
        db_table = 'empty'