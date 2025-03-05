from web.core.models import UserFlow
from web.core.session import Session as CoreSession


def _userflow() -> UserFlow | None:
    return UserFlow.objects.filter(system_name="vital-records").first()


class Session(CoreSession):
    def __init__(self, request, reset=False):
        super().__init__(request=request, reset=reset, userflow=_userflow())

    @property
    def verified_email(self):
        claims_result = self.claims_result
        if "email_verified" in claims_result:
            return claims_result.get("email", "")
        return ""
