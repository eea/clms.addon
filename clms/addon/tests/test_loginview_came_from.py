import unittest
from urllib.parse import urlsplit

from plone import api

from clms.addon.browser.loginview import (
    add_token_fragment,
    is_safe_came_from,
    same_domain,
)
from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING


class TestIsSafeCameFrom(unittest.TestCase):
    """Test the ``is_safe_came_from`` redirect-target validator."""

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        """Set up the test."""
        self.portal = self.layer["portal"]
        self.portal_url = api.portal.get_tool("portal_url")

    def _check(self, came_from):
        """Run the validator with the real portal_url tool."""
        return is_safe_came_from(came_from, self.portal_url)

    def test_rejects_protocol_relative(self):
        """Protocol-relative URLs resolve to an arbitrary host."""
        self.assertFalse(self._check("//attacker.example"))
        self.assertFalse(self._check("//127.0.0.1:8000/"))

    def test_rejects_backslash_variants(self):
        """Backslash and mixed-slash tricks are rejected."""
        self.assertFalse(self._check("/\\attacker.example"))
        self.assertFalse(self._check("\\\\attacker.example"))
        self.assertFalse(self._check("/\\/attacker.example"))

    def test_rejects_dangerous_schemes(self):
        """javascript:/data: URIs must never be accepted."""
        self.assertFalse(self._check("javascript:alert(document.cookie)"))
        self.assertFalse(self._check("data:text/html,<script>1</script>"))

    def test_rejects_case_shifted_offsite_scheme(self):
        """Case must not defeat the check (HTTPS:// off-site)."""
        self.assertFalse(self._check("HTTPS://attacker.example"))
        self.assertFalse(self._check("HtTp://attacker.example"))

    def test_rejects_offsite_absolute_url(self):
        """Ordinary off-site absolute URLs are rejected."""
        self.assertFalse(self._check("https://attacker.example"))
        self.assertFalse(self._check("http://attacker.example/steal"))

    def test_rejects_host_suffix_lookalike(self):
        """A host that merely embeds the portal host is off-site."""
        portal_host = self.portal_url().split("//", 1)[-1].split("/", 1)[0]
        self.assertFalse(
            self._check("https://{}.attacker.example/".format(portal_host))
        )

    def test_rejects_control_characters(self):
        """CR/LF/NUL must not smuggle values through."""
        self.assertFalse(self._check("/en/page\r\nSet-Cookie: x=1"))
        self.assertFalse(self._check("/en/page\x00//evil.example"))

    def test_rejects_empty(self):
        """Empty / falsy values are not safe targets."""
        self.assertFalse(self._check(""))
        self.assertFalse(self._check(None))

    def test_accepts_local_paths(self):
        """Local paths (the normal case) are accepted."""
        self.assertTrue(self._check("/en/profile"))
        self.assertTrue(self._check("/en/some/deep/path?query=1"))
        self.assertTrue(self._check("en/relative"))

    def test_accepts_in_portal_absolute_url(self):
        """Absolute URLs inside the portal are accepted."""
        self.assertTrue(self._check(self.portal_url() + "/en/page"))

    def test_accepts_same_host_api_prefixed_url(self):
        """Same-host URLs (EU Login adds the /api prefix) are accepted."""
        portal = self.portal_url()
        self.assertTrue(same_domain(portal, portal + "/api/en/page"))
        self.assertTrue(self._check(portal + "/api/en/page"))


class TestAddTokenFragment(unittest.TestCase):
    """Test that the token is delivered as a URL fragment, not a query."""

    TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1MSJ9.abc-_123"

    def test_token_goes_in_fragment_not_query(self):
        """The token must land in the fragment, never the query string."""
        result = add_token_fragment("/en/profile", self.TOKEN)
        split = urlsplit(result)
        self.assertEqual(split.fragment, "access_token=" + self.TOKEN)
        self.assertNotIn("access_token", split.query)
        self.assertEqual(result, "/en/profile#access_token=" + self.TOKEN)

    def test_preserves_existing_query(self):
        """An existing query string is left untouched."""
        result = add_token_fragment("/en/page?foo=bar", self.TOKEN)
        split = urlsplit(result)
        self.assertEqual(split.query, "foo=bar")
        self.assertEqual(split.fragment, "access_token=" + self.TOKEN)

    def test_replaces_existing_fragment(self):
        """A pre-existing fragment is replaced, not appended to."""
        result = add_token_fragment("/en/page#stale", self.TOKEN)
        self.assertEqual(
            urlsplit(result).fragment, "access_token=" + self.TOKEN
        )

    def test_absolute_url(self):
        """Absolute URLs keep scheme/host and get the fragment."""
        result = add_token_fragment(
            "https://land.copernicus.eu/en/page", self.TOKEN
        )
        self.assertEqual(
            result,
            "https://land.copernicus.eu/en/page#access_token=" + self.TOKEN,
        )


class TestSameDomain(unittest.TestCase):
    """Test the ``same_domain`` helper."""

    def test_same_host(self):
        """Identical hosts match regardless of path."""
        self.assertTrue(
            same_domain("https://example.org/a", "https://example.org/api/b")
        )

    def test_different_host(self):
        """Different hosts do not match."""
        self.assertFalse(
            same_domain("https://example.org/", "https://evil.example/")
        )

    def test_non_http_scheme(self):
        """Non-http(s) values never count as same-domain."""
        self.assertFalse(
            same_domain("ftp://example.org", "https://example.org")
        )
        self.assertFalse(
            same_domain("/local/path", "https://example.org")
        )
