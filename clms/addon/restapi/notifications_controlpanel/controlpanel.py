""" Control Panel RestAPI endpoint
"""
# pylint: disable=line-too-long
from clms.addon.controlpanels.notifications_controlpanel.controlpanel import (  # noqa: E501
    INotificationsControlPanel,
)

from clms.addon.interfaces import IClmsAddonLayer
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface


@adapter(Interface, IClmsAddonLayer)
class NotificationsControlPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = INotificationsControlPanel
    configlet_id = "notifications-controlpanel"
    configlet_category_id = "Products"
    title = "Notifications Configuration Control Panel"
    group = ""
    schema_prefix = "clms.addon.notifications_controlpanel"
