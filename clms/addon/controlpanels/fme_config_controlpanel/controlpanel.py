# -*- coding: utf-8 -*-
"""
This is the control panel for fme configuration
"""
from clms.addon import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IFMEConfigControlPanel(Interface):
    """ Control Panel Schema """

    url = schema.TextLine(
        title=_(
            "Enter the URL of the FME server",
        ),
        description=_(
            "This url will be used to make dataset download and "
            "transformation requests",
        ),
        default=u"http://fme.server.com",
        required=True,
        readonly=False,
    )


class FMEConfigControlPanel(RegistryEditForm):
    """ control panel rest API endpoint configuration """

    schema = IFMEConfigControlPanel
    schema_prefix = "clms.addon.fme_config_controlpanel"
    label = _("FME Config Control Panel")


FMEConfigControlPanelView = layout.wrap_form(
    FMEConfigControlPanel, ControlPanelFormWrapper
)
