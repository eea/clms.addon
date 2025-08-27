"""CDSE Batch Status Monitor.
   A view to trigger status check of downloads from CDSE.
   It uses a token saved as ENV VAR.
"""

import logging
import transaction
from datetime import datetime
from Products.Five import BrowserView
from clms.addon.browser.cdse.config import CDSE_MONITOR_VIEW_TOKEN_ENV_VAR
from clms.addon.browser.cdse.utils import get_env_var
from clms.downloadtool.utility import IDownloadToolUtility
from clms.downloadtool.api.services.cdse.cdse_integration import (
    get_portal_config, get_status, get_token)
from clms.downloadtool.api.services.cdse.fme import send_task_to_fme
from zope.component import getUtility

logger = logging.getLogger("clms.addon")

# defined by CDSE
STATUS_REJECTED = 'REJECTED'
STATUS_QUEUED = 'QUEUED'
STATUS_FINISHED = 'FINISHED_OK'

# defined by us
STATUS_MISSING = 'MISSING'


FME_STATUS = {
    'REJECTED': 'Rejected',
    'FINISHED_OK': 'Finished_ok'
}


def remove_task(task_id):
    """ Delete a task from downloadtool
    """
    utility = getUtility(IDownloadToolUtility)
    logger.info(f"Removing task {task_id}")
    utility.datarequest_remove_task(task_id)


def remove_all_cdse_tasks(task_ids):
    """ Remove all CDSE tasks from downloadtool
    """
    for task_id in task_ids:
        remove_task(task_id)

    transaction.commit()  # else the changes are not saved (why?)


def get_cdse_monitor_view_token():
    """The token that protects the view"""
    return get_env_var(CDSE_MONITOR_VIEW_TOKEN_ENV_VAR)

    # return "test-cdse"  # DEBUG --
    # http://localhost:8080/Plone/en/cdse-status-monitor?token=test-cdse


def get_old_status(batch_id, cdse_tasks):
    """ Return the current status of a CDSE task having the batch_id
    """
    filtered = [task for task in cdse_tasks if task.get(
        'CDSEBatchID', None) == batch_id]
    if len(filtered) > 0:
        return filtered[0].get('Status', '')

    return STATUS_MISSING


def get_task_id(batch_id, cdse_tasks):
    """ Return the current status of a CDSE task having the batch_id
    """
    filtered = [task for task in cdse_tasks if task.get(
        'CDSEBatchID', None) == batch_id]
    if len(filtered) > 0:
        return filtered[0].get('TaskId', None)

    return None


def analyze_tasks_group(child_tasks):
    """ Analyze current status of a group of CDSE tasks, return a status for
        parent task
    """
    status_list = [child.get('Status', '') for child in child_tasks]

    if STATUS_REJECTED in status_list:
        count = 0
        for status in status_list:
            if STATUS_REJECTED == status:
                count += 1
        result = {
            'final_status': STATUS_REJECTED,
            'message': f'{count}/{len(status_list)} tasks rejected by CDSE.'
        }
        return result

    if STATUS_FINISHED in status_list:
        count = 0
        for status in status_list:
            if STATUS_FINISHED == status:
                count += 1

        if count == len(status_list):
            result = {
                'final_status': STATUS_FINISHED,
                'message': f'{count}/{len(status_list)} CDSE tasks finished.'
            }
        return result

    return {
        'final_status': None,
        'message': None
    }


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

        cdse_task_ids = []
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
            cdse_task_ids.append(task_id)

        # remove_all_cdse_tasks(cdse_task_ids)

        cdse_batch_ids = [task['CDSEBatchID'] for task in cdse_child_tasks]
        logger.info("Tasks to be verified: ")
        for task in cdse_batch_ids:
            logger.info(task)

        logger.info("DONE checking CDSE tasks in downloadtool.")

        logger.info("Check status in CDSE:")
        config = get_portal_config()
        token = get_token()
        all_batches_status = get_status(token, config['batch_url'])
        for batch_id, info in all_batches_status.items():
            logger.info(
                f"{batch_id}: {info['original_status']} -> {info['status']}")

        logger.info("START updating tasks in downloadtool...")
        for batch_id in cdse_batch_ids:
            new_status = all_batches_status[batch_id]['status']
            message = all_batches_status[batch_id]['error']
            old_status = get_old_status(batch_id, cdse_tasks)

            if new_status != old_status:
                task_id = get_task_id(batch_id, cdse_tasks)
                utility.datarequest_status_patch(
                    {'Status': new_status, 'Message': message}, task_id)
                logger.info(f"{task_id} UPDATED STATUS: {new_status}")

                transaction.commit()  # really needed?

        logger.info("Check parent tasks...")
        for task in cdse_parent_tasks:
            group_id = task['cdse_task_group_id']
            child_tasks = [
                t for t in cdse_child_tasks if t['cdse_task_group_id'] == group_id]

            status_result = analyze_tasks_group(child_tasks)

            if status_result['final_status'] is not None:
                old_parent_status = task.get('Status', None)
                parent_task_id = task['TaskId']
                new_status = FME_STATUS[status_result['final_status']]
                utility.datarequest_status_patch(
                    {'Status': new_status,
                     'Message': status_result['message'],
                     'FinalizationDateTime': datetime.utcnow().isoformat()
                     }, parent_task_id
                )
                logger.info(f"{parent_task_id} UPDATED PARENT: {new_status}")
                transaction.commit()  # really needed?

                if new_status != old_parent_status:
                    if new_status == STATUS_FINISHED:
                        # WIP ? how to prevent re-sending task to FME
                        logger.info("Send task to FME...")
                        fme_result = send_task_to_fme(parent_task_id)
                        logger.info(fme_result)

        # WIP clear children?
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
