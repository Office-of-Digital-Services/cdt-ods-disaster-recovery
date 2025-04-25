from django.shortcuts import redirect

from web.core.session import Session


class EligibilityMixin:
    """
    A mixin that checks if the current session has a verified eligibility claim.
    """

    def dispatch(self, request, *args, **kwargs):
        session = Session(request)

        if not session.has_verified_eligibility():
            return redirect("vital_records:login")

        return super().dispatch(request, *args, **kwargs)
