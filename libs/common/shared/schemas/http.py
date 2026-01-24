from pydantic import HttpUrl, UrlConstraints


class HttpsUrl(HttpUrl):
    """A custom URL type for validating URLs with https scheme."""

    _constraints = UrlConstraints(allowed_schemes=["https"])
