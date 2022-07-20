"""
Override OIDC PAS Plugin redirect url
"""
from Products.Five.browser import BrowserView
from pas.plugins.oidc.browser.view import Session
from pas.plugins.oidc.browser.view import CallbackView as BaseCallbackView
from plone import api
from DateTime import DateTime
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class CallbackView(BaseCallbackView):
    """Callback view"""

    def return_url(self, session):
        """The return url will be a custom callback, this way
        the user will be logged in and we can check the last login time
        """
        return "{}/my-custom-callback".format(self.context.absolute_url())


class MyCallBack(BrowserView):
    """Custom callback view"""

    def __call__(self):
        """callback"""
        session = Session(
            self.request,
            use_session_data_manager=self.context.use_session_data_manager,
        )

        member = api.user.get_current()
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
            # Allow write-on-read to update user properties on first login
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

            portal_url = api.portal.get_tool("portal_url")

            if came_from:
                # pylint: disable=line-too-long
                if (
                    came_from.startswith("http")
                    and portal_url.isURLInPortal(came_from)
                    or not came_from.startswith("http")
                ):  # noqa: E501
                    redirect_url = came_from

        return self.request.response.redirect(redirect_url, status=302)
