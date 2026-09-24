"""Tests for one-time JWT rotation during login renewal."""

import unittest

from BTrees.OOBTree import OOBTree
from plone.app.testing import SITE_OWNER_NAME
from plone.restapi.services.auth.renew import Renew as StockRenew
from zope.event import notify
from ZPublisher.pubevents import PubStart

from clms.addon.restapi.login_renew.post import Renew
from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING


class LoginRenewTest(unittest.TestCase):
    """Verify that renewing consumes exactly one stored token."""

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.plugin = self.portal.acl_users.jwt_auth
        self.plugin.store_tokens = True
        self.plugin._tokens = OOBTree()

    def traverse(self):
        path = "/plone/@login-renew"
        self.request.environ["PATH_INFO"] = path
        self.request.environ["PATH_TRANSLATED"] = path
        self.request.environ["HTTP_ACCEPT"] = "application/json"
        self.request.environ["REQUEST_METHOD"] = "POST"
        notify(PubStart(self.request))
        return self.request.traverse(path)

    def test_custom_service_overrides_stock_renewal(self):
        token = self.plugin.create_token(SITE_OWNER_NAME)
        self.request._auth = f"Bearer {token}"

        service = self.traverse()

        self.assertIsInstance(service, Renew)
        self.assertNotIsInstance(service, StockRenew)

    def test_renewal_replaces_presented_token(self):
        old_token = self.plugin.create_token(SITE_OWNER_NAME)
        self.request._auth = f"Bearer {old_token}"

        result = self.traverse().reply()
        new_token = result["token"]

        self.assertNotEqual(old_token, new_token)
        stored_tokens = self.plugin._tokens[SITE_OWNER_NAME]
        self.assertNotIn(old_token, stored_tokens)
        self.assertIn(new_token, stored_tokens)

    def test_renewal_preserves_other_sessions(self):
        old_token = self.plugin.create_token(
            SITE_OWNER_NAME,
            data={"session": "renewed"},
        )
        other_token = self.plugin.create_token(
            SITE_OWNER_NAME,
            data={"session": "other"},
        )
        self.request._auth = f"Bearer {old_token}"

        result = self.traverse().reply()

        stored_tokens = self.plugin._tokens[SITE_OWNER_NAME]
        self.assertNotIn(old_token, stored_tokens)
        self.assertIn(other_token, stored_tokens)
        self.assertIn(result["token"], stored_tokens)
        self.assertEqual(2, len(stored_tokens))


if __name__ == "__main__":
    unittest.main()
