"""
A utility to save all subscribers for event notifications
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


class IEventNotificationsUtility(INotificationsUtility):
    pass


@implementer(IEventNotificationsUtility)
class EventNotificationsUtility(NotificationsUtility):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.event_notification_subscribers"


class IEventPendingSubscriptionsUtility(IPendingSubscriptionHandler):
    pass


@implementer(IEventPendingSubscriptionsUtility)
class EventPendingSubscriptionsUtility(PendingSubscriptionHandler):
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.event_pending_subscriptions"
