"""
Content rule string interpolator to return subscribed email address
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapter, getUtility
from zope.interface import Interface

from clms.addon import _
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
)


@adapter(Interface)
class NewsItemSubscriberSubstitution(BaseSubstitution):
    """ Subscriber substitution adapter"""

    category = _(u"Portal")
    description = _(u"Email addresses subscribed to newsitem notifications")

    def safe_call(self):
        """ call the utility to get the subscribers """
        utility = getUtility(INewsItemNotificationsUtility)
        return list(utility.list_subscribers().keys())
