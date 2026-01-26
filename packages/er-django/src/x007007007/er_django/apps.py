"""
Django AppConfig for ER Django integration
"""
from django.apps import AppConfig


class ErDjangoConfig(AppConfig):
    """
    Django app configuration for ER diagram integration.
    
    This app provides:
    - Django model to ER diagram conversion
    - ER-based migration generation
    - Management commands for ER operations
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'x007007007.er_django'
    verbose_name = 'ER Django Integration'
    
    def ready(self):
        """
        Called when Django starts.
        Register any signals or perform initialization here.
        """
        pass
