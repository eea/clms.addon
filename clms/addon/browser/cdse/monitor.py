"""CDSE Batch Status Monitor.
   A view to trigger status check of downloads from CDSE.
   It uses a token saved as ENV VAR."""

import logging
from Products.Five import BrowserView
from clms.addon.browser.cdse.config import CDSE_MONITOR_VIEW_TOKEN_ENV_VAR
from clms.addon.browser.cdse.utils import get_env_var
from clms.downloadtool.utility import IDownloadToolUtility
from zope.component import getUtility

logger = logging.getLogger("clms.addon")


def get_cdse_monitor_view_token():
    """The token that protects the view"""
    return get_env_var(CDSE_MONITOR_VIEW_TOKEN_ENV_VAR)

    # return "test-cdse"  # DEBUG --
    # http://localhost:8080/Plone/en/cdse-status-monitor?token=test-cdse


class CDSEBatchStatusMonitor(BrowserView):
    """ Check status of CDSE downloads """

    def check_cdse_status(self):
        """ Check the status for CDSE tasks """
        utility = getUtility(IDownloadToolUtility)

        logger.info(f"START: Get downloads list...")
        tasks = utility.datarequest_inspect()
        logger.info(f"END: Get downloads list...")

        logger.info(f"START: Filter by dataset source...")
        filtered = [
            t for t in tasks
            if any(
                ds.get("DatasetSource") == "CDSE" for ds in t.get(
                    "Datasets", []))
        ]
        logger.info(f"END: Filter by dataset source...")

        logger.info(f"FOUND {len(filtered)} CDSE download requests.")

        for task in filtered:
            user = task.get('UserID', 'Unknown user')
            task_id = task.get('TaskId', 'Unknown TaskId')
            fme_task_id = task.get('FMETaskId', 'Unknown FMETaskId')
            status = task.get('Status', 'Unknown Status')

            datasets = task.get('Datasets', [])
            if datasets:
                for dataset in datasets:
                    dataset_title = dataset.get('DatasetTitle', 'Unknown')
                    dataset_id = dataset.get('DatasetID', 'Unknown DatasetID')
                    logger.info(
                        f"Task {task_id} (FMEID {fme_task_id}) for user {user} "
                        f"has status '{status}'. Dataset: '{dataset_title}' "
                        f"(ID {dataset_id})."
                    )
            else:
                logger.info(f"Task {task_id} (FME {fme_task_id}) is empty.")

            if status == "Cancelled":
                logger.info("Nothing to do for this task.")
            else:
                logger.info("WIP Check CDSE status, update in download tool.")

                # CDSE status check
                # Updates in download tool.

        logger.info("DONE.")

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
