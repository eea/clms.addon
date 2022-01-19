"""
Cleanump registrations
"""
# -*- coding: utf-8 -*-

from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service, _no_content_marker
from zope.component import getUtility
from zope.interface import alsoProvides

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
    INewsLetterPendingUnSubscriptionsUtility,
)


class NewsItemNotificationSubscriptions(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(INewsItemNotificationsUtility)
        utility.cleanup_subscribers()
        self.request.response.setStatus(204)
        return _no_content_marker


class NewsItemPendingNotificationSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(INewsItemPendingSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return _no_content_marker


class NewsItemPendingNotificationUnSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(INewsItemPendingUnSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return _no_content_marker


class EventNotificationSubscriptions(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(IEventNotificationsUtility)
        utility.cleanup_subscribers()
        self.request.response.setStatus(204)
        return _no_content_marker


class EventPendingNotificationSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(IEventPendingSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return _no_content_marker


class EventPendingNotificationUnSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(IEventPendingUnSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return _no_content_marker


class NewsLetterNotificationSubscriptions(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(INewsLetterNotificationsUtility)
        utility.cleanup_subscribers()
        self.request.response.setStatus(204)
        return _no_content_marker


class NewsLetterPendingNotificationSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(INewsLetterPendingSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return _no_content_marker


class NewsLetterPendingNotificationUnSubscriptionRequests(Service):
    """ Service implementation"""

    def reply(self):
        """ cleanup the registry """
        alsoProvides(self.request, IDisableCSRFProtection)
        utility = getUtility(INewsLetterPendingUnSubscriptionsUtility)
        utility.cleanup_requests()
        self.request.response.setStatus(204)
        return _no_content_marker
