"""
REST API information for notification subscriptions
"""
# -*- coding: utf-8 -*-
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException

from chameleon import PageTemplateLoader
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service, _no_content_marker
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.utils import safe_text
from zope.component import getUtility
from zope.interface import alsoProvides

from clms.addon import _
from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
    IEventPendingSubscriptionsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
    INewsItemPendingSubscriptionsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
    INewsLetterPendingSubscriptionsUtility,
)

from clms.addon.utilities.productionupdates_notifications_utility import (
    IProductionUpdatesNotificationsUtility,
    IProductionUpdatesPendingSubscriptionsUtility
)


class BaseNotificationsSubscribeHandler(Service):
    """base class for the notification subscriptions"""

    @property
    def utility_interface(self):
        """utility to save the actual subscription request"""
        raise NotImplementedError(
            "You need to define the interface in your class"
        )

    @property
    def subscription_handler_utility(self):
        """utility that really handles the subscription. Will be used
        to check if the said e-mail address is already subscribed
        and if so inform the user with a message
        """
        raise NotImplementedError(
            "You need to define the interface in your class"
        )

    @property
    def registry_key_for_base_url(self):
        """the registry key for the confirmation url"""
        raise NotImplementedError("You need to define the key in your class")

    @property
    def unsubscribe_base_url(self):
        """the registry key for the unsubsribe url"""
        raise NotImplementedError("You need to define the key in your class")

    @property
    def email_subject(self):
        """return the email subject"""
        raise NotImplementedError(
            "You need to define the subject in your class"
        )

    @property
    def subscribe_email_message_template(self):
        """return the email subject"""
        raise NotImplementedError(
            "You need to define the subscribe_email_message_template in your"
            " class"
        )

    def email_message(self, url, portal_title, unsubscribe_url):
        """return the message"""
        path = os.path.dirname(__file__)
        templates = PageTemplateLoader(path)
        template = templates[self.subscribe_email_message_template]

        return template(
            portal_title=portal_title,
            url=url,
            unsubscribe_url=unsubscribe_url,
        )

    def reply(self):
        """return the real response"""
        alsoProvides(self.request, IDisableCSRFProtection)
        body = json_body(self.request)
        email = body.get("email")
        if email is not None:
            subscription_utility = getUtility(
                self.subscription_handler_utility
            )
            if subscription_utility.is_subscribed(email):
                self.request.response.setStatus(400)
                return {
                    "status": "error",
                    "message": "This e-mail address is already subscribed",
                }

            utility = getUtility(self.utility_interface)
            key = utility.create_pending_subscription(email)
            status = self.send_confirmation_email(email, key)
            if status:
                self.request.response.setStatus(204)
                return _no_content_marker

            self.request.response.setStatus(500)
            return {
                "status": "error",
                "message": (
                    "There was an error sending the email, try again please"
                ),
            }

        self.request.response.setStatus(400)
        return {"status": "error", "message": "No email address provided"}

    def send_confirmation_email(self, email, key):
        """send a confirmation email requesting the user to go to a
        given URL
        """
        registry = getUtility(IRegistry)
        url = registry.get(self.registry_key_for_base_url)

        unsubscribe_url = self.unsubscribe_base_url
        frontend_domain = api.portal.get_registry_record(
            "volto.frontend_domain"
        )
        if frontend_domain.endswith("/"):
            frontend_domain = frontend_domain[:-1]
        url = frontend_domain + "/en" + url + "/" + key
        unsubscribe_url = frontend_domain + "/en" + unsubscribe_url

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        from_address = mail_settings.email_from_address
        from_name = mail_settings.email_from_name
        source = '"{0}" <{1}>'.format(from_name, from_address)
        encoding = registry.get("plone.email_charset", "utf-8")
        host = api.portal.get_tool("MailHost")
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False
        )
        portal_title = site_settings.site_title
        subject = self.email_subject
        contents = self.email_message(url, portal_title, unsubscribe_url)

        message = MIMEMultipart("related")
        message["Subject"] = subject
        message["Reply-To"] = from_address
        message["From"] = source
        message.preamble = "This is a multi-part message in MIME format"

        msg_alternative = MIMEMultipart("alternative")
        message.attach(msg_alternative)

        msg_txt = MIMEText("This is the alternative plain text message.")
        msg_alternative.attach(msg_txt)

        msg_html = MIMEText(safe_text(contents), "html")
        msg_alternative.attach(msg_html)

        try:
            host.send(
                message.as_string(),
                email,
                source,
                subject=subject,
                charset=encoding,
            )

        except (SMTPException, RuntimeError):
            plone_utils = api.portal.get_tool("plone_utils")
            exception = plone_utils.exceptionString()
            message = "Unable to send mail: {exception}".format(
                exception=exception
            )

            return False

        return True


class NewsItemNotificationsSubscribe(BaseNotificationsSubscribeHandler):
    """News Item implementation"""

    utility_interface = INewsItemPendingSubscriptionsUtility
    subscription_handler_utility = INewsItemNotificationsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.newsitem_notification_subscriptions_url"  # noqa
    unsubscribe_base_url = "/unsubscribe/news"
    email_subject = _("Subscription to news notifications")
    subscribe_email_message_template = (
        "news_notifications_subscribe_template.pt"
    )


class EventNotificationsSubscribe(BaseNotificationsSubscribeHandler):
    """base class"""

    utility_interface = IEventPendingSubscriptionsUtility
    subscription_handler_utility = IEventNotificationsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.event_notification_subscriptions_url"  # noqa
    unsubscribe_base_url = "/unsubscribe/events"
    email_subject = _("Subscription to event notifications")
    subscribe_email_message_template = (
        "event_notifications_subscribe_template.pt"
    )


class NewsLetterNotificationsSubscribe(BaseNotificationsSubscribeHandler):
    """base class"""

    utility_interface = INewsLetterPendingSubscriptionsUtility
    subscription_handler_utility = INewsLetterNotificationsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.newsletter_notification_subscriptions_url"  # noqa
    unsubscribe_base_url = "/unsubscribe/newsletter"
    email_subject = _("Subscription to newsletter")
    subscribe_email_message_template = (
        "newsletter_notifications_subscribe_template.pt"
    )


class ProductionUpdatesNotificationsSubscribe(
    BaseNotificationsSubscribeHandler
):
    """ base class"""
    utility_interface = IProductionUpdatesPendingSubscriptionsUtility
    subscription_handler_utility = IProductionUpdatesNotificationsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.productionupdates_notification_subscriptions_url"  # noqa
    unsubscribe_base_url = "/unsubscribe/productionupdates"
    email_subject = _("Subscription to production updates")
    subscribe_email_message_template = (
        "productionupdates_notifications_subscribe_template.pt"
    )
