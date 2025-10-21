from plone.restapi.services import Service
from plone import api
from AccessControl.users import SpecialUser


class ValidateTokenAccess(Service):
    """Validate a token access"""

    def rsp(self, msg, code=400, status="error"):
        """Prepare an (usually error) response"""
        if code != 0:
            self.request.response.setStatus(code)
        return {"status": status, "msg": msg}

    def reply(self):
        """reply"""
        if api.user.is_anonymous():
            return self.rsp("Invalid token", code=401, status="error")

        try:
            current = api.user.get_current()
        except Exception:
            return self.rsp("Unknown error", code=502, status="error")

        print(current)
        try:
            name = current.name
        except Exception:
            return self.rsp("Unknown error", code=502, status="error")

        if name == "Anonymous User" or isinstance(current, SpecialUser):
            return self.rsp("Invalid token", code=401, status="error")
        else:
            return self.rsp("Token is valid", code=200, status="success")
