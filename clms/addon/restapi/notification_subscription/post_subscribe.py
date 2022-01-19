"""
REST API information for notification subscriptions
"""
# -*- coding: utf-8 -*-

from email.mime.text import MIMEText
from smtplib import SMTPException

from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import alsoProvides

from clms.addon import _
from clms.addon.utilities.event_notifications_utility import \
    IEventPendingSubscriptionsUtility
from clms.addon.utilities.newsitem_notifications_utility import \
    INewsItemPendingSubscriptionsUtility
from clms.addon.utilities.newsletter_utility import \
    INewsLetterPendingSubscriptionsUtility


class BaseNotificationsSubscribeHandler(Service):
    """ base class for the notification subscriptions """

    @property
    def utility_interface(self):
        """ utility to save the actual subscription request """
        raise NotImplementedError(
            "You need to define the interface in your class"
        )

    @property
    def registry_key_for_base_url(self):
        """ the registry key for the confirmation url """
        raise NotImplementedError("You need to define the key in your class")

    @property
    def email_subject(self):
        """ return the email subject """
        raise NotImplementedError(
            "You need to define the subject in your class"
        )

    def email_message(self, url, portal_title):
        """ return the email message """
        raise NotImplementedError(
            "You need to define the message in your class"
        )

    def reply(self):
        """ return the real response """
        alsoProvides(self.request, IDisableCSRFProtection)
        body = json_body(self.request)
        email = body.get("email")
        if email is not None:
            utility = getUtility(self.utility_interface)
            key = utility.create_pending_subscription(email)
            status = self.send_confirmation_email(email, key)
            if status:
                self.request.response.setStatus(204)
                return

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
        frontend_domain = api.portal.get_registry_record(
            "volto.frontend_domain"
        )
        if frontend_domain.endswith("/"):
            frontend_domain = frontend_domain[:-1]
        url = frontend_domain + url + "/" + key

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        from_address = mail_settings.email_from_address
        encoding = registry.get("plone.email_charset", "utf-8")
        host = api.portal.get_tool("MailHost")
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False
        )
        portal_title = site_settings.site_title
        subject = self.email_subject
        message = self.email_message(url, portal_title)

        message = MIMEText(message, "plain", encoding)
        message["Reply-To"] = from_address
        try:
            host.send(
                message.as_string(),
                email,
                from_address,
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
    """News Item implementation """

    utility_interface = INewsItemPendingSubscriptionsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.newsitem_notification_subscriptions_url"  # noqa
    email_subject = _("News item notification subscription")

    def email_message(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " subscribe to receive notifications about new news items from"
                " the ${portal_title} website. Please visit the following URL"
                " to confirm your subscription: ${url}.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )


class EventNotificationsSubscribe(BaseNotificationsSubscribeHandler):
    """ base class """

    utility_interface = IEventPendingSubscriptionsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.event_notification_subscriptions_url"  # noqa
    email_subject = _("Event notification subscription")

    def email_message(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " subscribe to receive notifications about new events from"
                " the ${portal_title} website. Please visit the following URL"
                " to confirm your subscription: ${url}.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )


class NewsLetterNotificationsSubscribe(BaseNotificationsSubscribeHandler):
    """ base class """

    utility_interface = INewsLetterPendingSubscriptionsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.newsletter_notification_subscriptions_url"  # noqa
    email_subject = _("Newsletter notification subscription")

    def email_message(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " subscribe to receive the newsletter from"
                " the ${portal_title} website. Please visit the following URL"
                " to confirm your subscription: ${url}.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )
