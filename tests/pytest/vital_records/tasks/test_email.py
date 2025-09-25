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

    @pytest.mark.parametrize(
        "record_type, expected_output",
        [
            ("birth", "Birth"),
            ("marriage", "Marriage"),
            ("death", "Death"),
            ("invalid_type", None),
        ],
    )
    def test__format_record_type(self, task, record_type, expected_output):
        assert task._format_record_type(record_type) == expected_output

    def test__create_base_email(self, mocker, task):
        """Tests that the base email object is created correctly."""
        mock_EmailMultiAlternatives = mocker.patch("web.vital_records.tasks.email.EmailMultiAlternatives")
        mock_email_instance = mock_EmailMultiAlternatives.return_value

        subject = "Test Subject"
        to_address = ["test@example.com"]
        text_content = "This is the text content."
        html_content = "<p>This is the HTML content.</p>"

        result = task._create_base_email(subject, to_address, text_content, html_content)

        mock_EmailMultiAlternatives.assert_called_once_with(
            subject=subject,
            body=text_content,
            to=to_address,
        )
        mock_email_instance.attach_alternative.assert_called_once_with(html_content, "text/html")
        assert result == mock_email_instance

    @pytest.mark.parametrize(
        "request_type, request_type_formatted", [("birth", "Birth"), ("marriage", "Marriage"), ("death", "Death")]
    )
    def test_handler(
        self,
        settings,
        mocker,
        request_id,
        mock_VitalRecordsRequest,
        request_type,
        request_type_formatted,
        task,
    ):
        mock_inst = mocker.MagicMock(email_address="email@example.com", number_of_records=1, type=request_type)
        mock_VitalRecordsRequest.get_with_status.return_value = mock_inst
        mock_render = mocker.patch("web.vital_records.tasks.email.render_to_string", return_value="email body")
        mock_email_office = mocker.MagicMock()
        mock_email_requestor = mocker.MagicMock()
        mock__create_base_email = mocker.patch(
            "web.vital_records.tasks.email.EmailTask._create_base_email",
            side_effect=[
                mock_email_office,
                mock_email_requestor,
            ],
        )

        # Simulate a success
        mock_email_office.send.return_value = 1
        mock_email_requestor.send.return_value = 1

        mock__format_record_type = mocker.patch("web.vital_records.tasks.email.EmailTask._format_record_type")
        mock__format_record_type.return_value = request_type_formatted

        result = task.handler(request_id, "package")

        mock__format_record_type.assert_called_once()

        expected_ctx = {
            "number_of_copies": mock_VitalRecordsRequest.number_of_records,
            "email_address": mock_VitalRecordsRequest.email_address,
            "logo_url": "https://webstandards.ca.gov/wp-content/uploads/sites/8/2024/10/cagov-logo-coastal-flat.png",
            "request_type": request_type_formatted,
        }
        mock_render.assert_any_call(EMAIL_TXT_TEMPLATE, expected_ctx)
        mock_render.assert_any_call(EMAIL_HTML_TEMPLATE, expected_ctx)

        expected_subject = f"Completed: {request_type_formatted} Record Request"
        office_call = mocker.call(
            subject=expected_subject,
            to_address=[settings.VITAL_RECORDS_EMAIL_TO],
            text_content="email body",
            html_content="email body",
        )
        requestor_call = mocker.call(
            subject=expected_subject,
            to_address=[mock_inst.email_address],
            text_content="email body",
            html_content="email body",
        )
        mock__create_base_email.assert_has_calls([office_call, requestor_call])

        mock_email_office.attach_file.assert_called_once_with("package", "application/pdf")
        mock_email_office.send.assert_called_once()

        mock_email_requestor.attach_file.assert_not_called()
        mock_email_requestor.send.assert_called_once()

        mock_VitalRecordsRequest.complete_send.assert_called_once()
        mock_VitalRecordsRequest.finish.assert_called_once()
        mock_VitalRecordsRequest.save.assert_called_once()

        assert result == (1, 1)
