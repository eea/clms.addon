# -*- coding: utf-8 -*-
from clms.addon import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope.interface import Interface
from zope import schema


class ILoginURLControlPanel(Interface):
    login_url = schema.TextLine(
        title=_(
            u"Enter the URL, relative to the portal root to be used as a login url",
        ),
        description=_(
            u"This will be used to login using EU Login and needs to point to the OIDC PAS Plugin",
        ),
        default=u"/api/acl_users/keycloak/login",
        required=True,
        readonly=False,
    )


class LoginURLControlPanel(RegistryEditForm):
    schema = ILoginURLControlPanel
    schema_prefix = "clms.addon.login_url_controlpanel"
    label = _("Login URL Control Panel")


LoginURLControlPanelView = layout.wrap_form(
    LoginURLControlPanel, ControlPanelFormWrapper
)
