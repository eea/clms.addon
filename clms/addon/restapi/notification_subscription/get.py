""" get all the newsletter subscribers"""
# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.component import getUtility

from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
)


class GetNewsletterSubscribers(Service):
    """Get all newsletter subscribers"""

    def reply(self):
        """get all newsletter subscribers"""
        utility = getUtility(INewsLetterNotificationsUtility)
        subscribers = utility.list_subscribers()
        subscribers_as_dicts = []
        for key, value in subscribers.items():
            new_dict = {}
            new_dict["email"] = key
            new_dict.update(value)
            subscribers_as_dicts.append(new_dict)

        return {"subscribers": subscribers_as_dicts}


class GetNewsitemNotificationSubscribers(Service):
    """Get all newsitem notification subscribers"""

    def reply(self):
        """get all newsitem notification subscribers"""
        utility = getUtility(INewsItemNotificationsUtility)
        subscribers = utility.list_subscribers()
        subscribers_as_dicts = []
        for key, value in subscribers.items():
            new_dict = {}
            new_dict["email"] = key
            new_dict.update(value)
            subscribers_as_dicts.append(new_dict)

        return {"subscribers": subscribers_as_dicts}


class GetEventNotificationSubscribers(Service):
    """Get all event notification subscribers"""

    def reply(self):
        """get all evetn notification subscribers"""
        utility = getUtility(IEventNotificationsUtility)
        subscribers = utility.list_subscribers()
        subscribers_as_dicts = []
        for key, value in subscribers.items():
            new_dict = {}
            new_dict["email"] = key
            new_dict.update(value)
            subscribers_as_dicts.append(new_dict)

        return {"subscribers": subscribers_as_dicts}
