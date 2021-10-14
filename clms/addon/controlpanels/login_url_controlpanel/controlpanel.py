# -*- coding: utf-8 -*-
"""
This is the control panel for the login_url
"""
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface

# pylint: disable=C0412
from clms.addon import _


class ILoginURLControlPanel(Interface):
    """ Control Panel Schema """

    login_url = schema.TextLine(
        title=_(
            "Enter the URL, relative to the portal root to be used "
            "as a login url",
        ),
        description=_(
            "This will be used to login using EU Login and needs to "
            "point to the OIDC PAS Plugin",
        ),
        default=u"/api/acl_users/keycloak/login",
        required=True,
        readonly=False,
    )


class LoginURLControlPanel(RegistryEditForm):
    """ control panel rest API endpoint configuration """

    schema = ILoginURLControlPanel
    schema_prefix = "clms.addon.login_url_controlpanel"
    label = _("Login URL Control Panel")


LoginURLControlPanelView = layout.wrap_form(
    LoginURLControlPanel, ControlPanelFormWrapper
)
