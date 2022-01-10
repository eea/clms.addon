"""
A utility to save all subscribers for event notifications
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


class IEventNotificationsUtility(INotificationsUtility):
    """ utility interface """


@implementer(IEventNotificationsUtility)
class EventNotificationsUtility(NotificationsUtility):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.event_notification_subscribers"


class IEventPendingSubscriptionsUtility(IPendingSubscriptionHandler):
    """ utility interface """


@implementer(IEventPendingSubscriptionsUtility)
class EventPendingSubscriptionsUtility(PendingSubscriptionHandler):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.event_pending_subscriptions"

    def do_something_with_confirmed_subscriber(self, subscriber):
        email = subscriber.get("email")
        if email is not None:
            utility = getUtility(IEventNotificationsUtility)
            return utility.subscribe_address(email)
        return False


class IEventPendingUnSubscriptionsUtility(IPendingUnSubscriptionHandler):
    """ utility interface """


@implementer(IEventPendingUnSubscriptionsUtility)
class EventPendingUnSubscriptionsUtility(PendingUnSubscriptionHandler):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.event_pending_unsubscriptions"

    def do_something_with_confirmed_unsubscriber(self, unsubscriber):
        email = unsubscriber.get("email")
        if email is not None:
            utility = getUtility(IEventNotificationsUtility)
            return utility.unsubscribe_address(email)
        return False
