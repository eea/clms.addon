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
    IEventPendingUnSubscriptionsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemPendingUnSubscriptionsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterPendingUnSubscriptionsUtility,
)


@implementer(IPublishTraverse)
class BaseNotificationsUnSubscribeConfirmHandler(Service):
    """ base class for the notification unsubscribe confirm handler """

    @property
    def utility_interface(self):
        """ utility to save the actual subscription request """
        raise NotImplementedError(
            "You need to define the interface in your class"
        )

    def __init__(self, context, request):
        """ initialize the handler """
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        """ Consume any path segments after the base url as parameters"""
        self.params.append(name)
        return self

    @property
    def _get_key(self):
        """ get the key from the request """
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter the key to be confirmed"
            )

        return self.params[0]

    def reply(self):
        """ return the real response """
        alsoProvides(self.request, IDisableCSRFProtection)
        if self.params:
            utility = getUtility(self.utility_interface)
            if utility.confirm_pending_unsubscription(self._get_key):
                self.request.response.setStatus(204)
                return _no_content_marker

            self.request.response.setStatus(400)
            return {"error": "Provided key is not valid"}

        self.request.response.setStatus(400)
        return {"error": "You need to provide a key"}


class NewsItemNotificationsUnSubscribeConfirm(
    BaseNotificationsUnSubscribeConfirmHandler
):
    """News Item implementation """

    utility_interface = INewsItemPendingUnSubscriptionsUtility


class EventNotificationsUnSubscribeConfirm(
    BaseNotificationsUnSubscribeConfirmHandler
):
    """ Event implementation """

    utility_interface = IEventPendingUnSubscriptionsUtility


class NewsLetterNotificationsUnSubscribeConfirm(
    BaseNotificationsUnSubscribeConfirmHandler
):
    """ NewsLetter implementation """

    utility_interface = INewsLetterPendingUnSubscriptionsUtility
