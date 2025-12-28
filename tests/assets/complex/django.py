from django.db import models

class USER(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Primary key for user")
    username = models.CharField(max_length=255, help_text="Unique username")
    password = models.CharField(max_length=255, help_text="Encrypted password")
    email = models.CharField(max_length=255, help_text="User email address")
    last_login = models.DateField(help_text="Last login timestamp")
    is_active = models.BooleanField(help_text="Whether user is active")
    class Meta:
        app_label = 'complex'
        db_table = 'complex_user'

class PROFILE(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Profile primary key")
    user = models.OneToOneField('USER', on_delete=models.CASCADE, related_name='profile_rel', help_text="Foreign key to USER")
    bio = models.CharField(max_length=255, help_text="User biography")
    avatar_url = models.CharField(max_length=255, help_text="Avatar image URL")
    class Meta:
        app_label = 'complex'
        db_table = 'complex_profile'

class POST(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Post primary key")
    author = models.ForeignKey('USER', on_delete=models.CASCADE, related_name='post_set', help_text="Foreign key to USER (author)")
    title = models.CharField(max_length=255, help_text="Post title")
    content = models.CharField(max_length=255, help_text="Post content")
    created_at = models.DateField(help_text="Post creation time")
    status = models.CharField(max_length=255, help_text="enum:draft,published,archived - Post status")
    tag_set = models.ManyToManyField('TAG', related_name='post_set')
    class Meta:
        app_label = 'complex'
        db_table = 'complex_post'

class TAG(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Tag primary key")
    name = models.CharField(max_length=255, help_text="Tag name")
    class Meta:
        app_label = 'complex'
        db_table = 'complex_tag'

class POST_TAGS(models.Model):
    post_id = models.IntegerField(help_text="Foreign key to POST")
    tag_id = models.IntegerField(help_text="Foreign key to TAG")
    class Meta:
        app_label = 'complex'
        db_table = 'complex_post_tags'