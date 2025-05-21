from uuid import UUID
from web.core.models import UserFlow
from web.core.session import Session as CoreSession


def _userflow() -> UserFlow | None:
    return UserFlow.objects.filter(system_name="vital-records").first()


class Session(CoreSession):
    _keys_request_id = "vitalrecords-requestid"

    def __init__(self, request, request_id=None, reset=False):
        super().__init__(request=request, reset=reset, userflow=_userflow())

        if request_id:
            self.request_id = request_id
        if reset:
            self.request_id = None

    @property
    def request_id(self):
        value = self.session.get(self._keys_request_id)
        return UUID(value) if value else None

    @request_id.setter
    def request_id(self, value):
        self.session[self._keys_request_id] = str(value) if value else None

    @property
    def verified_email(self):
        claims_result = self.claims_result
        if "email_verified" in claims_result:
            return claims_result.get("email", "")
        return ""
