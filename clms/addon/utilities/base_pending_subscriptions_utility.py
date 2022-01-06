"""
Pending subscription handlers
"""
from datetime import datetime
from zope.interface import Interface
from zope.interface import implementer
from plone import api
from zope.annotation.interfaces import IAnnotations
from persistent.mapping import PersistentMapping
from uuid import uuid
from datetime import timedelta


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
        """ delete unconfirmed items older than days days"""


@implementer(IPendingSubscriptionHandler)
class PendingSubscriptionHandler:
    """ Handler implementation """

    ANNOTATION_KEY = "clms.addon.dummy_pending_subscriptions"

    def create_pending_subscription(self, email):
        """ create pending subscription and return a key"""
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        key = uuid.uuid4().hex
        while key not in subscribers:
            key = uuid.uuid4().hex

        subscribers[key] = {
            "email": email,
            "date": datetime.utcnow().isoformat(),
            "status": "pending",
        }
        annotations[self.ANNOTATION_KEY] = subscribers
        return key

    def confirm_pending_subscription(self, key):
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
            return True

        return False

    def cleanup_unconfirmed_subscriptions(self, days=7):
        """ delete unconfirmed subscriptions older than the said number of days """
        portal = api.portal.get()
        annotations = IAnnotations(portal)
        subscribers = annotations.get(self.ANNOTATION_KEY, PersistentMapping())
        for key in subscribers.keys():
            if subscribers[key]["status"] == "pending":
                if (
                    datetime.utcnow()
                    - datetime.strptime(
                        subscribers[key]["date"], "%Y-%m-%dT%H:%M:%S.%f"
                    )
                ) > timedelta(days=days):
                    del subscribers[key]

        annotations[self.ANNOTATION_KEY] = subscribers
