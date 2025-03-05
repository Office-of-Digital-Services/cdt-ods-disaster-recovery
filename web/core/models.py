import importlib
from uuid import uuid4

from django.db import models

from cdt_identity.models import IdentityGatewayConfig, ClaimsVerificationRequest


class UserFlow(models.Model):
    """Represents a user journey through the Disaster Recovery app."""

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
        IdentityGatewayConfig,
        on_delete=models.PROTECT,
        help_text="The IdG connection details for this flow.",
    )
    claims_request = models.ForeignKey(
        ClaimsVerificationRequest,
        on_delete=models.PROTECT,
        help_text="The claims request details for this flow.",
    )

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
