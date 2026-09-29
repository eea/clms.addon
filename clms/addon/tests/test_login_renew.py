"""Tests for one-time JWT rotation during login renewal."""

import unittest
from time import time

from BTrees.OOBTree import OOBTree
from plone.app.testing import SITE_OWNER_NAME
from zope.event import notify
from ZPublisher.pubevents import PubStart

from clms.addon.session import (ABSOLUTE_SESSION_TIMEOUT, AUTH_TIME_DATA_KEY,
                                IDLE_ACTIVITY_UPDATE_INTERVAL,
                                IDLE_SESSION_TIMEOUT)
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

        result = self.traverse().reply()
        payload = self.plugin._decode_token(result["token"])

        self.assertIn("jti", payload)
        self.assertIn("iat", payload)

    def test_all_created_tokens_contain_current_issued_at(self):
        before = int(time())
        token = self.plugin.create_token(SITE_OWNER_NAME)
        after = int(time())

        payload = self.plugin._decode_token(token)

        self.assertGreaterEqual(payload["iat"], before)
        self.assertLessEqual(payload["iat"], after)
        self.assertEqual(payload["iat"], payload["nbf"])
        self.assertEqual(payload["iat"], payload["auth_time"])

    def test_all_created_tokens_contain_unique_token_ids(self):
        first_token = self.plugin.create_token(SITE_OWNER_NAME)
        second_token = self.plugin.create_token(SITE_OWNER_NAME)

        first_payload = self.plugin._decode_token(first_token)
        second_payload = self.plugin._decode_token(second_token)

        self.assertTrue(first_payload["jti"])
        self.assertNotEqual(first_payload["jti"], second_payload["jti"])

    def test_token_issuer_controls_issued_at(self):
        token = self.plugin.create_token(
            SITE_OWNER_NAME,
            data={"iat": 1, "nbf": 1},
        )

        payload = self.plugin._decode_token(token)

        self.assertGreater(payload["iat"], 1)
        self.assertEqual(payload["iat"], payload["nbf"])

    def test_token_issuer_controls_token_id(self):
        token = self.plugin.create_token(
            SITE_OWNER_NAME,
            data={"jti": "caller-controlled"},
        )

        payload = self.plugin._decode_token(token)

        self.assertNotEqual(payload["jti"], "caller-controlled")

    def test_token_issuer_controls_initial_auth_time(self):
        token = self.plugin.create_token(
            SITE_OWNER_NAME,
            data={"auth_time": 1},
        )

        payload = self.plugin._decode_token(token)

        self.assertGreater(payload["auth_time"], 1)

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

    def test_renewal_preserves_original_auth_time(self):
        original_auth_time = int(time()) - 60
        old_token = self.plugin.create_token(
            SITE_OWNER_NAME,
            data={AUTH_TIME_DATA_KEY: original_auth_time},
        )
        self.request._auth = f"Bearer {old_token}"

        result = self.traverse().reply()
        payload = self.plugin._decode_token(result["token"])

        self.assertEqual(original_auth_time, payload["auth_time"])

    def test_renewal_rejects_absolute_session_timeout(self):
        original_auth_time = int(time()) - ABSOLUTE_SESSION_TIMEOUT
        old_token = self.plugin.create_token(
            SITE_OWNER_NAME,
            data={AUTH_TIME_DATA_KEY: original_auth_time},
        )
        self.request._auth = f"Bearer {old_token}"

        result = self.traverse().reply()

        self.assertEqual(401, self.request.response.getStatus())
        self.assertEqual(
            "Invalid or expired authentication token", result["error"]["type"]
        )
        self.assertNotIn(old_token, self.plugin._tokens[SITE_OWNER_NAME])

    def test_idle_token_is_rejected_and_revoked(self):
        token = self.plugin.create_token(SITE_OWNER_NAME)
        self.plugin._tokens[SITE_OWNER_NAME][token] = (
            int(time()) - IDLE_SESSION_TIMEOUT
        )

        authenticated = self.plugin.authenticateCredentials(
            {
                "extractor": self.plugin.getId(),
                "token": token,
            }
        )

        self.assertIsNone(authenticated)
        self.assertNotIn(SITE_OWNER_NAME, self.plugin._tokens)

    def test_active_token_timestamp_update_is_throttled(self):
        token = self.plugin.create_token(SITE_OWNER_NAME)
        last_activity = int(time()) - IDLE_ACTIVITY_UPDATE_INTERVAL + 1
        self.plugin._tokens[SITE_OWNER_NAME][token] = last_activity

        authenticated = self.plugin.authenticateCredentials(
            {
                "extractor": self.plugin.getId(),
                "token": token,
            }
        )

        self.assertEqual((SITE_OWNER_NAME, SITE_OWNER_NAME), authenticated)
        self.assertEqual(
            last_activity,
            self.plugin._tokens[SITE_OWNER_NAME][token],
        )

    def test_active_token_timestamp_is_refreshed(self):
        token = self.plugin.create_token(SITE_OWNER_NAME)
        last_activity = int(time()) - IDLE_ACTIVITY_UPDATE_INTERVAL
        self.plugin._tokens[SITE_OWNER_NAME][token] = last_activity

        authenticated = self.plugin.authenticateCredentials(
            {
                "extractor": self.plugin.getId(),
                "token": token,
            }
        )

        self.assertEqual((SITE_OWNER_NAME, SITE_OWNER_NAME), authenticated)
        self.assertGreater(
            self.plugin._tokens[SITE_OWNER_NAME][token],
            last_activity,
        )


if __name__ == "__main__":
    unittest.main()
