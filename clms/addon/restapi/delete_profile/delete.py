""" REST API endpoint to delete user profile information"""
# -*- coding: utf-8 -*-
from logging import getLogger
from clms.downloadtool.utility import IDownloadToolUtility

from plone import api
from plone.restapi.services import Service
from zope.component import getUtility

from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
)
from clms.addon.utilities.newsletter_utility import (
    INewsLetterNotificationsUtility,
)

subscription_utilities = [
    INewsItemNotificationsUtility,
    IEventNotificationsUtility,
    INewsLetterNotificationsUtility,
]


class DeleteUserProfile(Service):
    """REST API endpoint class"""

    def reply(self):
        """implementaion of the endpoint"""
        if api.user.is_anonymous():
            self.request.response.setStatus(401)
            return None

        current_user = api.user.get_current()
        if "Manager" in api.user.get_roles(user=current_user):
            self.request.response.setStatus(400)

            return {
                "status": "error",
                "message": (
                    "You have specific Manager permissions. Please ask a"
                    " Manager to delete and close your account."
                ),
            }

        with api.env.adopt_roles(["Manager"]):
            self.remove_all_subscriptions(current_user.getProperty("email"))
            self.remove_all_downloads_information()
            api.user.delete(user=current_user)
            return self.reply_no_content()

    def remove_all_subscriptions(self, email):
        """remove all email subscriptions for the given email"""
        log = getLogger(__name__)
        for utility_interface in subscription_utilities:
            utility = getUtility(utility_interface)
            if utility.is_subscribed(email):
                result = utility.unsubscribe_address(email)
                if result:
                    log.info("User unsubscribed: %s %s", email, utility)
                else:
                    log.info(
                        "User was not unsubscribed: %s %s", email, utility
                    )
            else:
                log.info("User not suscribed: %s %s", email, utility)

        return 1

    def remove_all_downloads_information(self):
        """ remove all the downloads created by the current user"""
        log = getLogger(__name__)
        utility = getUtility(IDownloadToolUtility)
        user = api.user.get_current()
        user_id = user.getId()
        downloads = utility.datarequest_search(user_id, None)
        for key in downloads.keys():
            utility.datarequest_remove_task(key)
            log.info('Download request deleted: %s', key)
