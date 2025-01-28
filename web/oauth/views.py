import logging

from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from . import redirects
from . import claims
from .client import create_client, oauth
from .routes import Routes
from .session import Session

logger = logging.getLogger(__name__)


def _client_or_error_redirect(request: HttpRequest):
    """Calls `web.oauth.client.create_client()`.

    If a client is created successfully, return it; Otherwise, return a redirect response to OAuth system error.
    """
    oauth_client = None
    session = Session(request)

    oauth_config = session.oauth_config
    if not oauth_config:
        raise Exception("No oauth_config in session")

    scopes = session.oauth_scopes
    oauth_client = create_client(oauth, oauth_config, scopes=scopes)
    if not oauth_client:
        raise Exception(f"oauth_client not registered: {oauth_config.client_name}")

    return oauth_client


def authorize(request: HttpRequest):
    """View implementing OIDC token authorization."""
    logger.debug(Routes.AUTHORIZE)

    session = Session(request)
    oauth_client_result = _client_or_error_redirect(request)

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
    session.oauth_token = token["id_token"]
    # We store the returned claims in case they can be used later.
    expected_claims = session.oauth_claims_check.split(" ")
    stored_claims = []
    error_claims = {}

    if expected_claims:
        userinfo = token.get("userinfo", {})
        stored_claims, error_claims = claims.process(userinfo, expected_claims)
    # if we found the eligibility claim
    if session.oauth_claims_eligibility and session.oauth_claims_eligibility in stored_claims:
        # store them and redirect to success
        session.oauth_claims_verified = " ".join(stored_claims)
        return redirect(session.oauth_redirect_success)
    # else redirect to failure
    if error_claims:
        logger.error(error_claims)
    return redirect(session.oauth_redirect_failure)


def login(request: HttpRequest):
    """View implementing OIDC authorize_redirect."""
    logger.debug(Routes.LOGIN)

    oauth_client_result = _client_or_error_redirect(request)

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


def logout(request: HttpRequest):
    """View handler for OIDC sign out."""
    logger.debug(Routes.LOGOUT)

    session = Session(request)
    oauth_client_result = _client_or_error_redirect(request)

    if hasattr(oauth_client_result, "load_server_metadata"):
        # this looks like an oauth_client since it has the method we need
        # (called in redirects.deauthorize_redirect)
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    # overwrite the oauth session token, the user is signed out of the app
    token = session.oauth_token
    session.logout()

    route = reverse(Routes.POST_LOGOUT)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return redirects.deauthorize_redirect(request, oauth_client, token, redirect_uri)
