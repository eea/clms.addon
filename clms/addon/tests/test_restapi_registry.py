""" test that @anon-registry endpoint works as expected.
    the endpoints allows anonymous access to all registry keys starting with
    clms all other keys are protected by login like in the Plone's @registry
    endpoint
"""
# -*- coding: utf-8 -*-
import unittest

from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession

from clms.addon.testing import CLMS_ADDON_RESTAPI_TESTING


class TestAnonRegistry(unittest.TestCase):
    """Test that @anon-registry works."""

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.anonymous_session = RelativeSession(self.portal_url)
        self.anonymous_session.headers.update({"Accept": "application/json"})

        # transaction.commit()

    def test_anonymous_clms(self):
        """ Access as an anonymous user to a clms key"""

        response = self.anonymous_session.get(
            "@anon-registry/clms.addon.login_url_controlpanel.login_url"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

    def test_anonymous_whole_registry(self):
        """ Access to whole registry values is restricted to logged in users"""
        response = self.anonymous_session.get("@anon-registry?b_size=9999")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

    def test_anonymous_plone(self):
        """ Access as an anonymous user to a plone key"""
        response = self.anonymous_session.get(
            "@anon-registry/plone.alignment_styles"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

    def test_logged_whole_registry(self):
        """ Test that when logged in, the whole registry is accessible"""

        response = self.api_session.get("@anon-registry")
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", result)

    def test_logged_plone(self):
        """ test logged user access to a plone key"""
        response = self.api_session.get(
            "@anon-registry/plone.alignment_styles"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )
