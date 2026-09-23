"""Tests for revoking stored REST API JWTs."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch

from clms.addon.subscribers.token_revocation import (
    get_principal_id,
    revoke_tokens_on_credentials_updated,
    revoke_tokens_on_principal_deleted,
    revoke_user_tokens,
)


class TokenRevocationTest(unittest.TestCase):
    """Test token revocation independently of token creation."""

    def make_portal(self, tokens=None, include_plugin=True):
        """Create the minimum PAS structure used by the helper."""
        plugins = {}
        if include_plugin:
            plugins["jwt_auth"] = SimpleNamespace(_tokens=tokens)
        return SimpleNamespace(acl_users=plugins)

    def test_revoke_user_tokens_removes_all_tokens_for_user(self):
        tokens = {
            "alice": {"token-one": 1, "token-two": 2},
            "bob": {"token-three": 3},
        }

        revoked = revoke_user_tokens("alice", self.make_portal(tokens))

        self.assertTrue(revoked)
        self.assertNotIn("alice", tokens)
        self.assertIn("bob", tokens)

    def test_revoke_user_tokens_ignores_missing_user(self):
        tokens = {"bob": {"token-three": 3}}

        revoked = revoke_user_tokens("alice", self.make_portal(tokens))

        self.assertFalse(revoked)
        self.assertEqual(tokens, {"bob": {"token-three": 3}})

    def test_revoke_user_tokens_ignores_missing_plugin(self):
        portal = self.make_portal(include_plugin=False)

        self.assertFalse(revoke_user_tokens("alice", portal))

    def test_revoke_user_tokens_ignores_missing_storage(self):
        portal = self.make_portal(tokens=None)

        self.assertFalse(revoke_user_tokens("alice", portal))

    def test_revoke_user_tokens_ignores_missing_acl_users(self):
        portal = SimpleNamespace()

        self.assertFalse(revoke_user_tokens("alice", portal))

    def test_get_principal_id_accepts_user_id(self):
        self.assertEqual(get_principal_id("alice"), "alice")

    def test_get_principal_id_uses_get_id(self):
        principal = Mock()
        principal.getId.return_value = "alice"

        self.assertEqual(get_principal_id(principal), "alice")

    @patch("clms.addon.subscribers.token_revocation.api.portal.get")
    def test_credentials_updated_revokes_principal_tokens(self, get_portal):
        tokens = {"alice": {"token-one": 1}}
        get_portal.return_value = self.make_portal(tokens)
        principal = Mock()
        principal.getId.return_value = "alice"

        revoke_tokens_on_credentials_updated(principal, Mock())

        self.assertNotIn("alice", tokens)

    @patch("clms.addon.subscribers.token_revocation.api.portal.get")
    def test_principal_deleted_revokes_principal_tokens(self, get_portal):
        tokens = {"alice": {"token-one": 1}}
        get_portal.return_value = self.make_portal(tokens)

        revoke_tokens_on_principal_deleted("alice", Mock())

        self.assertNotIn("alice", tokens)


if __name__ == "__main__":
    unittest.main()
