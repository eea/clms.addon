""" Control Panel RestAPI endpoint
"""
from clms.addon.controlpanels.notifications_controlpanel.controlpanel import (INotificationsControlPanel)

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
