""" controlpanel tests """
# -*- coding: utf-8 -*-
import unittest

from plone import api
from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING  # noqa: E501


class TestControlPanel(unittest.TestCase):
    """Test that clms.addon is properly installed."""

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.controlpanel = api.portal.get_tool("portal_controlpanel")

    def test_login_url_controlpanel_installed(self):
        self.assertIn(
            "login_url_controlpanel-controlpanel",
            [item.id for item in self.controlpanel.listActions()],
        )

    def test_notifications_controlpanel_installed(self):
        self.assertIn(
            "notifications-controlpanel",
            [item.id for item in self.controlpanel.listActions()],
        )
