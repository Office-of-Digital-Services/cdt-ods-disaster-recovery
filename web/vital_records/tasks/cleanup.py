import logging
from pathlib import Path

from django.utils import timezone

from web.core.tasks import Task
from web.vital_records.models import VitalRecordsRequest, VitalRecordsRequestMetadata
from web.vital_records.tasks.utils import get_package_filename

logger = logging.getLogger(__name__)


def run_cleanup_task():
    """Submit a cleanup task to the task queue for processing."""
    logger.debug("Creating cleanup task")
    # create a new task instance
    task = CleanupTask()
    # calling task.run() submits the task to the queue for processing
    task.run()
    # if callers want to interrogate the status, etc.
    return task


class CleanupTask(Task):
    """Clean up Vital Records requests in the `finished` state.

    Removes the original database record and file(s) generated as part of fulfilling the request.
    Creates a metadata record of type `CompletedVitalRecordsRequest` for each cleaned up record.
    """

    group = "vital-records"
    name = "cleanup"

    def clean_file(self, request: VitalRecordsRequest) -> bool:
        """Deletes the package file for this request."""
        # delete the package file
        success = True
        filename = get_package_filename(request)
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

    def clean_record(self, request: VitalRecordsRequest) -> bool:
        """Deletes the database record for this request."""
        # save the request.id for use later, after the record is deleted
        logger.debug(f"Deleting record: {request.id}")
        # delete the request record
        try:
            count, _ = request.delete()
        except ValueError:
            count = 0

        return count == 1

    def clean_request(self, request: VitalRecordsRequest) -> bool:
        """Deletes the database record and package file for this request."""
        # save the request.id for use later, after the record is deleted
        request_id = request.id
        logger.debug(f"Cleaning up request: {request_id}")

        success = self.clean_record(request)
        if success:
            success = self.clean_file(request)

        if success:
            logger.debug(f"Cleaning complete for: {request_id}")
        else:
            logger.warning(f"Cleaning failed for record: {request_id}")

        return success

    def create_metadata(self, request: VitalRecordsRequest):
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

    def handler(self, *args, **kwargs):
        logger.info("Running cleanup task")

        batch = VitalRecordsRequest.get_finished()
        batch_count = batch.count()
        cleaned_count = 0
        logger.debug(f"Found {batch_count} records to clean")

        for request in batch:
            # create a metadata record for this request
            self.create_metadata(request)
            # clean up the request
            if self.clean_request(request):
                cleaned_count += 1

        result = True
        if batch_count > 0:
            if batch_count == cleaned_count:
                logger.info("Cleanup task completed successfully")
            else:
                logger.warning(f"Some records were not cleaned ({batch_count - cleaned_count} of {batch_count} failed)")
                result = False

        return result
