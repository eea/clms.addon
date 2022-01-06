""" base implementation"""
# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface import implementer
from plone import api
from zope.annotation.interfaces import IAnnotations
from persistent.mapping import PersistentMapping
from datetime import datetime


class INotificationsUtility(Interface):
    """ Utility interface """

    def subscribe_address(email):
        """subscribe email address to notifications. Return True if
        subscription was OK False if the user is already
        subscribed
        """

    def unsubscribe_address(email):
        """unsubscribe email address to notifications. Return True if
        unsubscription was OK False if the user is not subscribed
        """

    def list_subscribers():
        """ return list of all subscribers """


@implementer(INotificationsUtility)
class NotificationsUtility:
    ANNOTATION_KEY = "clms.addon.dummykey"

    def subscribe_address(self, email):
        """ subscribe email address"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        if email is not None and email.strip():
            if email not in subscribers:
                subscribers[email] = {"date": datetime.utcnow().isoformat()}
                annotations[self.ANNOTATION_KEY] = subscribers
                return True

        return False

    def unsubscribe_address(self, email):
        """ unsubscribe email address"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        if email is not None and email.strip():
            if email in subscribers:
                del subscribers[email]
                annotations[self.ANNOTATION_KEY] = subscribers
                return True

        return False

    def list_subscribers(self):
        """ return all subscribers """
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        return [key for key in subscribers.keys()]

    def cleanup_subscribers(self):
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        annotations[self.ANNOTATION_KEY] = PersistentMapping()
