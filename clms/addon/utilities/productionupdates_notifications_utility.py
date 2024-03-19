"""
A utility to save all subscribers for ProductionUpdates notifications
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


class IProductionUpdatesNotificationsUtility(INotificationsUtility):
    """ utility interface """


@implementer(IProductionUpdatesNotificationsUtility)
class ProductionUpdatesNotificationsUtility(NotificationsUtility):
    """ utility implementation """

    # pylint: disable=line-too-long
    ANNOTATION_KEY = "clms.addon.productionupdates_notification_subscribers"  # noqa

# pylint: disable=line-too-long
class IProductionUpdatesPendingSubscriptionsUtility(IPendingSubscriptionHandler):  # noqa
    """ utility interface"""


@implementer(IProductionUpdatesPendingSubscriptionsUtility)
# pylint: disable=line-too-long
class ProductionUpdatesPendingSubscriptionsUtility(
    PendingSubscriptionHandler
):  # noqa
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.productionupdates_pending_subscriptions"

    def do_something_with_confirmed_subscriber(self, subscriber):
        email = subscriber.get("email")
        if email is not None:
            utility = getUtility(IProductionUpdatesNotificationsUtility)
            return utility.subscribe_address(email)
        return False


class IProductionUpdatesPendingUnSubscriptionsUtility(
    IPendingUnSubscriptionHandler
):  # noqa
    """ utility interface """


@implementer(IProductionUpdatesPendingUnSubscriptionsUtility)
class ProductionUpdatesPendingUnSubscriptionsUtility(
    PendingUnSubscriptionHandler
):  # noqa
    """ utility implementation """

    ANNOTATION_KEY = "clms.addon.productionupdates_pending_unsubscriptions"

    def do_something_with_confirmed_unsubscriber(self, unsubscriber):
        email = unsubscriber.get("email")
        if email is not None:
            utility = getUtility(IProductionUpdatesNotificationsUtility)
            return utility.unsubscribe_address(email)
        return False
