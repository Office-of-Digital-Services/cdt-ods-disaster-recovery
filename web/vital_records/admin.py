from django.contrib import admin

from web.vital_records import models


@admin.register(models.VitalRecordsRequestMetadata)
class VitalRecordsRequestMetadataAdmin(admin.ModelAdmin):
    date_hierarchy = "submitted_at"
    list_display = (
        "id",
        "request_id",
        "type",
        "fire",
        "number_of_records",
        "submitted_at",
        "enqueued_at",
        "packaged_at",
        "sent_at",
    )
