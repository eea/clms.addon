"""Revoke REST API JWTs when a principal changes or is removed."""

from logging import getLogger
from time import time

from plone import api


logger = getLogger(__name__)


TOKEN_CLEANUP_INTERVAL = 15 * 60


def get_principal_id(principal):
    """Return the user ID represented by a PAS principal or ID string."""
    if isinstance(principal, str):
        return principal

    get_id = getattr(principal, "getId", None)
    if get_id is not None:
        return get_id()

    get_user_name = getattr(principal, "getUserName", None)
    if get_user_name is not None:
        return get_user_name()

    return None


def revoke_user_tokens(user_id, portal=None):
    """Remove all stored JWTs for a user.

    Return whether an entry was removed. Missing PAS state is intentionally a
    no-op so credential updates cannot fail because JWT authentication is not
    installed or has not yet been configured.
    """
    if not user_id:
        return False

    if portal is None:
        portal = api.portal.get()

    acl_users = getattr(portal, "acl_users", None)
    if acl_users is None:
        return False

    jwt_auth = acl_users.get("jwt_auth")
    if jwt_auth is None:
        return False

    tokens = getattr(jwt_auth, "_tokens", None)
    if tokens is None or user_id not in tokens:
        return False

    del tokens[user_id]
    logger.info("Revoked all REST API JWTs for principal %s", user_id)
    return True


def revoke_token(user_id, token, portal=None):
    """Remove one stored JWT without affecting the user's other sessions."""
    if not user_id or not token:
        return False

    if portal is None:
        portal = api.portal.get()

    acl_users = getattr(portal, "acl_users", None)
    if acl_users is None:
        return False

    jwt_auth = acl_users.get("jwt_auth")
    if jwt_auth is None:
        return False

    tokens = getattr(jwt_auth, "_tokens", None)
    if tokens is None or user_id not in tokens:
        return False

    user_tokens = tokens[user_id]
    if token not in user_tokens:
        return False

    del user_tokens[token]
    logger.info("Revoked one REST API JWT for principal %s", user_id)
    return True


def cleanup_expired_tokens(jwt_auth, now=None, force=False):
    """Remove expired or invalid JWTs from server-side storage.

    Cleanup is normally triggered during token creation and throttled to avoid
    scanning the complete token store for every login.  Passing ``force`` is
    useful for explicit maintenance calls.
    """
    tokens = getattr(jwt_auth, "_tokens", None)
    if tokens is None:
        return 0

    if now is None:
        now = int(time())

    last_cleanup = getattr(jwt_auth, "_last_token_cleanup", None)
    if (
        not force
        and last_cleanup is not None
        and now - last_cleanup < TOKEN_CLEANUP_INTERVAL
    ):
        return 0

    removed = 0
    for user_id in list(tokens.keys()):
        user_tokens = tokens[user_id]
        for token in list(user_tokens.keys()):
            payload = jwt_auth._decode_token(token, verify=False)
            expires = payload.get("exp") if payload else None
            if payload is None or (expires is not None and expires <= now):
                del user_tokens[token]
                removed += 1

        if not user_tokens:
            del tokens[user_id]

    jwt_auth._last_token_cleanup = now
    if removed:
        logger.info("Removed %d expired or invalid REST API JWTs", removed)
    return removed


def revoke_tokens_on_credentials_updated(principal, event):
    """Revoke a principal's JWTs after its credentials change."""
    revoke_user_tokens(get_principal_id(principal))


def revoke_tokens_on_principal_deleted(principal, event):
    """Remove a deleted principal's JWTs."""
    revoke_user_tokens(get_principal_id(principal))
