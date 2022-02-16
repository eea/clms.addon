"""
Pending subscription handlers
"""
import uuid
from datetime import datetime, timedelta

from persistent.mapping import PersistentMapping
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface, implementer


class IPendingUnSubscriptionHandler(Interface):
    """
    Pending subscription handler
    """

    def create_pending_unsubscription(email):
        """
        Create pending subscription
        """

    def confirm_pending_unsubscription(email):
        """
        Confirm pending subscription
        """

    def cleanup_unconfirmed_unsubscriptions(days):
        """ delete unconfirmed items older than days days"""


@implementer(IPendingUnSubscriptionHandler)
class PendingUnSubscriptionHandler:
    """ Handler implementation """

    ANNOTATION_KEY = "clms.addon.dummy_pending_unsubscriptions"

    def create_pending_unsubscription(self, email):
        """ create pending subscription and return a key"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        key = uuid.uuid4().hex
        while key in subscribers:
            key = uuid.uuid4().hex

        subscribers[key] = {
            "email": email,
            "date": datetime.utcnow().isoformat(),
            "status": "pending",
        }
        annotations[self.ANNOTATION_KEY] = subscribers
        return key

    def confirm_pending_unsubscription(self, key):
        """ mark a given key as confirmed """
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        if key in subscribers:
            subscribers[key]["status"] = "confirmed"
            subscribers[key][
                "confirmation_date"
            ] = datetime.utcnow().isoformat()
            annotations[self.ANNOTATION_KEY] = subscribers
            return self.do_something_with_confirmed_unsubscriber(
                subscribers[key]
            )

        return False

    def cleanup_unconfirmed_unsubscriptions(self, days=7):
        """delete unconfirmed subscriptions older than the said number of
        days
        """
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        new_subscribers = PersistentMapping()
        for key in subscribers.keys():
            if subscribers[key]["status"] == "pending":
                date_difference = datetime.utcnow() - datetime.strptime(
                    subscribers[key]["date"], "%Y-%m-%dT%H:%M:%S.%f"
                )
                if date_difference <= timedelta(days=days):
                    new_subscribers[key] = subscribers[key]

        annotations[self.ANNOTATION_KEY] = new_subscribers

    def do_something_with_confirmed_unsubscriber(self, unsubscriber):
        """ do something with the confirmed unsubscriber """
        raise NotImplementedError(
            "You need to implement this method in your subclass"
        )

    def cleanup_requests(self):
        """ cleanup all requests """
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        annotations[self.ANNOTATION_KEY] = PersistentMapping()

    def get_keys(self):
        """ return all registered keys"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        return subscribers.keys()

    def get_values(self):
        """ return all registered values"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        return subscribers.values()
