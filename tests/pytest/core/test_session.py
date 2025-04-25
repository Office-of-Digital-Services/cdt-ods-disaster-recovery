from uuid import uuid4

from cdt_identity.claims import ClaimsResult
from cdt_identity.models import ClaimsVerificationRequest
import pytest
from web.core.session import Session


@pytest.fixture
def session_instance(app_request, mocker):
    def _instance(has_verified_claims=True):
        session = Session(app_request)
        session.has_verified_claims = mocker.Mock(return_value=has_verified_claims)
        return session

    return _instance


@pytest.mark.django_db
def test_has_verified_eligibility_all_conditions_true(session_instance, mocker):
    session = session_instance()

    claims_request = ClaimsVerificationRequest(id=uuid4(), eligibility_claim="test_claim")
    claims_request.save()

    session.claims_request = claims_request
    session.claims_result = ClaimsResult({"test_claim": True})

    assert session.has_verified_eligibility() is True


def test_has_verified_eligibility_missing_verified_claims(session_instance):
    session = session_instance(False)

    assert session.has_verified_eligibility() is False


def test_has_verified_eligibility_missing_claims_request(session_instance, mocker):
    session = session_instance()

    mock_userflow = mocker.Mock()
    mock_userflow.claims_request = None
    session.userflow = mock_userflow

    assert session.has_verified_eligibility() is False


def test_has_verified_eligibility_missing_eligibility_claim(session_instance, mocker):
    session = session_instance()

    mock_userflow = mocker.Mock()
    mock_claims_request = mocker.Mock()
    mock_claims_request.eligibility_claim = None
    mock_userflow.claims_request = mock_claims_request
    session.userflow = mock_userflow

    assert session.has_verified_eligibility() is False


def test_has_verified_eligibility_claim_not_in_result(session_instance, mocker):
    session = session_instance()

    mock_userflow = mocker.Mock()
    mock_claims_request = mocker.Mock()
    mock_claims_request.eligibility_claim = "test_claim"
    mock_userflow.claims_request = mock_claims_request
    session.userflow = mock_userflow
    session.claims_result = ClaimsResult()

    assert session.has_verified_eligibility() is False
