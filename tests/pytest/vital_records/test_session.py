import pytest

from web.vital_records.session import Session


@pytest.mark.django_db
class TestSession:
    def test_init(self, app_request, request_id):
        session = Session(app_request, request_id=request_id)
        assert session.request_id == request_id

        session = Session(app_request, reset=True)
        assert session.request_id is None

        session = Session(app_request, request_id=request_id, reset=True)
        assert session.request_id is None

    def test_request_id(self, app_request, request_id):
        session = Session(app_request)
        assert session.request_id is None
        assert session._keys_request_id not in session.session

        session.request_id = request_id
        assert session.request_id == request_id
        assert session._keys_request_id in session.session
