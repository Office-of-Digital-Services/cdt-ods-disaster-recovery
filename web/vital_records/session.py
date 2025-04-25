from web.core.models import UserFlow
from web.core.session import Session as CoreSession
from web.vital_records.models import VitalRecordsRequest


def _userflow() -> UserFlow | None:
    return UserFlow.objects.filter(system_name="vital-records").first()


class Session(CoreSession):
    _keys_reqid = "_reqid"

    def __init__(self, request, reset=False):
        super().__init__(request=request, reset=reset, userflow=_userflow())

    @property
    def vital_records_request(self) -> VitalRecordsRequest:
        val = self.session.get(self._keys_reqid)
        return VitalRecordsRequest.objects.filter(pk=val).first()

    @vital_records_request.setter
    def vital_records_request(self, value: VitalRecordsRequest) -> None:
        if value:
            self.session[self._keys_reqid] = str(value.pk)
        else:
            self.session[self._keys_reqid] = None

    @property
    def verified_email(self):
        claims_result = self.claims_result
        if "email_verified" in claims_result:
            return claims_result.get("email", "")
        return ""
