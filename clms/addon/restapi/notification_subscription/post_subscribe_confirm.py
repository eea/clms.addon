"""
REST API information for notification subscriptions
"""
# -*- coding: utf-8 -*-

from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service, _no_content_marker
from zope.component import getUtility
from zope.interface import alsoProvides, implementer
from zope.publisher.interfaces import IPublishTraverse

from clms.addon.utilities.event_notifications_utility import (
    IEventPendingSubscriptionsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemPendingSubscriptionsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterPendingSubscriptionsUtility,
)
# pylint: disable=line-too-long
from clms.addon.utilities.productionupdates_notifications_utility import (
    IProductionUpdatesPendingSubscriptionsUtility
)


@implementer(IPublishTraverse)
class BaseNotificationsSubscribeConfirmHandler(Service):
    """ base class for the handlers """

    @property
    def utility_interface(self):
        """ get the utility interface """
        raise NotImplementedError(
            "You need to define the interface in your class"
        )

    def __init__(self, context, request):
        """ base initialization """
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        """ Consume any path segments after the base url as parameters"""
        self.params.append(name)
        return self

    @property
    def _get_key(self):
        """ get they key from params"""
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter the key to be confirmed"
            )

        return self.params[0]

    def reply(self):
        """ return the real response """
        alsoProvides(self.request, IDisableCSRFProtection)
        if self.params:
            try:
                key = self._get_key
                utility = getUtility(self.utility_interface)
                if utility.confirm_pending_subscription(key):
                    self.request.response.setStatus(204)
                    return _no_content_marker

                self.request.response.setStatus(400)
                return {"error": "Provided key is not valid"}
            except Exception:
                self.request.response.setStatus(400)
                return {"error": "You should provide just one key"}

        self.request.response.setStatus(400)
        return {"error": "You need to provide a key"}


class NewsItemNotificationsSubscribeConfirm(
    BaseNotificationsSubscribeConfirmHandler
):
    """News Item implementation """

    utility_interface = INewsItemPendingSubscriptionsUtility


class EventNotificationsSubscribeConfirm(
    BaseNotificationsSubscribeConfirmHandler
):
    """ Event implementation """

    utility_interface = IEventPendingSubscriptionsUtility


class NewsLetterNotificationsSubscribeConfirm(
    BaseNotificationsSubscribeConfirmHandler
):
    """ NewsLetter implementation """

    utility_interface = INewsLetterPendingSubscriptionsUtility


class ProductionUpdatesNotificationsSubscribeConfirm(
    BaseNotificationsSubscribeConfirmHandler
):
    """ Production updates implementation """

    utility_interface = IProductionUpdatesPendingSubscriptionsUtility
