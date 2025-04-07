from django.contrib.sessions.middleware import SessionMiddleware

import pytest

from pytest_socket import disable_socket


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def app_request(rf):
    """
    Fixture creates and initializes a new Django request object similar to a real application request.
    """
    # create a request for the path, initialize
    app_request = rf.get("/some/arbitrary/path")

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x)]
    for m in middleware:
        m.process_request(app_request)

    app_request.session.save()

    return app_request
