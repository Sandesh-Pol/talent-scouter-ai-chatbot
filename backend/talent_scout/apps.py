"""
TalentScout App Configuration
"""

from django.apps import AppConfig


class TalentScoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'talent_scout'
    verbose_name = 'TalentScout Hiring Assistant'
    
    def ready(self):
        """
        Perform initialization when app is ready.
        This is called once when Django starts.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info("TalentScout app initialized successfully")
