""" test the subscription utility """
# -*- coding: utf-8 -*-


import unittest

from BTrees.OOBTree import OOBTree
from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
    INewsLetterPendingUnSubscriptionsUtility,
)
from freezegun import freeze_time
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility


class TestSubscriptionUtility(unittest.TestCase):
    """test the subscription utility"""

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        """set up"""
        self.portal = self.layer["portal"]
        self.utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)

    def test_create_pending_unsubscription(self):
        """create a new pending subscription"""
        self.utility.create_pending_unsubscription("email@example.com")

        annotations = IAnnotations(self.portal)
        subscribers = annotations.get(self.utility.ANNOTATION_KEY, OOBTree())
        self.assertEqual(len(subscribers), 1)

        self.assertIn(
            "email@example.com",
            [item["email"] for item in subscribers.values()],
        )

    def test_confirm_pending_unsubscription(self):
        """confirm the subscription"""
        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("email@example.com")

        key = self.utility.create_pending_unsubscription("email@example.com")

        result = self.utility.confirm_pending_unsubscription(key)
        self.assertTrue(result)

    def test_confirm_invalid_subscription_key(self):
        """confirm the unsubscription with an invalid key"""
        key = self.utility.create_pending_unsubscription("email@example.com")
        random_key = "random_key"
        while random_key == key:
            random_key += "-1"
        result = self.utility.confirm_pending_unsubscription(random_key)
        self.assertFalse(result)

    @freeze_time("2019-01-05")
    def test_cleanup_unconfirmed_subscriptions(self):
        """cleanup unconfirmed subscriptions"""
        # We will manually create some subscription with passed datetimes
        # and then delete the unconfirmed ones
        subscriber1 = {
            "status": "pending",
            "date": "2019-01-01T00:00:00.0",
            "email": "subscriber1@example.com",
        }
        subscriber2 = {
            "status": "pending",
            "date": "2019-01-02T00:00:00.0",
            "email": "subscriber2@example.com",
        }
        subscriber3 = {
            "status": "pending",
            "date": "2019-01-03T00:00:00.0",
            "email": "subscriber3@example.com",
        }

        annotations = IAnnotations(self.portal)
        subscribers = annotations.get(self.utility.ANNOTATION_KEY, OOBTree())
        subscribers["subscriber1"] = subscriber1
        subscribers["subscriber2"] = subscriber2
        subscribers["subscriber3"] = subscriber3
        annotations[self.utility.ANNOTATION_KEY] = subscribers

        self.assertEqual(len(self.utility.get_keys()), 3)

        self.utility.cleanup_unconfirmed_unsubscriptions(days=2)

        self.assertEqual(len(self.utility.get_keys()), 1)
