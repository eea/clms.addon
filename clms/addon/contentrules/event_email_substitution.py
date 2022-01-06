"""
Content rule string interpolator to return subscribed email address
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import getUtility, adapter

from clms.addon import _
from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
)
from zope.interface import Interface


@adapter(Interface)
class EventSubscriberSubstitution(BaseSubstitution):

    category = _(u"Portal")
    description = _(u"Email addresses subscribed to event notifications")

    def safe_call(self):
        utility = getUtility(IEventNotificationsUtility)
        return utility.list_subscribers()
