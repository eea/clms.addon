""" test the subscription utility """
# -*- coding: utf-8 -*-


import unittest

from zope.component import getUtility

from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING
from clms.addon.utilities.base_pending_subscriptions_utility import (
    IPendingSubscriptionHandler,
)

from plone import api
from zope.annotation.interfaces import IAnnotations
from persistent.mapping import PersistentMapping
from freezegun import freeze_time


class TestUnSubscriptionUtility(unittest.TestCase):
    """ test the subscription utility """

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        """ set up"""
        self.portal = self.layer["portal"]
        self.utility = getUtility(IPendingSubscriptionHandler)

    def test_create_pending_subscription(self):
        """ create a new pending subscription """
        self.utility.create_pending_subscription("email@example.com")

        annotations = IAnnotations(self.portal)
        subscribers = annotations.get(
            self.utility.ANNOTATION_KEY, PersistentMapping()
        )
        self.assertEqual(len(subscribers), 1)

        self.assertIn(
            "email@example.com",
            [item["email"] for item in subscribers.values()],
        )

    def test_confirm_pending_subscription(self):
        """ confirm the subscription"""
        key = self.utility.create_pending_subscription("email@example.com")
        result = self.utility.confirm_pending_subscription(key)
        self.assertTrue(result)

    def test_confirm_invalid_subscription_key(self):
        key = self.utility.create_pending_subscription("email@example.com")
        random_key = "random_key"
        while random_key == key:
            random_key += "-1"
        result = self.utility.confirm_pending_subscription(random_key)
        self.assertFalse(result)

    @freeze_time("2019-01-05")
    def test_cleanup_unconfirmed_subscriptions(self):
        """ cleanup unconfirmed subscriptions """
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
        subscribers = annotations.get(
            self.utility.ANNOTATION_KEY, PersistentMapping()
        )
        subscribers["subscriber1"] = subscriber1
        subscribers["subscriber2"] = subscriber2
        subscribers["subscriber3"] = subscriber3
        annotations[self.utility.ANNOTATION_KEY] = subscribers

        self.assertEqual(len(self.utility.get_keys()), 3)

        self.utility.cleanup_unconfirmed_subscriptions(days=2)

        self.assertEqual(len(self.utility.get_keys()), 1)

    # def test_do_something_with_confirmed_subscriber(self):
    #     """this method should raise a NonImplementedError exception because
    #     it is meant to be implemented in a subclass
    #     """
    #     key = self.utility.create_pending_subscription("email@example.com")
    #     self.utility.confirm_pending_subscription(key)
    #     annotations = IAnnotations(self.portal)
    #     subscribers = annotations.get(
    #         self.utility.ANNOTATION_KEY, PersistentMapping()
    #     )
    #     subscriber = subscribers.get(key)
    #     self.assertRaises(
    #         NotImplementedError,
    #         self.utility.do_something_with_confirmed_subscriber,
    #         subscriber,
    #     )

    def test_cleanup_requests(self):
        pass

    def test_get_keys(self):
        pass

    def test_get_values(self):
        pass
