from web.core.models.userflow import UserFlow
from web.core.session import Session as CoreSession


def userflow() -> UserFlow | None:
    return UserFlow.objects.filter(system_name="vital-records").first()


class Session(CoreSession):
    def __init__(self, request, reset=False):
        super().__init__(request, reset)
        if reset:
            self.userflow = userflow()
            if self.userflow:
                self.oauth_config = self.userflow.oauth_config
                self.oauth_scopes = self.userflow.scopes
                self.oauth_claims_check = self.userflow.all_claims
                self.oauth_claims_eligibility = self.userflow.eligibility_claim
                self.oauth_redirect_failure = self.userflow.redirect_failure
                self.oauth_redirect_success = self.userflow.redirect_success

    @property
    def verified_email(self):
        claims = self.oauth_claims_verified.split(" ")
        if "email_verified" in claims:
            for claim in claims:
                if claim.startswith("email:"):
                    return claim.split(":")[1]
        return ""
