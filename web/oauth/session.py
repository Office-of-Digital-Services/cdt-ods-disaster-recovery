import logging

from django.db import models
from django.http import HttpRequest

from .models import ClientConfig


logger = logging.getLogger(__name__)


class Session:

    props = {
        "oauth_claims_check": str,
        "oauth_claims_eligibility": str,
        "oauth_claims_verified": str,
        "oauth_config": ClientConfig,
        "oauth_redirect_failure": str,
        "oauth_redirect_success": str,
        "oauth_scopes": str,
        "oauth_token": str,
    }

    def __init__(self, request: HttpRequest, reset: bool = False):
        self.request = request
        self.session = request.session

        logger.debug(self.session.keys())

        for prop_name in self.props.keys():
            self._make_property(prop_name)

        if reset:
            self.oauth_claims_check = ""
            self.oauth_claims_eligibility = ""
            self.logout()

    def _make_property(self, prop_name):
        def _getter(s):
            if issubclass(self.props[prop_name], models.Model):
                val = s.session.get(prop_name)
                cls = self.props[prop_name]
                return cls.objects.filter(id=val).first()
            else:
                return s.session.get(prop_name)

        def _setter(s, value):
            if issubclass(self.props[prop_name], models.Model):
                s.session[prop_name] = str(getattr(value, "id"))
            else:
                s.session[prop_name] = value

        prop = property(fget=_getter, fset=_setter)
        setattr(self.__class__, prop_name, prop)

    @property
    def logged_in(self):
        """Check if the current session has an OAuth token."""
        return bool(self.oauth_token)

    def logout(self):
        """Reset the session claims and tokens."""
        self.oauth_claims_verified = ""
        self.oauth_token = ""
