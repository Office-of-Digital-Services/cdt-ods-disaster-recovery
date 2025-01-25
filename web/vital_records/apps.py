"""
Request vital records.
"""

from django.apps import AppConfig


class VitalsAppConfig(AppConfig):
    name = "web.vital_records"
    label = "vital_records"
    verbose_name = "Vital Records"
