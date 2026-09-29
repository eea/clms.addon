"""Enforce an idle timeout for stored REST API JWTs."""

from logging import getLogger
from time import time

from plone.restapi.pas.plugin import JWTAuthenticationPlugin

from clms.addon.session import (IDLE_ACTIVITY_UPDATE_INTERVAL,
                                IDLE_SESSION_TIMEOUT)

logger = getLogger(__name__)

_original_authenticate_credentials = (
    JWTAuthenticationPlugin.authenticateCredentials
)


def authenticate_credentials_with_idle_timeout(self, credentials):
    """Reject idle JWTs and periodically persist their latest activity."""
    authenticated = _original_authenticate_credentials(self, credentials)
    if authenticated is None or not self.store_tokens:
        return authenticated

    token = credentials.get("token")
    user_id = authenticated[0]
    tokens = getattr(self, "_tokens", None)
    if tokens is None or user_id not in tokens:
        return None

    user_tokens = tokens[user_id]
    if token not in user_tokens:
        return None

    now = int(time())
    last_activity = user_tokens[token]
    idle_timeout = getattr(
        self,
        "idle_session_timeout",
        IDLE_SESSION_TIMEOUT,
    )

    if not isinstance(last_activity, (int, float)):
        user_tokens[token] = now
        return authenticated

    if now - last_activity >= idle_timeout:
        del user_tokens[token]
        if not user_tokens:
            del tokens[user_id]
        logger.info("Revoked idle REST API JWT for principal %s", user_id)
        return None

    update_interval = getattr(
        self,
        "idle_activity_update_interval",
        IDLE_ACTIVITY_UPDATE_INTERVAL,
    )
    if now - last_activity >= update_interval:
        user_tokens[token] = now

    return authenticated


JWTAuthenticationPlugin.idle_session_timeout = IDLE_SESSION_TIMEOUT
JWTAuthenticationPlugin.idle_activity_update_interval = (
    IDLE_ACTIVITY_UPDATE_INTERVAL
)
JWTAuthenticationPlugin.authenticateCredentials = (
    authenticate_credentials_with_idle_timeout
)
