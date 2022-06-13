"""
Content rule string interpolator to return subscribed email address
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapter, getUtility
from zope.interface import Interface

from clms.addon import _
from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
)


@adapter(Interface)
class EventSubscriberSubstitution(BaseSubstitution):
    """ Subscriber substitution adapter"""

    category = _(u"Portal")
    description = _(u"Email addresses subscribed to event notifications")

    def safe_call(self):
        """ call the utility to get the subscribers """
        utility = getUtility(IEventNotificationsUtility)
        return ",".join(list(utility.list_subscribers().keys()))
