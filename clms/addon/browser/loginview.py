"""
Override OIDC PAS Plugin redirect url
"""
from pas.plugins.oidc.browser.view import CallbackView as BaseCallbackView
from plone import api
from DateTime import DateTime


class CallbackView(BaseCallbackView):
    """ Callback view """

    def return_url(self, session):
        """
            We need to check several things here:

            - First of all we need to login the user in the membership tool
              so that last_login_time is updated.

            - If this is the first time that the user logs in, redirect to the
                /profile url to let her fill the profile form

            - If the user comes from a given url (came_from=whatever), check if
                that url is a url in the portal, and if so redirect here there.

            - If everything else fails, redirect to the home page.
        """

        super_url = super().return_url(session)

        member = api.user.get_current()
        login_time = member.getProperty("login_time", "2000/01/01")
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        is_initial_login = login_time == DateTime("2000/01/01")

        membership_tool = api.portal.get_tool("portal_membership")
        membership_tool.loginUser(self.request)
        if is_initial_login:
            return '/en/profile'

        return super_url
