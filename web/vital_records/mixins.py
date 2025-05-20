from django.http import HttpResponseForbidden

from web.vital_records.session import Session


class ValidateRequestIdMixin:
    def dispatch(self, request, *args, **kwargs):
        session = Session(request)
        request_id = self.kwargs.get("pk")

        if session.request_id == request_id:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
