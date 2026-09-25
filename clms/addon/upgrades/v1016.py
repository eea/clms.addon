"""Configure server-side storage for REST API JWTs."""

from logging import getLogger

from BTrees.OOBTree import OOBTree
from plone import api


logger = getLogger(__name__)

TOKEN_TIMEOUT = 60 * 60


def upgrade(setup_tool=None):
    """Enable JWT revocation and use a one-hour token lifetime."""
    logger.info("Running upgrade (Python): v1016")

    portal = api.portal.get()
    jwt_auth = portal.acl_users.get("jwt_auth")
    if jwt_auth is None:
        raise RuntimeError("JWT authentication plugin 'jwt_auth' was not found")

    if getattr(jwt_auth, "_tokens", None) is None:
        jwt_auth._tokens = OOBTree()

    jwt_auth.store_tokens = True
    jwt_auth.token_timeout = TOKEN_TIMEOUT

    logger.info(
        "Enabled server-side JWT storage with a %s-second timeout",
        TOKEN_TIMEOUT,
    )
