""" test the notifications related REST API endpoints """
# -*- coding: utf-8 -*-

import unittest

from plone import api
from clms.addon.testing import CLMS_ADDON_RESTAPI_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from plone.restapi.testing import RelativeSession

from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
    INewsItemPendingUnSubscriptionsUtility,
)
from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
    IEventPendingUnSubscriptionsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
    INewsLetterPendingUnSubscriptionsUtility,
)

from zope.component import getUtility

import transaction


class TestNewsItemNotificationsEndpoint(unittest.TestCase):
    """ test the @newsitem-notification-* endpoints. """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})

    def test_newsitem_notifications_unsubscribe_is_registered(self):
        """test that a subscription request is registered, to get this,
        we need to subscribe a user first.

        We do it directly using the utility, without going through the
        subscription API

        """
        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsitem-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 1)

    def test_confirm_subscription(self):
        """ test that we can confirm a subscription """

        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsitem-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not unsubscribed yet
        utility = getUtility(INewsItemNotificationsUtility)
        self.assertTrue(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = [key for key in pending_utility.get_keys()]

        response = self.api_session.post(
            "@newsitem-notification-unsubscribe-confirm/{}".format(keys[0])
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # now we have one item in the unsubscribers list
        self.assertFalse(utility.is_subscribed("email@example.com"))

    def test_confirm_subscription_with_no_key(self):
        """when trying to confirma a subscription without providing a key
        the endpoint should return an error
        """

        response = self.api_session.post(
            "@newsitem-notification-unsubscribe-confirm"
        )

        self.assertEqual(response.status_code, 400)

    def test_confirm_subscription_with_invalid_key(self):
        """when trying to confirm a subscription with an invalid key
        the endpoint should return an error
        """

        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        # to test this we will create a subscription request, then create a random key
        # which is different to an existing key, and try to confirm the subscription with
        # the random key

        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsitem-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not unsubscribed yet
        utility = getUtility(INewsItemNotificationsUtility)
        self.assertTrue(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = [key for key in pending_utility.get_keys()]

        # create a random key
        random_key = "random_key"
        while random_key in keys:
            random_key += "-1"

        response = self.api_session.post(
            "@newsitem-notification-unsubscribe-confirm/{}".format(random_key)
        )

        self.assertEqual(response.status_code, 400)


class TestEventNotificationsEndpoint(unittest.TestCase):
    """ test the @event-notification-* endpoints. """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})

    def test_event_notifications_unsubscribe_is_registered(self):
        """ test that a subscription request is registered """

        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        utility = getUtility(IEventPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@event-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        utility = getUtility(IEventPendingUnSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 1)
        self.assertIn(
            "email@example.com",
            [item["email"] for item in utility.get_values()],
        )

    def test_confirm_subscription(self):
        """ test that we can confirm a subscription """
        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        utility = getUtility(IEventPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@event-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(IEventPendingUnSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not unsubscribed yet
        utility = getUtility(IEventNotificationsUtility)
        self.assertTrue(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = [key for key in pending_utility.get_keys()]

        response = self.api_session.post(
            "@event-notification-unsubscribe-confirm/{}".format(keys[0])
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # now we have one item in the unsubscribers list
        self.assertFalse(utility.is_subscribed("email@example.com"))

    def test_confirm_subscription_with_no_key(self):
        """when trying to confirma a subscription without providing a key
        the endpoint should return an error
        """

        response = self.api_session.post(
            "@event-notification-unsubscribe-confirm"
        )

        self.assertEqual(response.status_code, 400)

    def test_confirm_subscription_with_invalid_key(self):
        """when trying to confirm a subscription with an invalid key
        the endpoint should return an error
        """
        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        # to test this we will create a subscription request, then create a random key
        # which is different to an existing key, and try to confirm the subscription with
        # the random key

        utility = getUtility(IEventPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@event-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(IEventPendingUnSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not unsubscribed yet
        utility = getUtility(IEventNotificationsUtility)
        self.assertTrue(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = [key for key in pending_utility.get_keys()]

        # create a random key
        random_key = "random_key"
        while random_key in keys:
            random_key += "-1"

        response = self.api_session.post(
            "@event-notification-unsubscribe-confirm/{}".format(random_key)
        )

        self.assertEqual(response.status_code, 400)


class TestNewsletterEndpoint(unittest.TestCase):
    """ test the @newsletter-* endpoints. """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})

    def test_newsletter_notifications_unsubscribe_is_registered(self):
        """ test that a subscription request is registered """

        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("email@example.com")
        transaction.commit()

        utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsletter-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 1)
        self.assertIn(
            "email@example.com",
            [item["email"] for item in utility.get_values()],
        )

    def test_confirm_subscription(self):
        """ test that we can confirm a subscription """
        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("email@example.com")
        transaction.commit()

        utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsletter-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not unsubscribed yet
        utility = getUtility(INewsLetterNotificationsUtility)
        self.assertTrue(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = [key for key in pending_utility.get_keys()]

        response = self.api_session.post(
            "@newsletter-notification-unsubscribe-confirm/{}".format(keys[0])
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        self.assertFalse(utility.is_subscribed("email@example.com"))

    def test_confirm_subscription_with_no_key(self):
        """when trying to confirma a subscription without providing a key
        the endpoint should return an error
        """

        response = self.api_session.post(
            "@newsletter-notification-unsubscribe-confirm"
        )

        self.assertEqual(response.status_code, 400)

    def test_confirm_subscription_with_invalid_key(self):
        """when trying to confirm a subscription with an invalid key
        the endpoint should return an error
        """

        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        # to test this we will create a subscription request, then create a random key
        # which is different to an existing key, and try to confirm the subscription with
        # the random key

        utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsletter-notification-unsubscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not unsubscribed yet
        utility = getUtility(INewsLetterNotificationsUtility)
        self.assertTrue(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = [key for key in pending_utility.get_keys()]

        # create a random key
        random_key = "random_key"
        while random_key in keys:
            random_key += "-1"

        response = self.api_session.post(
            "@newsletter-notification-unsubscribe-confirm/{}".format(
                random_key
            )
        )

        self.assertEqual(response.status_code, 400)
