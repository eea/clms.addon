""" Control Panel RestAPI endpoint
"""
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface

from clms.addon.controlpanels.fme_config_controlpanel.controlpanel import \
    IFMEConfigControlPanel
from clms.addon.interfaces import IClmsAddonLayer


@adapter(Interface, IClmsAddonLayer)
class FMEConfigControlPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IFMEConfigControlPanel
    configlet_id = "fme_config-controlpanel"
    configlet_category_id = "Products"
    title = "FME Config Control Panel"
    group = ""
    schema_prefix = "clms.addon.fme_config_controlpanel"
