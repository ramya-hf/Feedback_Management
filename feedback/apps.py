from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feedback'
    verbose_name = 'Feedback Management'

    def ready(self):
        """Import signals when the app is ready."""
        import feedback.signals
