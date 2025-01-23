import logging

from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from . import redirects, session
from .client import oauth, create_client
from .models import OAuthClientConfig
from .routes import Routes


logger = logging.getLogger(__name__)


def _oauth_client_config():
    return OAuthClientConfig.objects.first()


def _oauth_client_or_error_redirect(request: HttpRequest, config: OAuthClientConfig):
    """Calls `web.oauth.client.create_client()`.

    If a client is created successfully, return it; Otherwise, return a redirect response to OAuth system error.
    """
    oauth_client = None
    exception = None

    try:
        oauth_client = create_client(oauth, config)
    except Exception as ex:
        exception = ex

    if not oauth_client and not exception:
        exception = Exception(f"oauth_client not registered: {config.client_name}")

    if exception:
        raise exception

    return oauth_client


def authorize(request):
    """View implementing OIDC token authorization."""
    logger.debug(Routes.AUTHORIZE)

    oauth_client_config = _oauth_client_config()
    oauth_client_result = _oauth_client_or_error_redirect(request, oauth_client_config)

    if hasattr(oauth_client_result, "authorize_access_token"):
        # this looks like an oauth_client since it has the method we need
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    logger.debug("Attempting to authorize OIDC access token")
    token = None
    exception = None

    try:
        token = oauth_client.authorize_access_token(request)
    except Exception as ex:
        exception = ex

    if token is None:
        logger.warning("Could not authorize OIDC access token")
        exception = Exception("oauth_client.authorize_access_token returned None")

    if exception:
        raise exception

    logger.debug("OIDC access token authorized")

    # We store the id_token in the user's session. This is the minimal amount of information needed later to log the user out.
    id_token = token["id_token"]

    # We store the returned claim in case it can be used later.
    claims = []
    stored_claims = []

    error_claim = {}

    if claims:
        userinfo = token.get("userinfo")

        if userinfo:
            for claim in claims:
                claim_value = userinfo.get(claim)
                # the claim comes back in userinfo like { "claim": "1" | "0" }
                claim_value = int(claim_value) if claim_value else None
                if claim_value is None:
                    logger.warning(f"userinfo did not contain: {claim}")
                elif claim_value == 1:
                    # if userinfo contains our claim and the flag is 1 (true), store the *claim*
                    stored_claims.append(claim)
                elif claim_value >= 10:
                    error_claim[claim] = claim_value

    session.oauth_token(request, id_token)
    session.oauth_claims(request, stored_claims)

    return redirect(Routes.SUCCESS)


def login(request):
    """View implementing OIDC authorize_redirect."""
    logger.debug(Routes.LOGIN)

    oauth_client_config = _oauth_client_config()
    oauth_client_result = _oauth_client_or_error_redirect(request, oauth_client_config)

    if hasattr(oauth_client_result, "authorize_redirect"):
        # this looks like an oauth_client since it has the method we need
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    route = reverse(Routes.AUTHORIZE)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth authorize_redirect with redirect_uri: {redirect_uri}")

    exception = None
    result = None

    try:
        result = oauth_client.authorize_redirect(request, redirect_uri)
    except Exception as ex:
        exception = ex

    if result and result.status_code >= 400:
        exception = Exception(f"authorize_redirect error response [{result.status_code}]: {result.content.decode()}")
    elif result is None and exception is None:
        exception = Exception("authorize_redirect returned None")

    if exception:
        raise exception

    return result


def logout(request):
    """View handler for OIDC sign out."""
    logger.debug(Routes.LOGOUT)

    oauth_client_config = _oauth_client_config()
    oauth_client_result = _oauth_client_or_error_redirect(request, oauth_client_config)

    if hasattr(oauth_client_result, "load_server_metadata"):
        # this looks like an oauth_client since it has the method we need
        # (called in redirects.deauthorize_redirect)
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    # overwrite the oauth session token, the user is signed out of the app
    token = session.oauth_token(request)
    session.logout(request)

    route = reverse(Routes.POST_LOGOUT)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return redirects.deauthorize_redirect(request, oauth_client, token, redirect_uri)
