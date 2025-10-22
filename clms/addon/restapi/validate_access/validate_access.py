import logging
from plone.restapi.services import Service
from plone import api
from AccessControl.users import SpecialUser
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ValidateTokenAccess(Service):
    """Validate a token access"""

    def rsp(self, expires=None, code=400, valid=False, msg=""):
        """Prepare an (usually error) response"""
        self.request.response.setStatus(code)
        if expires is None:
            return {"valid": valid, "msg": msg}
        return {"valid": valid, "expires": expires, "msg": msg}

    def reply(self):
        """reply"""
        logger.info("ValidateTokenAccess called")

        if api.user.is_anonymous():
            logger.info("Anon user detected")
            return self.rsp(
                expires=None, code=401, valid=False, msg="Invalid token")

        try:
            current = api.user.get_current()
            logger.info(f"Current user: {current}")
        except Exception as e:
            logger.info(f"get_current failed: {e}")
            return self.rsp(
                expires=None, code=503, valid=False, msg="Unknown error")

        try:
            name = current.getId()
            logger.info(f"Resolved username: {name}")
        except Exception as e:
            logger.info(f"getId failed: {e}")
            return self.rsp(
                expires=None, code=503, valid=False, msg="Unknown error")

        if name == "Anonymous User" or isinstance(current, SpecialUser):
            logger.info(f"Invalid token for {name}")
            return self.rsp(
                expires=None, code=401, valid=False, msg="Invalid token")

        logger.info(f"Token valid for {name}")

        tokens = self.context.acl_users.token_auth._credential_storage[
            'access_tokens']

        user_id = name

        valid_tokens = []
        for k, t in tokens.items():
            logger.info(k)
            logger.info(t)
            if t.get("user_id") == user_id:
                issued = t["issued"]
                expires_in = t["expires_in"]
                expires_at = issued + timedelta(seconds=expires_in)
                if expires_at > datetime.now():
                    valid_tokens.append(t)

        token_data = None
        if valid_tokens:
            token_data = max(valid_tokens, key=lambda x: x["issued"])

        # {'key_id': '68a770021b510e078e191235f6asdasdasd',
        # 'user_id': 'userhere',
        # 'issued': datetime.datetime(2025, 10, 21, 15, 57, 8, 19218),
        # 'expires_in': 3600
        # }
        expires_str = ""
        if token_data is not None:
            try:
                issued = token_data.get("issued")
                expires_in = token_data.get("expires_in")
                expires_at = issued + timedelta(seconds=expires_in)
                expires_str = expires_at.isoformat()  # "2025-10-09T12:00:00Z"
            except Exception:
                logger.info("Error expires in.")

        return self.rsp(
            expires=expires_str, code=200, valid=True, msg="Token is valid")
