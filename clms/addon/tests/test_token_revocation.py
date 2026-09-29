"""Tests for revoking stored REST API JWTs."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch

from clms.addon.subscribers.token_revocation import (
    cleanup_expired_tokens,
    get_principal_id,
    revoke_tokens_on_credentials_updated,
    revoke_tokens_on_principal_deleted,
    revoke_token,
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

    def test_revoke_token_removes_only_presented_token(self):
        tokens = {
            "alice": {"token-one": 1, "token-two": 2},
            "bob": {"token-three": 3},
        }

        revoked = revoke_token("alice", "token-one", self.make_portal(tokens))

        self.assertTrue(revoked)
        self.assertNotIn("token-one", tokens["alice"])
        self.assertIn("token-two", tokens["alice"])
        self.assertIn("token-three", tokens["bob"])

    def test_revoke_token_ignores_unknown_token(self):
        tokens = {"alice": {"token-one": 1}}

        revoked = revoke_token("alice", "unknown", self.make_portal(tokens))

        self.assertFalse(revoked)
        self.assertIn("token-one", tokens["alice"])

    def test_cleanup_removes_expired_and_invalid_tokens(self):
        tokens = {
            "alice": {"expired": 1, "valid": 2, "no-expiry": 3},
            "bob": {"invalid": 4},
        }
        payloads = {
            "expired": {"exp": 99},
            "valid": {"exp": 101},
            "no-expiry": {"sub": "alice"},
            "invalid": None,
        }
        plugin = SimpleNamespace(
            _tokens=tokens,
            _decode_token=lambda token, verify=False: payloads[token],
        )

        removed = cleanup_expired_tokens(plugin, now=100)

        self.assertEqual(2, removed)
        self.assertEqual({"valid": 2, "no-expiry": 3}, tokens["alice"])
        self.assertNotIn("bob", tokens)
        self.assertEqual(100, plugin._last_token_cleanup)

    def test_cleanup_is_throttled(self):
        tokens = {"alice": {"expired": 1}}
        plugin = SimpleNamespace(
            _tokens=tokens,
            _last_token_cleanup=100,
            _decode_token=Mock(return_value={"exp": 1}),
        )

        removed = cleanup_expired_tokens(plugin, now=101)

        self.assertEqual(0, removed)
        self.assertIn("expired", tokens["alice"])
        plugin._decode_token.assert_not_called()

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
