"""
Cleanump registrations
"""
# -*- coding: utf-8 -*-

from plone.restapi.services import Service
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
from zope.component import getUtility


class NewsItemNotificationSubscriptions(Service):
    """ Service implementation"""

    def reply(self):
        utility = getUtility(INewsItemNotificationsUtility)
        utility.cleanup_subscribers()
        self.request.response.setStatus(204)
        return {}


class EventNotificationSubscriptions(Service):
    """ Service implementation"""

    def reply(self):
        utility = getUtility(IEventNotificationsUtility)
        utility.cleanup_subscribers()
        self.request.response.setStatus(204)
        return {}


class NewsItemPendingNotificationSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return {}


class EventPendingNotificationSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        utility = getUtility(IEventPendingSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return {}


class NewsItemPendingNotificationUnSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return {}


class EventPendingNotificationUnSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        utility = getUtility(IEventPendingUnSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return {}
