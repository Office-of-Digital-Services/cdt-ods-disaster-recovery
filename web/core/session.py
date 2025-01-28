from django.http import HttpRequest

from web.core.models import UserFlow
from web.oauth.session import Session as OAuthSession


class Session(OAuthSession):

    def __init__(self, request: HttpRequest, reset: bool = False):
        self.props["userflow"] = UserFlow
        super().__init__(request, reset)
        if reset:
            self.session["userflow"] = None
