"""
Content rule string interpolator to return subscribed email address
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapter, getUtility
from zope.interface import Interface

from clms.addon import _
from clms.addon.utilities.productionupdates_notifications_utility import (
    IProductionUpdatesNotificationsUtility
)


@adapter(Interface)
class ProductionUpdatesSubscriberSubstitution(BaseSubstitution):
    """ Subscriber substitution adapter"""

    category = _("Portal")
    description = _("Email addresses subscribed to production "
                    "updates notifications")

    def safe_call(self):
        """ call the utility to get the subscribers """
        utility = getUtility(IProductionUpdatesNotificationsUtility)
        return ",".join(list(utility.list_subscribers().keys()))
