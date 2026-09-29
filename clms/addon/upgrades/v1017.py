"""Configure an absolute lifetime for REST API sessions."""

from logging import getLogger

from plone import api

from clms.addon.session import ABSOLUTE_SESSION_TIMEOUT

logger = getLogger(__name__)


def upgrade(setup_tool=None):
    """Limit renewal chains to the configured absolute session lifetime."""
    logger.info("Running upgrade (Python): v1017")

    portal = api.portal.get()
    jwt_auth = portal.acl_users.get("jwt_auth")
    if jwt_auth is None:
        raise RuntimeError(
            "JWT authentication plugin 'jwt_auth' was not found"
        )

    jwt_auth.absolute_session_timeout = ABSOLUTE_SESSION_TIMEOUT
    logger.info(
        "Set the absolute REST API session timeout to %s seconds",
        ABSOLUTE_SESSION_TIMEOUT,
    )
