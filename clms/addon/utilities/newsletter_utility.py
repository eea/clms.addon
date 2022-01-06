"""
A utility to save all subscribers for NewsLetter notifications
"""
# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.interface import implementer

from .base_notifications_utility import (
    INotificationsUtility,
    NotificationsUtility,
)
from .base_pending_subscriptions_utility import (
    IPendingSubscriptionHandler,
    PendingSubscriptionHandler,
)
from .base_pending_unsubscriptions_utility import (
    IPendingUnSubscriptionHandler,
    PendingUnSubscriptionHandler,
)


class INewsLetterNotificationsUtility(INotificationsUtility):
    """ utility interface """


@implementer(INewsLetterNotificationsUtility)
class NewsLetterNotificationsUtility(NotificationsUtility):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.newsletter_notification_subscribers"


class INewsLetterPendingSubscriptionsUtility(IPendingSubscriptionHandler):
    """ utility interface """


@implementer(INewsLetterPendingSubscriptionsUtility)
class NewsLetterPendingSubscriptionsUtility(PendingSubscriptionHandler):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.newsletter_pending_subscriptions"

    def do_something_with_confirmed_subscriber(self, subscriber):
        email = subscriber.get("email")
        if email is not None:
            utility = getUtility(INewsLetterNotificationsUtility)
            return utility.subscribe_address(email)
        return False


class INewsLetterPendingUnSubscriptionsUtility(IPendingUnSubscriptionHandler):
    """ utility interface """


@implementer(INewsLetterPendingUnSubscriptionsUtility)
class NewsLetterPendingUnSubscriptionsUtility(PendingUnSubscriptionHandler):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.NewsLetter_pending_unsubscriptions"

    def do_something_with_confirmed_unsubscriber(self, unsubscriber):
        email = unsubscriber.get("email")
        if email is not None:
            utility = getUtility(INewsLetterNotificationsUtility)
            return utility.unsubscribe_address(email)
        return False
