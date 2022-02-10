""" test the subscription utility """
# -*- coding: utf-8 -*-


import unittest

from persistent.mapping import PersistentMapping
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING
from clms.addon.utilities.base_notifications_utility import (
    INotificationsUtility,
)


class TestNotificationsUtility(unittest.TestCase):
    """ test the subscription utility """

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        """ setup """
        self.portal = self.layer["portal"]
        self.utility = getUtility(INotificationsUtility)

    def test_subscribe_address(self):
        """ test subscribe_address adds record"""
        result = self.utility.subscribe_address("email@example.com")
        self.assertTrue(result)
        self.assertTrue(self.utility.is_subscribed("email@example.com"))

        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(
            self.utility.ANNOTATION_KEY, PersistentMapping()
        )
        self.assertEqual(len(subscribers), 1)
        self.assertIn("email@example.com", subscribers)

    def test_unsubscribe_address(self):
        """ test unsubsribe address removes record"""
        self.utility.subscribe_address("email@example.com")

        result = self.utility.unsubscribe_address("email@example.com")
        self.assertTrue(result)
        self.assertFalse(self.utility.is_subscribed("email@example.com"))

        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(
            self.utility.ANNOTATION_KEY, PersistentMapping()
        )
        self.assertEqual(len(subscribers), 0)

    def test_list_subscribers(self):
        """ test added subscribers are in the list """
        self.utility.subscribe_address("email@example.com")
        self.assertIn("email@example.com", self.utility.list_subscribers())

    def test_is_subscribed(self):
        """ test that is_subscribed result return True for subscribed users"""
        self.utility.subscribe_address("email@example.com")
        self.assertTrue(self.utility.is_subscribed("email@example.com"))

    def test_is_not_subscribed(self):
        """ test not-subscribed users return False"""
        self.assertEqual(len(self.utility.list_subscribers()), 0)
        self.assertFalse(self.utility.is_subscribed("email@example.com"))

    def test_cleanup_subscribers(self):
        """ test cleanup subscribers empties the list"""
        self.utility.subscribe_address("email@example.com")
        self.assertEqual(len(self.utility.list_subscribers()), 1)
        self.utility.cleanup_subscribers()
        self.assertEqual(len(self.utility.list_subscribers()), 0)
