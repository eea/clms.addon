"""
A utility to save all subscribers for NewsItem notifications
"""
# -*- coding: utf-8 -*-

from zope.interface import implementer
from .base_notifications_utility import (
    INotificationsUtility,
    NotificationsUtility,
)
from .base_pending_subscriptions_utility import (
    IPendingSubscriptionHandler,
    PendingSubscriptionHandler,
)
from zope.component import getUtility


class INewsItemNotificationsUtility(INotificationsUtility):
    pass


@implementer(INewsItemNotificationsUtility)
class NewsItemNotificationsUtility(NotificationsUtility):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.newsitem_notification_subscribers"


class INewsItemPendingSubscriptionsUtility(IPendingSubscriptionHandler):
    pass


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
