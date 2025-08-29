"""CDSE Batch Status Monitor.
   A view to trigger status check of downloads from CDSE.
   It uses a token saved as ENV VAR.
"""

from plone import api
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
    'FINISHED_OK': 'Finished_ok',
    'CREATED': 'Queued',
    'ANALYSIS': 'Queued',
    'ANALYSIS_DONE': 'Queued',
    'PROCESSING': 'In progress',
    'DONE': 'Finished_ok',
    'FAILED': 'Rejected',
    'STOPPED': 'Cancelled'
}


def get_cdse_monitor_view_token():
    """The token that protects the view"""
    if 'localhost' in api.portal.get().absolute_url():
        return "test-cdse"  # DEBUG

    return get_env_var(CDSE_MONITOR_VIEW_TOKEN_ENV_VAR)
    # http://localhost:8080/Plone/en/cdse-status-monitor?token=test-cdse


def get_old_status(batch_id, child_tasks):
    """ Return the current status of a CDSE task having the batch_id
    """
    filtered = [task for task in child_tasks if task.get(
        'CDSEBatchID', None) == batch_id]
    if len(filtered) > 0:
        return filtered[0].get('Status', '')

    return STATUS_MISSING


def get_task_id(batch_id, child_tasks):
    """ Return the task id of a CDSE task having the batch_id
    """
    filtered = [task for task in child_tasks if task.get(
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

    def get_cdse_tasks_from_downloadtool(self, utility):
        """Get current situation of CDSE tasks in downloadtool"""
        utility = getUtility(IDownloadToolUtility)

        logger.info("Get downloads tasks list...")
        tasks = utility.datarequest_inspect()

        cdse_tasks = [
            task for task in tasks if task.get(
                'cdse_task_role', None) is not None]

        parent_tasks = [task for task in cdse_tasks if task.get(
            'cdse_task_role', '') == 'parent']

        child_tasks = [task for task in cdse_tasks if task.get(
            'cdse_task_role', '') == 'child']

        logger.info(f"FOUND {len(cdse_tasks)} CDSE download tasks.")
        logger.info(f"--> {len(parent_tasks)} parent tasks.")
        logger.info(f"--> {len(child_tasks)} child tasks.")

        cdse_task_ids = []
        for task in cdse_tasks:
            task_id = task.get("TaskId", "Unknown TaskId")
            cdse_task_ids.append(task_id)

        batch_ids = [task['CDSEBatchID'] for task in child_tasks]

        return [
            cdse_tasks, parent_tasks, child_tasks, batch_ids]

    def get_tasks_status_from_cdse(self, batch_ids):
        """Check status in CDSE"""
        config = get_portal_config()
        token = get_token()
        cdse_status = {
            batch_id: get_status(token, config['batch_url'], batch_id)[
                batch_id]
            for batch_id in batch_ids
        }
        return cdse_status

    def update_child_tasks(self, child_tasks, batch_ids, cdse_status, utility):
        """ Update status of each child task if it is changed in CDSE
        """
        logger.info("Update child tasks status...")
        number_updated = 0
        for batch_id in batch_ids:
            new_status = cdse_status[batch_id]['status']
            message = cdse_status[batch_id]['error']
            old_status = get_old_status(batch_id, child_tasks)

            if new_status != old_status:
                task_id = get_task_id(batch_id, child_tasks)
                number_updated += 1
                utility.datarequest_status_patch(
                    {'Status': new_status, 'Message': message}, task_id)
                logger.info(f"{task_id} UPDATED CHILD: {new_status}")

                transaction.commit()  # really needed?
        logger.info(f"Done. {number_updated} child tasks updated.")

    def update_parent_tasks(self, parent_tasks, child_tasks, utility):
        """ Update status of parent tasks
        """
        logger.info("Update parent tasks status...")
        number_updated = 0
        for task in parent_tasks:
            group_id = task['cdse_task_group_id']
            child_tasks_group = [
                t for t in child_tasks if t['cdse_task_group_id'] == group_id]

            status_result = analyze_tasks_group(child_tasks_group)
            updated_status = status_result['final_status']
            updated_message = status_result['message']

            if updated_status is not None:
                old_status = task.get('Status', None)
                task_id = task['TaskId']
                new_status = FME_STATUS[updated_status]
                already_sent = task.get('FMETaskId', None)

                need_status_change = True
                if task.get('FinalizationDateTime', None) is not None:
                    need_status_change = False
                if already_sent:
                    need_status_change = False

                need_finalization_date = False
                if updated_status == STATUS_REJECTED:
                    need_finalization_date = True

                if need_status_change:
                    if need_finalization_date:
                        now = datetime.utcnow().isoformat()
                        utility.datarequest_status_patch(
                            {'Status': new_status,
                             'Message': updated_message,
                             'FinalizationDateTime': now
                             }, task_id
                        )
                    else:
                        utility.datarequest_status_patch(
                            {'Status': new_status,
                             'Message': updated_message,
                             }, task_id
                        )
                    number_updated += 1
                    logger.info(f"{task_id} UPDATED PARENT: {new_status}")
                    transaction.commit()  # really needed?

                if updated_status == STATUS_FINISHED and not already_sent:
                    logger.info("Send task to FME...")
                    fme_result = send_task_to_fme(task_id)
                    logger.info(fme_result)
                    utility.datarequest_status_patch(
                        {
                            'Status': FME_STATUS['CREATED']
                        }, task_id
                    )
                    transaction.commit()  # really needed?
        logger.info(f"Done. {number_updated} parent tasks updated.")

    def check_cdse_status(self):
        """Check the status for CDSE tasks"""
        utility = getUtility(IDownloadToolUtility)
        (
            cdse_tasks,
            parent_tasks,
            child_tasks,
            batch_ids
        ) = self.get_cdse_tasks_from_downloadtool(utility)

        cdse_status = self.get_tasks_status_from_cdse(batch_ids)

        self.update_child_tasks(child_tasks, batch_ids, cdse_status, utility)

        self.update_parent_tasks(parent_tasks, child_tasks, utility)

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
