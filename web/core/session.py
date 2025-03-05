from django.http import HttpRequest

from web.core.models import UserFlow
from cdt_identity.session import Session as OAuthSession


class Session(OAuthSession):

    _keys_userflow = "userflow"

    def __init__(self, request: HttpRequest, reset: bool = False, userflow: UserFlow = None):
        if userflow:
            super().__init__(
                request=request,
                reset=reset,
                client_config=userflow.oauth_config,
                claims_request=userflow.claims_request,
            )
            self.userflow = userflow
        else:
            super().__init__(request=request, reset=reset)

    @property
    def userflow(self) -> UserFlow:
        val = self.session.get(self._keys_userflow)
        return UserFlow.objects.filter(pk=val).first()

    @userflow.setter
    def userflow(self, value: UserFlow) -> None:
        if value:
            self.session[self._keys_userflow] = str(value.pk)
        else:
            self.session[self._keys_userflow] = None
