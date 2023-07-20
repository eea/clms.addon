""" base implementation"""
# -*- coding: utf-8 -*-
from datetime import datetime

from BTrees.OOBTree import OOBTree
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface, implementer


class INotificationsUtility(Interface):
    """Utility interface"""

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
        """return list of all subscribers"""

    def is_subscribed(email):
        """return whether the said e-mail address is subscribed"""


@implementer(INotificationsUtility)
class NotificationsUtility:
    """Utility implementation"""

    ANNOTATION_KEY = "clms.addon.dummykey"

    def subscribe_address(self, email):
        """subscribe email address"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        if email is not None and email.strip() and email not in subscribers:
            subscribers[email] = {"date": datetime.utcnow().isoformat()}
            annotations[self.ANNOTATION_KEY] = subscribers
            return True

        return False

    def unsubscribe_address(self, email):
        """unsubscribe email address"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        if email is not None and email.strip() and email in subscribers:
            del subscribers[email]
            annotations[self.ANNOTATION_KEY] = subscribers
            return True

        return False

    def list_subscribers(self):
        """return all subscribers"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        return subscribers

    def cleanup_subscribers(self):
        """cleanup the registry"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        annotations[self.ANNOTATION_KEY] = OOBTree()

    def is_subscribed(self, email):
        """return if the email is already subscribed"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        if email is not None and email.strip():
            return email in subscribers

        return False
