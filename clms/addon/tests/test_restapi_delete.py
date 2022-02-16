"""
    test manger only endpoints to cleanup notification registries
"""
# -*- coding: utf-8 -*-


import unittest

import transaction
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

from clms.addon.testing import CLMS_ADDON_RESTAPI_TESTING
from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
    IEventPendingSubscriptionsUtility,
    IEventPendingUnSubscriptionsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
    INewsItemPendingSubscriptionsUtility,
    INewsItemPendingUnSubscriptionsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
    INewsLetterPendingSubscriptionsUtility,
)


class TestDeleteNewsletterRegistries(unittest.TestCase):
    """ test manger only endpoints to cleanup notification registries """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """ setup """
        self.portal = self.layer["portal"]
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})

        self.manager_api_session = RelativeSession(self.portal.absolute_url())
        self.manager_api_session.headers.update({"Accept": "application/json"})
        self.manager_api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        """ tear down and close sessions """
        self.api_session.close()
        self.manager_api_session.close()

    def test_newsletter_subscriptions_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification subscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-newsletter-notification-subscriptions"
        )
        self.assertEqual(response.status_code, 401)

    def test_newsletter_subscriptions_requests_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification subscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-newsletter-notification-subscription-requests"
        )
        self.assertEqual(response.status_code, 401)

    def test_newsletter_unsubscriptions_requests_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification unsubscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-newsletter-notification-unsubscription-requests"
        )
        self.assertEqual(response.status_code, 401)

    def test_newsletter_subscriptions_delete(
        self,
    ):
        """ test deleting notification subscriptions as manager """
        utility = getUtility(INewsLetterNotificationsUtility)
        utility.subscribe_address("email@example.com")
        self.assertEqual(len(utility.list_subscribers()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-newsletter-notification-subscriptions"
        )
        self.assertEqual(response.status_code, 204)

    def test_newsletter_subscriptions_requests_delete(
        self,
    ):
        """ test deleting notification subscriptions as manager """
        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        utility.create_pending_subscription("email@example.com")
        self.assertEqual(len(utility.get_keys()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-newsletter-notification-subscription-requests"
        )
        self.assertEqual(response.status_code, 204)

        transaction.commit()

        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 0)

    def test_newsletter_unsubscriptions_requests_delete(
        self,
    ):
        """ test deleting notification unsubscriptions as manager """
        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        utility.create_pending_unsubscription("email@example.com")
        self.assertEqual(len(utility.get_keys()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-newsletter-notification-unsubscription-requests"
        )
        self.assertEqual(response.status_code, 204)
        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 0)


class TestDeleteNewsitemNotificationRegistries(unittest.TestCase):
    """ test manager only endpoints to cleanup notification registries """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """ setup """
        self.portal = self.layer["portal"]
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})

        self.manager_api_session = RelativeSession(self.portal.absolute_url())
        self.manager_api_session.headers.update({"Accept": "application/json"})
        self.manager_api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        """ tear down and close sessions """
        self.api_session.close()
        self.manager_api_session.close()

    def test_newsitem_subscriptions_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification subscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-newsitem-notification-subscriptions"
        )
        self.assertEqual(response.status_code, 401)

    def test_newsitem_subscriptions_requests_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification subscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-newsitem-notification-subscription-requests"
        )
        self.assertEqual(response.status_code, 401)

    def test_newsitem_unsubscriptions_requests_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification unsubscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-newsitem-notification-unsubscription-requests"
        )
        self.assertEqual(response.status_code, 401)

    def test_newsitem_subscriptions_delete(
        self,
    ):
        """ test deleting notification subscriptions as manager """
        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("email@example.com")
        self.assertEqual(len(utility.list_subscribers()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-newsitem-notification-subscriptions"
        )
        self.assertEqual(response.status_code, 204)

    def test_newsitem_subscriptions_requests_delete(
        self,
    ):
        """ test deleting notification subscriptions as manager """
        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        utility.create_pending_subscription("email@example.com")
        self.assertEqual(len(utility.get_keys()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-newsitem-notification-subscription-requests"
        )
        self.assertEqual(response.status_code, 204)

        transaction.commit()

        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 0)

    def test_newsitem_unsubscriptions_requests_delete(
        self,
    ):
        """ test deleting notification unsubscriptions as manager """
        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        utility.create_pending_unsubscription("email@example.com")
        self.assertEqual(len(utility.get_keys()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-newsitem-notification-unsubscription-requests"
        )
        self.assertEqual(response.status_code, 204)
        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 0)


class TestDeleteEventNotificationRegistries(unittest.TestCase):
    """ test manager only endpoints to cleanup notification registries """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """ setup """
        self.portal = self.layer["portal"]
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})

        self.manager_api_session = RelativeSession(self.portal.absolute_url())
        self.manager_api_session.headers.update({"Accept": "application/json"})
        self.manager_api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        """ tear down and close sessions """
        self.api_session.close()
        self.manager_api_session.close()

    def test_event_subscriptions_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification subscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-event-notification-subscriptions"
        )
        self.assertEqual(response.status_code, 401)

    def test_event_subscriptions_requests_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification subscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-event-notification-subscription-requests"
        )
        self.assertEqual(response.status_code, 401)

    def test_event_unsubscriptions_requests_anonymous_delete_not_allowed(
        self,
    ):
        """ test deleting notification unsubscriptions as anonymous """
        response = self.api_session.delete(
            "/@cleanup-event-notification-unsubscription-requests"
        )
        self.assertEqual(response.status_code, 401)

    def test_event_subscriptions_delete(
        self,
    ):
        """ test deleting notification subscriptions as manager """
        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("email@example.com")
        self.assertEqual(len(utility.list_subscribers()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-event-notification-subscriptions"
        )
        self.assertEqual(response.status_code, 204)

    def test_event_subscriptions_requests_delete(
        self,
    ):
        """ test deleting notification subscriptions as manager """
        utility = getUtility(IEventPendingSubscriptionsUtility)
        utility.create_pending_subscription("email@example.com")
        self.assertEqual(len(utility.get_keys()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-event-notification-subscription-requests"
        )
        self.assertEqual(response.status_code, 204)

        transaction.commit()

        utility = getUtility(IEventPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 0)

    def test_event_unsubscriptions_requests_delete(
        self,
    ):
        """ test deleting notification unsubscriptions as manager """
        utility = getUtility(IEventPendingUnSubscriptionsUtility)
        utility.create_pending_unsubscription("email@example.com")
        self.assertEqual(len(utility.get_keys()), 1)

        transaction.commit()

        response = self.manager_api_session.delete(
            "/@cleanup-event-notification-unsubscription-requests"
        )
        self.assertEqual(response.status_code, 204)
        utility = getUtility(IEventPendingSubscriptionsUtility)
        self.assertEqual(len(utility.get_keys()), 0)
