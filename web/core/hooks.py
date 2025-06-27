from django.shortcuts import redirect

from cdt_identity.hooks import DefaultHooks


class DisasterRecoveryHooks(DefaultHooks):
    @classmethod
    def post_logout(cls, request):
        super().post_logout(request)
        return redirect("https://www.ca.gov/lafires/")

    @classmethod
    def system_error(cls, request, exception, operation):
        super().system_error(request, exception, operation)
        raise exception
