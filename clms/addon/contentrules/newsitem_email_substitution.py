"""
Content rule string interpolator to return subscribed email address
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import getUtility, adapter

from clms.addon import _
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
)
from zope.interface import Interface


@adapter(Interface)
class NewsItemSubscriberSubstitution(BaseSubstitution):

    category = _(u"Portal")
    description = _(u"Email addresses subscribed to newsitem notifications")

    def safe_call(self):
        utility = getUtility(INewsItemNotificationsUtility)
        return utility.list_subscribers()
