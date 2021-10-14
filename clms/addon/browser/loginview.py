"""
Override OIDC PAS Plugin redirect url
"""
from pas.plugins.oidc.browser.view import CallbackView as BaseCallbackView


class CallbackView(BaseCallbackView):
    def __call__(self):
        """
        Override redirect url
        """
        _ = super().__call__()
        return self.request.response.redirect("/", status=302)
