from django.shortcuts import redirect

from web.core.session import Session


class EligibilityMixin:
    """
    A mixin that checks if the current session has a verified eligibility claim.
    """

    redirect_url = "core:index"

    def dispatch(self, request, *args, **kwargs):
        session = Session(request)

        if not session.has_verified_eligibility():
            return redirect(self.redirect_url)

        return super().dispatch(request, *args, **kwargs)
