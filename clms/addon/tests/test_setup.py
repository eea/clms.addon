# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from plone.browserlayer import utils

from clms.addon.interfaces import IClmsAddonLayer
from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING

from Products.CMFPlone.utils import get_installer


class TestSetup(unittest.TestCase):
    """Test that clms.addon is properly installed."""

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if clms.addon is installed."""
        self.assertTrue(self.installer.is_product_installed("clms.addon"))

    def test_browserlayer(self):
        """Test that IClmsAddonLayer is registered."""
        self.assertIn(IClmsAddonLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    """ test that clms.addon is properly uninstalled """

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        """ setup"""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("clms.addon")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if clms.addon is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("clms.addon"))

    def test_browserlayer_removed(self):
        """Test that IClmsAddonLayer is removed."""
        self.assertNotIn(IClmsAddonLayer, utils.registered_layers())
