import logging
from pathlib import Path
from uuid import UUID

from django.utils import timezone

from web.vital_records.models import VitalRecordsRequest, VitalRecordsRequestMetadata
from web.vital_records.tasks.utils import get_package_filename

logger = logging.getLogger(__name__)


class CleanupScheduledTask:
    """Clean up Vital Records requests in the `finished` state.

    Removes the original database record and file(s) generated as part of fulfilling the request.
    Creates a metadata record of type `CompletedVitalRecordsRequest` for each cleaned up record.

    This is a scheduled task created and managed via the Django Admin.
    """

    @classmethod
    def clean_file(cls, request_id: UUID) -> bool:
        """Deletes the package file for this request."""
        # delete the package file
        success = True
        filename = get_package_filename(request_id)
        logger.debug(f"Deleting package file: {filename}")
        request_file = Path(filename)

        if request_file.exists():
            if request_file.is_file():
                request_file.unlink()
            else:
                success = False
                logger.warning(f"Package file wasn't a file (maybe dir?): {filename}")

            if request_file.exists():
                success = False
                logger.warning(f"Couldn't delete package file: {filename}")

        return success

    @classmethod
    def clean_record(cls, request: VitalRecordsRequest) -> bool:
        """Deletes the database record for this request."""
        # save the request.id for use later, after the record is deleted
        logger.debug(f"Deleting record: {request.id}")
        # delete the request record
        try:
            count, _ = request.delete()
        except ValueError:
            count = 0

        return count == 1

    @classmethod
    def clean_request(cls, request: VitalRecordsRequest) -> bool:
        """Deletes the database record and package file for this request."""
        # save the request.id for use later, after the record is deleted
        request_id = request.id
        logger.debug(f"Cleaning up request: {request_id}")

        success = cls.clean_record(request)
        if success:
            success = cls.clean_file(request_id)

        if success:
            logger.debug(f"Cleaning complete for: {request_id}")
        else:
            logger.warning(f"Cleaning failed for record: {request_id}")

        return success

    @classmethod
    def create_metadata(cls, request: VitalRecordsRequest):
        """Creates a VitalRecordsRequestMetadata record for this request."""
        logger.debug(f"Creating metadata record for: {request.id}")
        metadata = VitalRecordsRequestMetadata.objects.create(
            request_id=request.id,
            fire=request.fire,
            number_of_records=request.number_of_records,
            submitted_at=request.submitted_at,
            enqueued_at=request.enqueued_at,
            packaged_at=request.packaged_at,
            sent_at=request.sent_at,
            cleaned_at=timezone.now(),
        )
        metadata.save()
        logger.debug(f"Metadata created for: {request.id}")

    @classmethod
    def handler(cls):
        logger.info("Running cleanup task")

        batch = VitalRecordsRequest.objects.filter(status="finished")
        batch_count = batch.count()
        cleaned_count = 0
        logger.debug(f"Found {batch_count} records to clean")

        for request in batch:
            # create a metadata record for this request
            cls.create_metadata(request)
            # clean up the request
            if cls.clean_request(request):
                cleaned_count += 1

        result = True
        if batch_count > 0:
            if batch_count == cleaned_count:
                logger.info("Cleanup task completed successfully")
            else:
                logger.warning(f"Some records were not cleaned ({batch_count - cleaned_count} of {batch_count} failed)")
                result = False

        return result
