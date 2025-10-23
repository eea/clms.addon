import logging
from plone.restapi.services import Service
from plone.protect.authenticator import createToken

logger = logging.getLogger(__name__)


class GetCSRFToken(Service):
    """Get a CSRF token to be used with custom forms"""

    def reply(self):
        """reply"""
        self.request.response.setHeader("Content-Type", "application/json")
        token = createToken()
        logger.info("CLMS GetCSRFToken")
        return {"token": token}
