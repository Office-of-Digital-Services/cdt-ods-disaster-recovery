import importlib
from uuid import uuid4

from django.db import models

from web.oauth.models.config import ClientConfig


class UserFlow(models.Model):
    """Represents a user journey through the DDRC app."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    label = models.CharField(
        help_text="A human readable label, used as the display text (user-facing)",
        max_length=50,
    )
    system_name = models.SlugField(
        help_text="Internal system name for this flow, mapped to the root URL.",
        unique=True,
    )
    urlconf_path = models.CharField(
        help_text="Django app path to the URLconf for this flow.",
        max_length=100,
    )
    oauth_config = models.ForeignKey(
        ClientConfig,
        on_delete=models.PROTECT,
        help_text="The IdG connection details for this flow.",
    )
    scopes = models.CharField(
        help_text="A space-separated list of identifiers used to specify what information is being requested",
        max_length=200,
    )
    eligibility_claim = models.CharField(
        help_text="The claim that is used to verify eligibility",
        max_length=50,
    )
    extra_claims = models.CharField(
        blank=True,
        default="",
        help_text="A space-separated list of any additional claims",
        max_length=200,
    )
    redirect_failure = models.CharField(
        default="oauth:error",
        help_text="A Django route in the form of app:endpoint to redirect to after a successful claims check",
        max_length=50,
    )
    redirect_success = models.CharField(
        default="oauth:success",
        help_text="A Django route in the form of app:endpoint to redirect to after a successful claims check",
        max_length=50,
    )
    scheme_override = models.CharField(
        blank=True,
        default="",
        help_text="(Optional) the authentication scheme to use. Defaults to that provided by the OAuth config.",
        max_length=50,
        verbose_name="Claims scheme",
    )

    @property
    def all_claims(self):
        return " ".join((self.eligibility_claim, self.extra_claims))

    @property
    def index_url(self):
        try:
            match = [url for url in self.urlpatterns if url.pattern.regex.match("")]
            index = match[0]
            return f"{self.urlconf.app_name}:{index.name}"
        except Exception:
            return None

    @property
    def urlconf(self):
        try:
            return importlib.import_module(self.urlconf_path)
        except Exception:
            return None

    @property
    def urlpatterns(self):
        try:
            return self.urlconf.urlpatterns
        except Exception:
            return []
