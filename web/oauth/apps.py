"""
The oauth application: Implements OpenID Connect.

https://www.microsoft.com/en-us/security/business/security-101/what-is-openid-connect-oidc
"""

from django.apps import AppConfig


class OAuthAppConfig(AppConfig):
    name = "web.oauth"
    label = "oauth"
    verbose_name = "OpenID Connect"
