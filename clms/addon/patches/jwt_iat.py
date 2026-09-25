"""Add an issued-at claim to every REST API JWT."""

from time import time

from plone.restapi.pas.plugin import JWTAuthenticationPlugin


_original_create_token = JWTAuthenticationPlugin.create_token


def create_token_with_iat(self, userid, timeout=None, data=None):
    """Create a JWT whose ``iat`` is controlled by the token issuer."""
    payload = dict(data or {})
    payload["iat"] = int(time())
    return _original_create_token(
        self,
        userid,
        timeout=timeout,
        data=payload,
    )


JWTAuthenticationPlugin.create_token = create_token_with_iat
