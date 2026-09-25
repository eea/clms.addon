"""Rotate REST API JWTs when renewing a login."""

from uuid import uuid4

from clms.addon.subscribers.token_revocation import revoke_token
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import (
    IAuthenticationPlugin,
)
from zope.interface import alsoProvides

import plone.protect.interfaces


INVALID_TOKEN_ERROR = {
    "error": {
        "type": "Invalid or expired authentication token",
        "message": "The authentication token is invalid or expired.",
    }
}


class Renew(Service):
    """Renew an authentication token and consume the presented token."""

    def get_jwt_plugin(self):
        """Return the active JWT authentication plugin, if installed."""
        acl_users = getToolByName(self, "acl_users")
        plugins = acl_users._getOb("plugins")
        authenticators = plugins.listPlugins(IAuthenticationPlugin)
        for _plugin_id, authenticator in authenticators:
            if authenticator.meta_type == "JWT Authentication Plugin":
                return authenticator
        return None

    def invalid_token(self):
        """Return the stock response for invalid or expired credentials."""
        self.request.response.setStatus(401)
        return INVALID_TOKEN_ERROR

    def reply(self):
        """Consume the old stored token and return a fresh stored token."""
        plugin = self.get_jwt_plugin()
        if plugin is None:
            self.request.response.setStatus(501)
            return {
                "error": {
                    "type": "Renew failed",
                    "message": "JWT authentication plugin not installed.",
                }
            }

        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request,
                plone.protect.interfaces.IDisableCSRFProtection,
            )

        membership = getToolByName(self.context, "portal_membership")
        if bool(membership.isAnonymousUser()):
            return self.invalid_token()

        if not plugin.store_tokens:
            self.request.response.setStatus(501)
            return {
                "error": {
                    "type": "Renew failed",
                    "message": "Server-side JWT storage is not enabled.",
                }
            }

        credentials = plugin.extractCredentials(self.request)
        old_token = credentials.get("token") if credentials else None
        user = membership.getAuthenticatedMember()
        user_id = user.getId()

        # Consume before minting. Both mutations commit in the same ZODB
        # transaction, and a concurrent request consuming the same token will
        # conflict and then observe that it has already been revoked.
        if not revoke_token(user_id, old_token, portal=self.context):
            return self.invalid_token()

        payload = {
            "fullname": user.getProperty("fullname"),
            "jti": uuid4().hex,
        }
        new_token = plugin.create_token(user_id, data=payload)
        return {"token": new_token}
