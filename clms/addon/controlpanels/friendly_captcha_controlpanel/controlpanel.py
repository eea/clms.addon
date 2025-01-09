"""
control panel to save Friendly Captcha configuration
"""

# -*- coding: utf-8 -*-
from clms.addon import _
from clms.addon.interfaces import IClmsAddonLayer
from plone.app.registry.browser.controlpanel import (
    ControlPanelFormWrapper,
    RegistryEditForm,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.controlpanels.interfaces import IControlpanel
from plone.z3cform import layout
from zope import schema
from zope.component import adapter
from zope.interface import Interface, implementer


class IFriendlyCaptchaControlPanel(IControlpanel):
    """marker interface for the control panel"""


class IFriendlyCaptcha(Interface):
    """control panel schema"""

    public_key = schema.TextLine(
        title=_("Public key"),
        description=_("Site key"),
        required=True,
        default=_(""),
    )
    private_key = schema.TextLine(
        title=_("Private key"),
        description=_("Secret"),
        required=True,
        default=_(""),
    )


class FriendlyCaptchaView(RegistryEditForm):
    """control panel view"""

    schema = IFriendlyCaptcha
    schema_prefix = "clms.addon.friendly_captcha"
    label = _("Friendly Captcha Control Panel")


FriendlyCaptchaViewView = layout.wrap_form(
    FriendlyCaptchaView, ControlPanelFormWrapper)


@adapter(Interface, IClmsAddonLayer)
@implementer(IFriendlyCaptchaControlPanel)
class FriendlyCaptchaConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IFriendlyCaptcha
    configlet_id = "friendly-captcha-controlpanel"
    configlet_category_id = "Products"
    title = _("Friendly Captcha Control Panel")
    group = ""
    schema_prefix = "clms.addon.friendly_captcha"
