from django.apps import AppConfig


class AsistenciaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asistencia_app'

    def ready(self):
        import asistencia_app.signals
