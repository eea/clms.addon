""" get all the newsletter subscribers"""
# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
)
from zope.component import getUtility


class Get(Service):
    """ Get all the newsletter subscribers"""

    def reply(self):
        """ get all the newsletter subscribers"""
        utility = getUtility(INewsLetterNotificationsUtility)
        subscribers = utility.list_subscribers()
        subscribers_as_dicts = []
        for key, value in subscribers.items():
            new_dict = {}
            new_dict["email"] = key
            new_dict.update(value)
            subscribers_as_dicts.append(new_dict)

        return {"subscribers": subscribers_as_dicts}
