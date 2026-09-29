"""Add issuer-controlled claims to every REST API JWT."""

from time import time
from uuid import uuid4

from plone.restapi.pas.plugin import JWTAuthenticationPlugin

from clms.addon.session import ABSOLUTE_SESSION_TIMEOUT, AUTH_TIME_DATA_KEY
from clms.addon.subscribers.token_revocation import cleanup_expired_tokens

_original_create_token = JWTAuthenticationPlugin.create_token


def create_token_with_issuer_claims(self, userid, timeout=None, data=None):
    """Create a JWT whose standard claims are controlled by the issuer."""
    if self.store_tokens:
        cleanup_expired_tokens(self)

    payload = dict(data or {})
    issued_at = int(time())
    auth_time = payload.pop(AUTH_TIME_DATA_KEY, issued_at)
    payload["iat"] = issued_at
    payload["nbf"] = issued_at
    payload["jti"] = uuid4().hex
    payload["auth_time"] = auth_time
    return _original_create_token(
        self,
        userid,
        timeout=timeout,
        data=payload,
    )


JWTAuthenticationPlugin.absolute_session_timeout = ABSOLUTE_SESSION_TIMEOUT
JWTAuthenticationPlugin.create_token = create_token_with_issuer_claims
