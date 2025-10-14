"""
Pending subscription handlers
"""
import uuid
from datetime import datetime, timedelta, timezone

from BTrees.OOBTree import OOBTree
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface, implementer


class IPendingSubscriptionHandler(Interface):
    """
    Pending subscription handler
    """

    def create_pending_subscription(email):
        """
        Create pending subscription
        """

    def confirm_pending_subscription(email):
        """
        Confirm pending subscription
        """

    def cleanup_unconfirmed_subscriptions(days):
        """delete unconfirmed items older than days days"""


@implementer(IPendingSubscriptionHandler)
class PendingSubscriptionHandler:
    """Handler implementation"""

    ANNOTATION_KEY = "clms.addon.dummy_pending_subscriptions"

    def create_pending_subscription(self, email):
        """create pending subscription and return a key"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        key = uuid.uuid4().hex
        while key in subscribers:
            key = uuid.uuid4().hex

        now_datetime = datetime.now(timezone.utc).isoformat()
        subscribers[key] = {
            "email": email,
            "date": now_datetime,
            "status": "pending",
        }
        annotations[self.ANNOTATION_KEY] = subscribers
        return key

    def confirm_pending_subscription(self, key):
        """mark a given key as confirmed"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        now_datetime = datetime.now(timezone.utc).isoformat()
        if key in subscribers:
            subscribers[key]["status"] = "confirmed"
            subscribers[key]["confirmation_date"] = now_datetime
            annotations[self.ANNOTATION_KEY] = subscribers
            return self.do_something_with_confirmed_subscriber(
                subscribers[key]
            )

        return False

    def cleanup_unconfirmed_subscriptions(self, days=7):
        """delete unconfirmed subscriptions older than the said number of
        days
        """
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        new_subscribers = OOBTree()
        now_datetime = datetime.now(timezone.utc)

        for key in subscribers.keys():
            if subscribers[key]["status"] == "pending":
                date_str = subscribers[key]["date"]
                parsed_date = datetime.fromisoformat(date_str)
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)

                date_difference = now_datetime - parsed_date

                if date_difference <= timedelta(days=days):
                    new_subscribers[key] = subscribers[key]

        annotations[self.ANNOTATION_KEY] = new_subscribers

    def do_something_with_confirmed_subscriber(self, subscriber):
        """do something with the confirmed subscriber"""
        raise NotImplementedError(
            "You need to implement this method in your subclass"
        )

    def cleanup_requests(self):
        """cleanup all requests"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        annotations[self.ANNOTATION_KEY] = OOBTree()

    def get_keys(self):
        """return all registered keys"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        return subscribers.keys()

    def get_values(self):
        """return all registered values"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, OOBTree())
        return subscribers.values()
