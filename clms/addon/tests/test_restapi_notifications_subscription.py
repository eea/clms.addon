""" test the notifications related REST API endpoints """
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
from zope.component import getUtility

from clms.addon.testing import CLMS_ADDON_RESTAPI_TESTING
from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
    IEventPendingSubscriptionsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
    INewsItemPendingSubscriptionsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
    INewsLetterPendingSubscriptionsUtility,
)


class TestNewsItemNotificationsEndpoint(unittest.TestCase):
    """test the @newsitem-notification-* endpoints."""

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})

        self.manager_api_session = RelativeSession(self.portal_url)
        self.manager_api_session.headers.update({"Accept": "application/json"})
        self.manager_api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        """tearDown"""
        self.api_session.close()

    def test_newsitem_notifications_subscribe_is_registered(self):
        """test that a subscription request is registered"""

        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsitem-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 1)
        self.assertIn(
            "email@example.com",
            [item["email"] for item in utility.get_values()],
        )

    def test_confirm_subscription(self):
        """test that we can confirm a subscription"""
        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsitem-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsItemPendingSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not subscribed yet
        utility = getUtility(INewsItemNotificationsUtility)
        self.assertFalse(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = list(pending_utility.get_keys())

        response = self.api_session.post(
            "@newsitem-notification-subscribe-confirm/{}".format(keys[0])
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # now we have one item in the subscribers list
        self.assertTrue(utility.is_subscribed("email@example.com"))

    def test_confirm_subscription_with_no_key(self):
        """when trying to confirma a subscription without providing a key
        the endpoint should return an error
        """

        response = self.api_session.post(
            "@newsitem-notification-subscribe-confirm"
        )

        self.assertEqual(response.status_code, 400)

    def test_confirm_subscription_with_invalid_key(self):
        """when trying to confirm a subscription with an invalid key
        the endpoint should return an error
        """
        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsitem-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsItemPendingSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not subscribed yet
        utility = getUtility(INewsItemNotificationsUtility)
        self.assertFalse(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = list(pending_utility.get_keys())

        # create a random key
        random_key = "random_key"
        while random_key in keys:
            random_key += "-1"

        response = self.api_session.post(
            "@newsitem-notification-subscribe-confirm/{}".format(random_key)
        )

        self.assertEqual(response.status_code, 400)

    def test_notification_subscribers(self):
        """test getting all subscribers as manager"""

        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("subscriber1@example.com")
        utility.subscribe_address("subscriber2@example.com")
        transaction.commit()

        # if we make a subscription request
        response = self.manager_api_session.get(
            "@newsitem-notification-subscribers",
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("subscribers", result)
        self.assertEqual(len(result["subscribers"]), 2)

    def test_notification_subscribers_anonymous(self):
        """test getting all subscribers as anonymous is not allowed"""

        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("subscriber1@example.com")
        utility.subscribe_address("subscriber2@example.com")
        transaction.commit()

        # if we make a subscription request
        response = self.api_session.get(
            "@newsitem-notification-subscribers",
        )

        self.assertEqual(response.status_code, 401)


class TestEventNotificationsEndpoint(unittest.TestCase):
    """test the @event-notification-* endpoints."""

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})

        self.manager_api_session = RelativeSession(self.portal_url)
        self.manager_api_session.headers.update({"Accept": "application/json"})
        self.manager_api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        """tearDown"""
        self.api_session.close()

    def test_event_notifications_subscribe_is_registered(self):
        """test that a subscription request is registered"""

        utility = getUtility(IEventPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@event-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        utility = getUtility(IEventPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 1)
        self.assertIn(
            "email@example.com",
            [item["email"] for item in utility.get_values()],
        )

    def test_confirm_subscription(self):
        """test that we can confirm a subscription"""
        utility = getUtility(IEventPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@event-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(IEventPendingSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not subscribed yet
        utility = getUtility(IEventNotificationsUtility)
        self.assertFalse(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = list(pending_utility.get_keys())

        response = self.api_session.post(
            "@event-notification-subscribe-confirm/{}".format(keys[0])
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # now we have one item in the subscribers list
        self.assertTrue(utility.is_subscribed("email@example.com"))

    def test_confirm_subscription_with_no_key(self):
        """when trying to confirma a subscription without providing a key
        the endpoint should return an error
        """

        response = self.api_session.post(
            "@event-notification-subscribe-confirm"
        )

        self.assertEqual(response.status_code, 400)

    def test_confirm_subscription_with_invalid_key(self):
        """when trying to confirm a subscription with an invalid key
        the endpoint should return an error
        """

        utility = getUtility(IEventPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@event-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(IEventPendingSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not subscribed yet
        utility = getUtility(IEventNotificationsUtility)
        self.assertFalse(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = list(pending_utility.get_keys())

        # create a random key
        random_key = "random_key"
        while random_key in keys:
            random_key += "-1"

        response = self.api_session.post(
            "@event-notification-subscribe-confirm/{}".format(random_key)
        )

        self.assertEqual(response.status_code, 400)

    def test_notification_subscribers(self):
        """test getting all subscribers as manager"""

        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("subscriber1@example.com")
        utility.subscribe_address("subscriber2@example.com")
        transaction.commit()

        # if we make a subscription request
        response = self.manager_api_session.get(
            "@event-notification-subscribers",
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("subscribers", result)
        self.assertEqual(len(result["subscribers"]), 2)

    def test_notification_subscribers_anonymous(self):
        """test getting all subscribers as anonymous is not allowed"""

        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("subscriber1@example.com")
        utility.subscribe_address("subscriber2@example.com")
        transaction.commit()

        # if we make a subscription request
        response = self.api_session.get(
            "@event-notification-subscribers",
        )

        self.assertEqual(response.status_code, 401)


class TestNewsletterEndpoint(unittest.TestCase):
    """test the @newsletter-* endpoints."""

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})

        self.manager_api_session = RelativeSession(self.portal_url)
        self.manager_api_session.headers.update({"Accept": "application/json"})
        self.manager_api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        """tearDown"""
        self.api_session.close()
        self.manager_api_session.close()

    def test_newsletter_notifications_subscribe_is_registered(self):
        """test that a subscription request is registered"""

        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsletter-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 1)
        self.assertIn(
            "email@example.com",
            [item["email"] for item in utility.get_values()],
        )

    def test_confirm_subscription(self):
        """test that we can confirm a subscription"""
        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsletter-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not subscribed yet
        utility = getUtility(INewsLetterNotificationsUtility)
        self.assertFalse(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = list(pending_utility.get_keys())

        response = self.api_session.post(
            "@newsletter-notification-subscribe-confirm/{}".format(keys[0])
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # now we have one item in the subscribers list
        self.assertTrue(utility.is_subscribed("email@example.com"))

    def test_confirm_subscription_with_no_key(self):
        """when trying to confirma a subscription without providing a key
        the endpoint should return an error
        """

        response = self.api_session.post(
            "@newsletter-notification-subscribe-confirm"
        )

        self.assertEqual(response.status_code, 400)

    def test_confirm_subscription_with_invalid_key(self):
        """when trying to confirm a subscription with an invalid key
        the endpoint should return an error
        """

        # to test this we will create a subscription request, then create
        # a random key
        # which is different to an existing key, and try to confirm the
        # subscription with the random key

        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsletter-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not subscribed yet
        utility = getUtility(INewsLetterNotificationsUtility)
        self.assertFalse(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = list(pending_utility.get_keys())

        # create a random key
        random_key = "random_key"
        while random_key in keys:
            random_key += "-1"

        response = self.api_session.post(
            "@newsletter-notification-subscribe-confirm/{}".format(random_key)
        )

        self.assertEqual(response.status_code, 400)

    def test_confirm_subscription_with_multiple_keys(self):
        """when trying to confirm a subscription with multiple keys
        the endpoint should return an error
        """

        # to test this we will create a subscription request, then create a
        # random key
        # which is different to an existing key, and try to confirm the
        # subscription with the random key

        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        # starting from an empty list
        self.assertEqual(len(utility.get_keys()), 0)

        # if we make a subscription request
        response = self.api_session.post(
            "@newsletter-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        # we have one item there
        pending_utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        self.assertEqual(len(pending_utility.get_keys()), 1)

        # and we are not subscribed yet
        utility = getUtility(INewsLetterNotificationsUtility)
        self.assertFalse(utility.is_subscribed("email@example.com"))

        # get this item's key and make a confirmation request
        keys = list(pending_utility.get_keys())

        # create a random key
        random_key = "random_key"
        while random_key in keys:
            random_key += "-1"

        response = self.api_session.post(
            "@newsletter-notification-subscribe-confirm/{0}/{0}".format(
                random_key
            )
        )

        self.assertEqual(response.status_code, 400)

    def test_newsletter_subscribers(self):
        """test getting all subscribers as manager"""

        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("subscriber1@example.com")
        utility.subscribe_address("subscriber2@example.com")
        transaction.commit()

        # if we make a subscription request
        response = self.manager_api_session.get(
            "@newsletter-subscribers",
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("subscribers", result)
        self.assertEqual(len(result["subscribers"]), 2)

    def test_newsletter_subscribers_anonymous(self):
        """test getting all subscribers as anonymous is not allowed"""

        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("subscriber1@example.com")
        utility.subscribe_address("subscriber2@example.com")
        transaction.commit()

        # if we make a subscription request
        response = self.api_session.get(
            "@newsletter-subscribers",
        )

        self.assertEqual(response.status_code, 401)

    def test_subscribe_an_already_subscribed_user(self):
        """When a subscribed user makes a subscription request,
        the endpoint processes the result but the user receives a confirmation
        email saying nothing else is required on his part.
        """
        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("email@example.com")

        transaction.commit()

        response = self.api_session.post(
            "@newsletter-notification-subscribe",
            json={"email": "email@example.com"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "error")

    def test_subscribe_without_email(self):
        """if the email is not provided, the endpoint returns an error"""
        response = self.api_session.post(
            "@newsletter-notification-subscribe", json={}
        )
        self.assertEqual(response.status_code, 400)
