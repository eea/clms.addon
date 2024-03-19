# -*- coding: utf-8 -*-
"""
This is the control panel for the login_url
"""
from clms.addon import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class INotificationsControlPanel(Interface):
    """ Control Panel Schema """

    newsitem_notification_subscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the newsitem notification subscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            " for the newsitems notifications subscription handled by the"
            " frontend",
        ),
        default="/newsitem-notification-subscription",
        required=True,
        readonly=False,
    )

    newsitem_notification_unsubscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the newsitem notification unsubscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            " for the newsitems notification unsubscription handled by the"
            " frontend",
        ),
        default="/newsitem-notification-unsubscription",
        required=True,
        readonly=False,
    )

    event_notification_subscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the event notification subscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            "for the events notifications subscription handled by the"
            " frontend",
        ),
        default="/event-notification-subscription",
        required=True,
        readonly=False,
    )

    event_notification_unsubscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the event notification unsubscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            " for the events notifications unsubscription handled by the"
            " frontend",
        ),
        default="/event-notification-unsubscription",
        required=True,
        readonly=False,
    )

    event_notification_subscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the event notification subscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            "for the events notifications subscription handled by the"
            " frontend",
        ),
        default="/event-notification-subscription",
        required=True,
        readonly=False,
    )

    event_notification_unsubscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the event notification unsubscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            " for the events notifications unsubscription handled by the"
            " frontend",
        ),
        default="/event-notification-unsubscription",
        required=True,
        readonly=False,
    )

    productionupdates_notification_subscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the production updates notification subscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            " for the production updates subscription handled by the frontend",
        ),
        default="/productionupdates-notification-subscription",
        required=True,
        readonly=False,
    )

    productionupdates_notification_unsubscriptions_url = schema.TextLine(
        title=_(
            "Base URL for the production updates notification unsubscription",
        ),
        description=_(
            "This base URL will be used to build the actual confirmation URL"
            " for the production updates unsubscription handled by the "
            "frontend",
        ),
        default="/productionupdates-notification-unsubscription",
        required=True,
        readonly=False,
    )


class NotificationsControlPanel(RegistryEditForm):
    """ control panel rest API endpoint configuration """

    schema = INotificationsControlPanel
    schema_prefix = "clms.addon.notifications_controlpanel"
    label = _("Login URL Control Panel")


NotificationsControlPanelView = layout.wrap_form(
    NotificationsControlPanel, ControlPanelFormWrapper
)
