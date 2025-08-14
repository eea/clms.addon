"""CDSE Batch Status Monitor.
   A view to trigger status check of downloads from CDSE.
   It uses a token saved as ENV VAR."""

import logging
from Products.Five import BrowserView
from clms.addon.browser.cdse.config import CDSE_MONITOR_VIEW_TOKEN_ENV_VAR
from clms.addon.browser.cdse.utils import get_env_var

logger = logging.getLogger("clms.addon")


def get_cdse_monitor_view_token():
    """The token that protects the view"""
    # return get_env_var(CDSE_MONITOR_VIEW_TOKEN_ENV_VAR)

    return "test-cdse"  # DEBUG
    # http://localhost:8080/Plone/en/cdse-status-monitor?token=test-cdse


class CDSEBatchStatusMonitor(BrowserView):
    """ Check status of CDSE downloads """

    def check_cdse_status(self):
        """ WIP """

        logger.info("WIP Check CDSE status")

        return "done"

    def __call__(self):
        cdse_view_token = get_cdse_monitor_view_token()

        if cdse_view_token is None:
            logger.info("CDSE Monitor Canceled: missing view token ENV.")
            return "missing env var"

        view_token = self.request.form.get("token", None)
        if view_token is None:
            logger.info("CDSE Monitor Canceled: missing view token.")
            return "missing view token"

        if view_token != cdse_view_token:
            logger.info("CDSE Monitor Canceled: invalid view token.")
            return "invalid view token"

        self.check_cdse_status()
        return "ok"
