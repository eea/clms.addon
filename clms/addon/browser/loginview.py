"""
Override OIDC PAS Plugin redirect url
"""
from pas.plugins.oidc.browser.view import CallbackView as BaseCallbackView
from pas.plugins.oidc.browser.view import Session
from plone import api
from DateTime import DateTime


class CallbackView(BaseCallbackView):
    """ Callback view """

    def __call__(self):
        """
        We need to check several things here:

        - If this is the first time that the user logs in, redirect to the
            /profile url to let her fill the profile form

        - If the user comes from a given url (came_from=whatever), check if
            that url is a url in the portal, and if so redirect here there.

        - If everything else fails, redirect to the home page.

        """
        _ = super().__call__()

        member = api.user.get_current()
        login_time = member.getProperty("login_time", "2000/01/01")
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        is_initial_login = login_time == DateTime("2000/01/01")

        membership_tool = api.portal.get_tool("portal_membership")
        membership_tool.loginUser(self.request)
        if is_initial_login:
            return self.request.response.redirect("/profile", status=302)

        session = Session(
            self.request,
            use_session_data_manager=self.context.use_session_data_manager,
        )
        return self.request.response.redirect(self.return_url(session=session))
