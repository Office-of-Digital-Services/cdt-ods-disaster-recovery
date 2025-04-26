import os

from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.urls import path
from django.views.generic import TemplateView

app_name = "core"


def test_email(request):
    email = EmailMessage(
        subject="Vital records request",
        body="A new request is attached.",
        from_email=os.environ.get("EMAIL_FROM", "noreply@example.com"),
        to=[os.environ.get("EMAIL_TO", "to@example.com")],
        cc=[os.environ.get("EMAIL_CC", "cc@example.com")],
    )
    result = email.send()
    return JsonResponse({"result": result})


# /
urlpatterns = [
    path("", TemplateView.as_view(template_name="core/index.html"), name="index"),
    path("test/email", test_email, name="test_email"),
    path("logout/complete", TemplateView.as_view(template_name="core/post_logout.html"), name="post_logout"),
]
