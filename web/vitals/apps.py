"""
The vitals application: Request vital records.
"""

from django.apps import AppConfig


class VitalsAppConfig(AppConfig):
    name = "web.vitals"
    label = "vitals"
    verbose_name = "Vital Records"
