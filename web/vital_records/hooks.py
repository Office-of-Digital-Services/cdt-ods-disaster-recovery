from django.shortcuts import redirect

from web.core.hooks import DisasterRecoveryHooks


class VitalRecordsHooks(DisasterRecoveryHooks):
    @classmethod
    def cancel_login(cls, request):
        super().cancel_login(request)
        return redirect("vital_records:unverified")

    @classmethod
    def claims_verified_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_eligible(request, claims_request, claims_result)
        return redirect("vital_records:request_start")

    @classmethod
    def claims_verified_not_eligible(cls, request, claims_request, claims_result):
        super().claims_verified_not_eligible(request, claims_request, claims_result)
        return redirect("vital_records:unverified")
