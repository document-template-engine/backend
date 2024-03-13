from django.apps import AppConfig


class BaseObjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_objects'
