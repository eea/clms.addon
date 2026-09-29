"""Configure idle expiry for REST API sessions."""

from logging import getLogger
from time import time

from plone import api

from clms.addon.session import (IDLE_ACTIVITY_UPDATE_INTERVAL,
                                IDLE_SESSION_TIMEOUT)

logger = getLogger(__name__)


def upgrade(setup_tool=None):
    """Enable idle expiry without immediately invalidating active sessions."""
    logger.info("Running upgrade (Python): v1018")

    portal = api.portal.get()
    jwt_auth = portal.acl_users.get("jwt_auth")
    if jwt_auth is None:
        raise RuntimeError(
            "JWT authentication plugin 'jwt_auth' was not found"
        )

    jwt_auth.idle_session_timeout = IDLE_SESSION_TIMEOUT
    jwt_auth.idle_activity_update_interval = IDLE_ACTIVITY_UPDATE_INTERVAL

    now = int(time())
    tokens = getattr(jwt_auth, "_tokens", None)
    if tokens is not None:
        for user_tokens in tokens.values():
            for token in list(user_tokens.keys()):
                user_tokens[token] = now

    logger.info(
        "Enabled a %s-second REST API idle timeout with activity persisted "
        "every %s seconds",
        IDLE_SESSION_TIMEOUT,
        IDLE_ACTIVITY_UPDATE_INTERVAL,
    )
