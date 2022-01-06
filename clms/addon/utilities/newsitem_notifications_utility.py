"""
A utility to save all subscribers for NewsItem notifications
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


class INewsItemNotificationsUtility(INotificationsUtility):
    """ utility interface """


@implementer(INewsItemNotificationsUtility)
class NewsItemNotificationsUtility(NotificationsUtility):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.newsitem_notification_subscribers"


class INewsItemPendingSubscriptionsUtility(IPendingSubscriptionHandler):
    """ utility interface"""


@implementer(INewsItemPendingSubscriptionsUtility)
class NewsItemPendingSubscriptionsUtility(PendingSubscriptionHandler):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.newsitem_pending_subscriptions"

    def do_something_with_confirmed_subscriber(self, subscriber):
        email = subscriber.get("email")
        if email is not None:
            utility = getUtility(INewsItemNotificationsUtility)
            return utility.subscribe_address(email)
        return False


class INewsItemPendingUnSubscriptionsUtility(IPendingUnSubscriptionHandler):
    """ utility interface """


@implementer(INewsItemPendingUnSubscriptionsUtility)
class NewsItemPendingUnSubscriptionsUtility(PendingUnSubscriptionHandler):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.newsitem_pending_unsubscriptions"

    def do_something_with_confirmed_unsubscriber(self, unsubscriber):
        email = unsubscriber.get("email")
        if email is not None:
            utility = getUtility(INewsItemNotificationsUtility)
            return utility.unsubscribe_address(email)
        return False
