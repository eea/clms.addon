""" test that login_url_controlpanel is available on REST API """
# -*- coding: utf-8 -*-
import unittest

import transaction
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.restapi.testing import RelativeSession

from clms.addon.testing import CLMS_ADDON_RESTAPI_TESTING


class TestDatasetSearch(unittest.TestCase):
    """Test that clms.addon is properly installed."""

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        transaction.commit()

    def test_controlpanel_available(self):
        """test that controlpanel information is available on REST API"""

        response = self.api_session.get("@controlpanels/login-url")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

        results = response.json()
        self.assertIn("schema", results)
        self.assertIn("fieldsets", results["schema"])
        self.assertIn("properties", results["schema"])
