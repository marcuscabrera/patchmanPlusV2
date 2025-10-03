from django.apps import AppConfig


class IpamConfig(AppConfig):
    """Application configuration for the IP address management module."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ipam'
    verbose_name = 'IP Address Management'
