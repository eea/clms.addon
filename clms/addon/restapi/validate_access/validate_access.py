import logging
from plone.restapi.services import Service
from plone import api
from AccessControl.users import SpecialUser

logger = logging.getLogger(__name__)


class ValidateTokenAccess(Service):
    """Validate a token access"""

    def rsp(self, msg, code=400, status="error"):
        """Prepare an (usually error) response"""
        if code != 0:
            self.request.response.setStatus(code)
        logger.info(f"RSP: {status} ({code}) - {msg}")
        return {"status": status, "msg": msg}

    def reply(self):
        """reply"""
        logger.info("ValidateTokenAccess called")

        if api.user.is_anonymous():
            logger.info("Anon user detected")
            return self.rsp("Invalid token", code=401, status="error")

        try:
            current = api.user.get_current()
            logger.info(f"Current user: {current}")
        except Exception as e:
            logger.info(f"get_current failed: {e}")
            return self.rsp("Unknown error", code=503, status="error")

        try:
            name = current.getId()
            logger.info(f"Resolved username: {name}")
        except Exception as e:
            logger.info(f"getId failed: {e}")
            return self.rsp("Unknown error", code=503, status="error")

        if name == "Anonymous User" or isinstance(current, SpecialUser):
            logger.info(f"Invalid token for {name}")
            return self.rsp("Invalid token", code=401, status="error")

        logger.info(f"Token valid for {name}")
        return self.rsp("Token is valid", code=200, status="success")
