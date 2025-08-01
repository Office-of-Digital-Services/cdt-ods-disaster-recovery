import pytest

from web.vital_records.tasks.email import EmailTask, EMAIL_HTML_TEMPLATE, EMAIL_TXT_TEMPLATE


@pytest.fixture
def mock_VitalRecordsRequest(mocker, mock_VitalRecordsRequest):
    mocker.patch("web.vital_records.tasks.email.VitalRecordsRequest", mock_VitalRecordsRequest)
    return mock_VitalRecordsRequest.get_with_status.return_value


class TestEmailTask:
    @pytest.fixture
    def task(self, request_id, mock_PackageTask) -> EmailTask:
        mock_package_task = mock_PackageTask.return_value
        mock_package_task.kwargs = {"request_id": request_id}
        return EmailTask(request_id, "package")

    def test_task(self, request_id, task):
        assert task.group == "vital-records"
        assert task.name == "email"
        assert task.kwargs["request_id"] == request_id
        assert task.kwargs["package"] == "package"
        assert task.started is False

    def test_handler(self, settings, mocker, request_id, mock_VitalRecordsRequest, task):
        mock_render = mocker.patch("web.vital_records.tasks.email.render_to_string", return_value="email body")
        mock_EmailMultiAlternatives = mocker.patch("web.vital_records.tasks.email.EmailMultiAlternatives")
        mock_email = mock_EmailMultiAlternatives.return_value
        mock_email.send.return_value = 0

        result = task.handler(request_id, "package")

        expected_ctx = {
            "number_of_copies": mock_VitalRecordsRequest.number_of_records,
            "email_address": mock_VitalRecordsRequest.email_address,
            "logo_url": "https://webstandards.ca.gov/wp-content/uploads/sites/8/2024/10/cagov-logo-coastal-flat.png",
        }
        mock_render.assert_any_call(EMAIL_TXT_TEMPLATE, expected_ctx)
        mock_render.assert_any_call(EMAIL_HTML_TEMPLATE, expected_ctx)

        mock_EmailMultiAlternatives.assert_called_once_with(
            subject="Completed: Birth Record Request",
            body=mock_render.return_value,
            to=[settings.VITAL_RECORDS_EMAIL_TO],
        )

        mock_email.attach_alternative.assert_called_once_with(mock_render.return_value, "text/html")
        mock_email.attach_file.assert_called_once_with("package", "application/pdf")
        mock_email.send.assert_called_once()

        mock_VitalRecordsRequest.complete_send.assert_called_once()
        mock_VitalRecordsRequest.finish.assert_called_once()
        mock_VitalRecordsRequest.save.assert_called_once()

        assert result == 0
