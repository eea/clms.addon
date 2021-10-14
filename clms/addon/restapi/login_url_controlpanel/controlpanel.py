""" Control Panel RestAPI endpoint
"""
from clms.addon.controlpanels.login_url_controlpanel.controlpanel import (
    ILoginURLControlPanel,
)
from clms.addon.interfaces import IClmsAddonLayer
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface


@adapter(Interface, IClmsAddonLayer)
class LoginURLControlPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = ILoginURLControlPanel
    configlet_id = "login_url_controlpanel-controlpanel"
    configlet_category_id = "Products"
    title = "Login URL Control Panel"
    group = ""
    schema_prefix = "clms.addon.login_url_controlpanel"
