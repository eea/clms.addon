"""
Override OIDC PAS Plugin redirect url
"""
import base64
from logging import getLogger
from urllib.parse import urlparse

from clms.addon.utils import add_url_params
from DateTime import DateTime
from pas.plugins.oidc.browser.view import CallbackView as BaseCallbackView
from pas.plugins.oidc.browser.view import LoginView as BaseLoginView
from pas.plugins.oidc.browser.view import Session
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.PlonePAS.events import UserInitialLoginInEvent, UserLoggedInEvent
from zope import event
from zope.interface import alsoProvides


class CallbackView(BaseCallbackView):
    """Callback view"""

    def __call__(self):
        """custom __call__ method"""
        try:
            return super().__call__()
        except Exception as e:
            log = getLogger(__name__)
            log.info("There was an error handling the login process")
            log.exception(e)
            self.request.response.setHeader(
                "Cache-Control", "no-cache, must-revalidate"
            )
            api.portal.show_message(
                "There was an error connecting with the EU Login service. It"
                " may be out of service. Please try again after some minutes.",
                request=self.request,
                type="error",
            )
            return self.request.response.redirect("/")

    # pylint: disable=dangerous-default-value
    def return_url(self, session, userinfo={}, token=None):
        """Calculate the return url and update user properties"""
        redirect_url = "/"
        came_from = self.request.get("came_from")
        if not came_from and session:
            came_from = session.get("came_from")
            if not came_from.startswith("http"):
                # try to convert from base64
                try:
                    came_from = base64.standard_b64decode(came_from).decode(
                        "utf-8"
                    )
                except Exception as e:
                    log = getLogger(__name__)
                    log.info(e)

        portal_url = api.portal.get_tool("portal_url")

        if came_from:
            # pylint: disable=line-too-long
            if (came_from.startswith("http") and portal_url.isURLInPortal(came_from) or same_domain(portal_url(), came_from) or not came_from.startswith("http")):  # noqa: E501
                redirect_url = came_from

        new_url = self.update_user_data(userinfo)
        url = new_url or redirect_url
        new_came_from = add_url_params(url, {"access_token": token})

        return new_came_from

    def update_user_data(self, userinfo):
        """update user's properties"""
        with api.env.adopt_roles(["Manager"]):
            userid = userinfo.get("sub")
            if userid is not None:
                member = api.user.get(userid=userid)

                res = False
                default = DateTime("2000/01/01")
                login_time = member.getProperty("login_time", default)
                if login_time == default:
                    res = True
                    login_time = DateTime()
                member.setProperties(
                    login_time=self.context.ZopeTime(),
                    last_login_time=login_time,
                )

                if res:
                    event.notify(UserInitialLoginInEvent(member))
                else:
                    event.notify(UserLoggedInEvent(member))

                if res:
                    # Allow write-on-read to update user properties
                    # on first login
                    alsoProvides(self.request, IDisableCSRFProtection)
                    redirect_url = "/en/profile"
                    return redirect_url

        return None


class LoginView(BaseLoginView):
    """Override of Login view to avoid Timeout and other errors from EU Login
    services
    """

    def __call__(self):
        """custom __call__ method"""
        try:
            return super().__call__()
        except Exception as e:
            log = getLogger(__name__)
            log.info("There was an error handling the login process")
            log.exception(e)
            self.request.response.setHeader(
                "Cache-Control", "no-cache, must-revalidate"
            )
            return self.request.response.redirect("/")


class MyCallBack(BrowserView):
    """Custom callback view"""

    def __call__(self):
        """callback"""
        session = Session(
            self.request,
            use_session_data_manager=self.context.use_session_data_manager,
        )
        redirect_url = "/"
        # pylint: disable=too-many-nested-blocks
        if not api.user.is_anonymous():
            member = api.user.get_current()
            if member:
                login_time = member.getProperty("login_time", "2000/01/01")
                initial_login_time = member.getProperty(
                    "initial_login_time", "2000/01/01"
                )
                if not isinstance(login_time, DateTime):
                    login_time = DateTime(login_time)
                is_initial_login = login_time == DateTime(
                    "2000/01/01"
                ) or initial_login_time == DateTime("2000/01/01")

                membership_tool = api.portal.get_tool("portal_membership")
                membership_tool.loginUser(self.request)

                redirect_url = "/"

                if is_initial_login:
                    # Allow write-on-read to update user properties
                    # on first login
                    alsoProvides(self.request, IDisableCSRFProtection)
                    redirect_url = "/en/profile"
                    member.setMemberProperties(
                        mapping={
                            "initial_login_time": DateTime(),
                        }
                    )
                else:
                    came_from = self.request.get("came_from")
                    if not came_from and session:
                        came_from = session.get("came_from")
                        if not came_from.startswith("http"):
                            # try to convert from base64
                            try:
                                came_from = base64.standard_b64decode(
                                    came_from
                                ).decode("utf-8")
                            except Exception as e:
                                log = getLogger(__name__)
                                log.info(e)

                    portal_url = api.portal.get_tool("portal_url")

                    if came_from:
                        # pylint: disable=line-too-long
                        if (came_from.startswith("http") and portal_url.isURLInPortal(came_from) or same_domain(portal_url(), came_from) or not came_from.startswith("http")):  # noqa: E501
                            redirect_url = came_from

        else:
            came_from = self.request.get("came_from")
            if not came_from and session:
                came_from = session.get("came_from")
                if not came_from.startswith("http"):
                    # try to convert from base64
                    try:
                        came_from = base64.standard_b64decode(
                            came_from
                        ).decode("utf-8")
                    except Exception as e:
                        log = getLogger(__name__)
                        log.info(e)

        return self.request.response.redirect(redirect_url, status=302)


def same_domain(url1, url2):
    """detect whether both URLs are from the same domain. We need to check this
    because the URL when coming from EU Login has the /api prefix
    """
    if url1.startswith("http") and url2.startswith("http"):
        parsed_url1 = urlparse(url1)
        parsed_url2 = urlparse(url2)
        return parsed_url1.hostname == parsed_url2.hostname

    return False
