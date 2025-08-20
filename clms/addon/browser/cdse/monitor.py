"""CDSE Batch Status Monitor.
   A view to trigger status check of downloads from CDSE.
   It uses a token saved as ENV VAR.
"""

import logging
from Products.Five import BrowserView
from clms.addon.browser.cdse.config import CDSE_MONITOR_VIEW_TOKEN_ENV_VAR
from clms.addon.browser.cdse.utils import get_env_var
from clms.downloadtool.utility import IDownloadToolUtility
from clms.downloadtool.api.services.cdse.cdse_integration import (
    get_portal_config, get_status, get_token)
from zope.component import getUtility

logger = logging.getLogger("clms.addon")


STATUS_REJECTED = 'REJECTED'
STATUS_QUEUED = 'QUEUED'
STATUS_FINISHED = 'FINISHED_OK'


def get_cdse_monitor_view_token():
    """The token that protects the view"""
    # return get_env_var(CDSE_MONITOR_VIEW_TOKEN_ENV_VAR)

    return "test-cdse"  # DEBUG --
    # http://localhost:8080/Plone/en/cdse-status-monitor?token=test-cdse


class CDSEBatchStatusMonitor(BrowserView):
    """Check status of CDSE downloads"""

    def check_cdse_status(self):
        """Check the status for CDSE tasks"""
        utility = getUtility(IDownloadToolUtility)

        logger.info("Get downloads tasks list...")
        tasks = utility.datarequest_inspect()

        logger.info("Search for CDSE tasks...")
        cdse_tasks = [
            task for task in tasks if task.get(
                'cdse_task_role', None) is not None]

        cdse_parent_tasks = [task for task in cdse_tasks if task.get(
            'cdse_task_role', '') == 'parent']

        cdse_child_tasks = [task for task in cdse_tasks if task.get(
            'cdse_task_role', '') == 'child']

        logger.info(f"FOUND {len(cdse_tasks)} CDSE download tasks.")
        logger.info(f"--> {len(cdse_parent_tasks)} parent tasks.")
        logger.info(f"--> {len(cdse_child_tasks)} child tasks.")

        for task in cdse_tasks:
            user = task.get("UserID", "Unknown user")
            task_id = task.get("TaskId", "Unknown TaskId")
            task_role = task.get("cdse_task_role", 'N/A')
            task_group = task.get("cdse_task_group_id", 'N/A')
            fme_task_id = task.get("FMETaskId", "N/A")
            status = task.get("Status", "N/A")

            logger.info(
                f"From: {user} > role: {task_role} -> group: {task_group} "
                f"task ID: {task_id} FME: {fme_task_id} status: {status}"
            )

        logger.info("DONE checking CDSE tasks in downloadtool.")

        logger.info("Check status in CDSE:")
        config = get_portal_config()
        token = get_token()
        all_batches_status = get_status(token, config['batch_url'])
        for batch_id, info in all_batches_status.items():
            logger.info(
                f"{batch_id}: {info['original_status']} -> {info['status']}")
        logger.info("DONE check status in CDSE.")

        logger.info("START updating tasks in downloadtool...")
        for batch_id, info in all_batches_status.items():
            if info['status'] == STATUS_REJECTED:
                logger.info("TODO delete rejected task.")
            if info['status'] == STATUS_QUEUED:
                logger.info("TODO update queued task.")
            if info['status'] == STATUS_FINISHED:
                logger.info("TODO update finished task. Also FME call.")
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
