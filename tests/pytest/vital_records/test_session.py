from uuid import uuid4

import pytest

from cdt_identity.claims import ClaimsResult
from cdt_identity.models import ClaimsVerificationRequest, IdentityGatewayConfig

from web.vital_records.session import Session, _userflow
from web.core.models import UserFlow
from web.vital_records.models import VitalRecordsRequest


@pytest.mark.django_db
class TestSession:

    @pytest.fixture
    def uuid(self):
        return uuid4()

    @pytest.fixture
    def mock_userflow(self, uuid):
        flow = UserFlow(id=uuid, system_name="vital-records")
        claims_request = ClaimsVerificationRequest(id=uuid)
        claims_request.save()
        flow.claims_request = claims_request
        oauth_config = IdentityGatewayConfig(id=uuid, client_id=uuid)
        oauth_config.save()
        flow.oauth_config = oauth_config
        flow.save()
        return flow

    @pytest.fixture
    def mock_vital_records_request(self, uuid):
        req = VitalRecordsRequest(id=uuid)
        req.save()
        return req

    def test_userflow(self, mocker):
        mock_flow = mocker.patch("web.vital_records.session.UserFlow")
        mock_flow.objects.filter.return_value.first.return_value = "flow"

        assert _userflow() == "flow"

    def test_session_init(self, app_request, mocker, mock_userflow):
        mock_uf = mocker.patch("web.vital_records.session._userflow")
        mock_uf.return_value = mock_userflow
        session = Session(app_request)

        assert session.request == app_request

    def test_vital_records_request_getter(self, app_request, uuid, mocker):
        session = Session(app_request)
        session.session = {"_reqid": uuid}

        mock_vr = mocker.patch("web.vital_records.session.VitalRecordsRequest")
        mock_vr.objects.filter.return_value.first.return_value = "test_request"

        assert session.vital_records_request == "test_request"

    def test_vital_records_request_setter(self, app_request, uuid, mock_vital_records_request):
        session = Session(app_request)
        session.session = {}

        session.vital_records_request = mock_vital_records_request
        assert session.session["_reqid"] == str(uuid)

        session.vital_records_request = None
        assert session.session["_reqid"] is None

    def test_verified_email(self, app_request):
        session = Session(app_request)

        # Test when email is verified
        session.claims_result = ClaimsResult({"email_verified": True, "email": "test@example.com"})
        assert session.verified_email == "test@example.com"

        # Test when email is not verified
        session.claims_result = ClaimsResult()
        assert session.verified_email == ""
