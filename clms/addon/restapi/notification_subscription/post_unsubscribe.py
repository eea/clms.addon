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
from plone.restapi.services import Service, _no_content_marker
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import alsoProvides

from clms.addon import _
from clms.addon.utilities.event_notifications_utility import (
    IEventPendingUnSubscriptionsUtility, IEventNotificationsUtility
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemPendingUnSubscriptionsUtility, INewsItemNotificationsUtility
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterPendingUnSubscriptionsUtility, INewsLetterNotificationsUtility
)


class BaseNotificationsUnSubscribeHandler(Service):
    """ base class for the handlers"""

    @property
    def utility_interface(self):
        """ utility to save the actual unsubscription request """
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
        """ the key to get the base url from the registry """
        raise NotImplementedError("You need to define the key in your class")

    @property
    def email_subject(self):
        """ the subject of the email """
        raise NotImplementedError(
            "You need to define the subject in your class"
        )

    def email_message(self, url, portal_title):
        """ return the message to be sent """
        raise NotImplementedError(
            "You need to define the message in your class"
        )

    def email_message_not_subscribed(self, url, portal_title):
        """return the email message to be sent to the user when she is
        not subscribed
        """
        raise NotImplementedError(
            "You need to define the message in your class"
        )

    def reply(self):
        """ return the real response """
        alsoProvides(self.request, IDisableCSRFProtection)
        body = json_body(self.request)
        email = body.get("email")
        if email is not None:
            # pylint: disable=line-too-long
            subscription_utility = getUtility(self.subscription_handler_utility)  # noqa: E501
            if subscription_utility.is_subscribed(email):
                utility = getUtility(self.utility_interface)
                key = utility.create_pending_unsubscription(email)
                status = self.send_confirmation_email(email, key)
                if status:
                    self.request.response.setStatus(204)
                    return _no_content_marker

                self.request.response.setStatus(500)
                return {
                    "status": "error",
                    "message": (
                        "There was an error sending the email, try again "
                        "please"
                    ),
                }

            self.send_not_subscribed_email(email)
            self.request.response.setStatus(204)
            return _no_content_marker

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

        url = frontend_domain + "/en" + url + "/" + key

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
        message["From"] = from_address
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

    def send_not_subscribed_email(self, email):
        """send an email to the user stating that she is not subsribed"""
        registry = getUtility(IRegistry)
        url = registry.get(self.registry_key_for_base_url)

        frontend_domain = api.portal.get_registry_record(
            "volto.frontend_domain"
        )
        if frontend_domain.endswith("/"):
            frontend_domain = frontend_domain[:-1]

        url = frontend_domain + "/en" + url

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
        message = self.email_message_not_subscribed(url, portal_title)

        message = MIMEText(message, "plain", encoding)
        message["Reply-To"] = from_address
        message["From"] = from_address
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


class NewsItemNotificationsUnSubscribe(BaseNotificationsUnSubscribeHandler):
    """News Item implementation """

    utility_interface = INewsItemPendingUnSubscriptionsUtility
    subscription_handler_utility = INewsItemNotificationsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.newsitem_notification_unsubscriptions_url"  # noqa
    email_subject = _("News item notification unsubscription")

    def email_message(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " unsubscribe from receiving notifications about news items"
                " from the ${portal_title} website. Please visit the following"
                " URL to confirm your unsubscription: ${url}.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )

    def email_message_not_subscribed(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " unsubscribe from receiving notifications about news items"
                " from the ${portal_title} website at ${url}. We are glad to "
                " inform you that you are not subscribed to receive those "
                " notifications. This requires no additional action on your "
                " part.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )


class EventNotificationsUnSubscribe(BaseNotificationsUnSubscribeHandler):
    """ base class """

    utility_interface = IEventPendingUnSubscriptionsUtility
    subscription_handler_utility = IEventNotificationsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.event_notification_unsubscriptions_url"  # noqa
    email_subject = _("Event notification unsubscription")

    def email_message(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " unsubscribe from receiving notifications about events from"
                " the ${portal_title} website. Please visit the following URL"
                " to confirm your subscription: ${url}.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )

    def email_message_not_subscribed(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " unsubscribe from receiving notifications about events"
                " from the ${portal_title} website at ${url}. We are glad to "
                " inform you that you are not subscribed to receive those "
                " notifications. This requires no additional action on your "
                " part.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )


class NewsLetterNotificationsUnSubscribe(BaseNotificationsUnSubscribeHandler):
    """ base class """

    utility_interface = INewsLetterPendingUnSubscriptionsUtility
    subscription_handler_utility = INewsLetterNotificationsUtility
    # pylint: disable=line-too-long
    registry_key_for_base_url = "clms.addon.notifications_controlpanel.newsletter_notification_unsubscriptions_url"  # noqa
    email_subject = _("NewsLetter notification unsubscription")

    def email_message(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " unsubscribe from receiving the newsletter from"
                " the ${portal_title} website. Please visit the following URL"
                " to confirm your subscription: ${url}.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )

    def email_message_not_subscribed(self, url, portal_title):
        """ return the message """
        return translate(
            _(
                "You are receiving this email because you have requested to"
                " unsubscribe from receiving the newsletter "
                " from the ${portal_title} website at ${url}. We are glad to "
                " inform you that you are not subscribed to receive the "
                " newsletter. This requires no additional action on your "
                " part.",
                mapping={
                    "portal_title": portal_title,
                    "url": url,
                },
            )
        )
