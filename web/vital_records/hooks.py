from django.shortcuts import redirect

from web.core.hooks import DisasterRecoveryHooks
from web.vital_records.routes import Routes


class VitalRecordsHooks(DisasterRecoveryHooks):
    @classmethod
    def cancel_login(cls, request):
        super().cancel_login(request)
        return redirect(Routes.app_route(Routes.unverified))

    @classmethod
    def claims_verified_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_eligible(request, claims_request, claims_result)
        return redirect(Routes.app_route(Routes.request_start))

    @classmethod
    def claims_verified_not_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_not_eligible(request, claims_request, claims_result)
        return redirect(Routes.app_route(Routes.unverified))
