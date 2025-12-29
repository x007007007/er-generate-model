from django.db import models

# Custom QuerySet for USER
class USERQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for USER
class USERManager(models.Manager):
    def get_queryset(self):
        return USERQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class USER(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Primary key for user")
    username = models.CharField(max_length=255, help_text="Unique username")
    password = models.CharField(max_length=255, help_text="Encrypted password")
    email = models.CharField(max_length=255, help_text="User email address")
    last_login = models.DateField(help_text="Last login timestamp")
    is_active = models.BooleanField(help_text="Whether user is active")
    objects = USERManager()
    class Meta:
        app_label = 'complex'
        db_table = 'complex_user'

# Custom QuerySet for PROFILE
class PROFILEQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for PROFILE
class PROFILEManager(models.Manager):
    def get_queryset(self):
        return PROFILEQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class PROFILE(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Profile primary key")
    user = models.OneToOneField('USER', on_delete=models.CASCADE, related_name='profile_rel', help_text="Foreign key to USER")
    bio = models.CharField(max_length=255, help_text="User biography")
    avatar_url = models.CharField(max_length=255, help_text="Avatar image URL")
    objects = PROFILEManager()
    class Meta:
        app_label = 'complex'
        db_table = 'complex_profile'

# Custom QuerySet for POST
class POSTQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for POST
class POSTManager(models.Manager):
    def get_queryset(self):
        return POSTQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class POST(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Post primary key")
    author = models.ForeignKey('USER', on_delete=models.CASCADE, related_name='post_set', help_text="Foreign key to USER (author)")
    title = models.CharField(max_length=255, help_text="Post title")
    content = models.CharField(max_length=255, help_text="Post content")
    created_at = models.DateField(help_text="Post creation time")
    status = models.CharField(max_length=255, help_text="enum:draft,published,archived - Post status")
    tag_set = models.ManyToManyField('TAG', related_name='post_set')
    objects = POSTManager()
    class Meta:
        app_label = 'complex'
        db_table = 'complex_post'

# Custom QuerySet for TAG
class TAGQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for TAG
class TAGManager(models.Manager):
    def get_queryset(self):
        return TAGQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class TAG(models.Model):
    id = models.IntegerField(primary_key=True, help_text="Tag primary key")
    name = models.CharField(max_length=255, help_text="Tag name")
    objects = TAGManager()
    class Meta:
        app_label = 'complex'
        db_table = 'complex_tag'

# Custom QuerySet for POST_TAGS
class POST_TAGSQuerySet(models.QuerySet):
    # TODO: Add custom queryset methods here
    # Example:
    # def active(self):
    #     return self.filter(is_active=True)
    pass

# Custom Manager for POST_TAGS
class POST_TAGSManager(models.Manager):
    def get_queryset(self):
        return POST_TAGSQuerySet(self.model, using=self._db)
    
    # TODO: Add custom manager methods here
    # Example:
    # def active(self):
    #     return self.get_queryset().active()
    pass

class POST_TAGS(models.Model):
    post_id = models.IntegerField(help_text="Foreign key to POST")
    tag_id = models.IntegerField(help_text="Foreign key to TAG")
    objects = POST_TAGSManager()
    class Meta:
        app_label = 'complex'
        db_table = 'complex_post_tags'