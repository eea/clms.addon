"""Revoke REST API JWTs when a principal changes or is removed."""

from logging import getLogger

from plone import api


logger = getLogger(__name__)


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


def revoke_tokens_on_credentials_updated(principal, event):
    """Revoke a principal's JWTs after its credentials change."""
    revoke_user_tokens(get_principal_id(principal))


def revoke_tokens_on_principal_deleted(principal, event):
    """Remove a deleted principal's JWTs."""
    revoke_user_tokens(get_principal_id(principal))
