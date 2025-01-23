"""
The core application: Base templates and reusable models and components.
"""

from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    name = "web.core"
    label = "core"
    verbose_name = "Core"
