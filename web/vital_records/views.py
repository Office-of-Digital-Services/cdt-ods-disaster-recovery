from django.http import HttpRequest
from django.template.response import TemplateResponse

from web.vital_records.session import Session


def index(request: HttpRequest):
    Session(request, reset=True)
    return TemplateResponse(request, "vital_records/index.html")


def request(request: HttpRequest):
    return TemplateResponse(request, "vital_records/request.html")


def submitted(request: HttpRequest):
    return TemplateResponse(request, "vital_records/submitted.html")


def unverified(request: HttpRequest):
    return TemplateResponse(request, "vital_records/unverified.html")
