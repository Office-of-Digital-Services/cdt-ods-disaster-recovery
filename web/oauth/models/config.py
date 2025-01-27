from uuid import uuid4

from django.db import models

from .secret_name_field import SecretNameField


class ClientConfig(models.Model):
    """OAuth Client configuration."""

    class Meta:
        verbose_name = "OAuth Client"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    client_name = models.SlugField(
        help_text="The name of this OAuth client",
        unique=True,
    )
    client_id_secret_name = SecretNameField(help_text="The name of the secret containing the client ID for this OAuth client")
    authority = models.CharField(
        help_text="The fully qualified HTTPS domain name for an OAuth authority server",
        max_length=50,
    )
    scheme = models.CharField(
        help_text="The authentication scheme for the authority server",
        max_length=50,
    )

    @property
    def client_id(self):
        secret_name_field = self._meta.get_field("client_id_secret_name")
        return secret_name_field.secret_value(self)

    def __str__(self):
        return self.client_name
