from django.http import HttpRequest

_OAUTH_CLAIMS = "oauth_claims"
_OAUTH_TOKEN = "oauth_token"


def logged_in(request: HttpRequest):
    """Check if the current session has an OAuth token."""
    return bool(oauth_token(request))


def logout(request: HttpRequest):
    """Reset the session claims and tokens."""
    oauth_claims(request, [])
    oauth_token(request, "")


def oauth_claims(request: HttpRequest, new_value: list[str] = None) -> str | None:
    """Get the oauth claims from the request's session. Optionally update the value first."""
    if new_value is not None:
        request.session[_OAUTH_CLAIMS] = new_value
    return request.session.get(_OAUTH_CLAIMS)


def oauth_token(request: HttpRequest, new_value: str = None) -> str | None:
    """Get the oauth token from the request's session. Optionally update the value first."""
    if new_value is not None:
        request.session[_OAUTH_TOKEN] = new_value
    return request.session.get(_OAUTH_TOKEN)
