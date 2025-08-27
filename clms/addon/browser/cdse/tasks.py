"""Admin view to list ALL/CDSE download tasks."""

from Products.Five import BrowserView
from zope.component import getUtility
from clms.downloadtool.utility import IDownloadToolUtility
from datetime import datetime
import json
import logging
import transaction


logger = logging.getLogger("clms.addon")


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


class CDSEDownloadsView(BrowserView):
    """Show ALL/CDSE download requests"""

    def __call__(self):
        """
        See all tasks, not only CDSE:
        http://localhost:8080/Plone/en/cdse-status-tasks?options=ALL

        Remove all CDSE tasks
        ...:8080/Plone/en/cdse-status-tasks?options=DELETE-CDSE&token=20250827
        """

        options = self.request.form.get("options", 'CDSE')  # or ALL

        if options == "DELETE-CDSE":
            token = self.request.form.get('token', None)
            today_str = datetime.today().strftime("%Y%m%d")
            if token is None:
                return "Missing token. Add &token=YYYYMMDD"
            elif token == today_str:
                self.remove_cdse_tasks()
                return "REMOVED ALL CDSE download tasks."
            else:
                return "Invalid token. Use &token=YYYYMMDD"

        utility = getUtility(IDownloadToolUtility)
        data = utility.datarequest_inspect()
        cdse_tasks = [task for task in data if task.get(
            'cdse_task_role', None) is not None]
        self.request.response.setHeader(
            'Content-Type', 'text/html; charset=utf-8')

        html = ["<h1>Download Requests</h1>", "<pre>"]
        if options == "ALL":
            html.append(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            html.append(json.dumps(cdse_tasks, indent=2, ensure_ascii=False))
        html.append("</pre>")

        return "\n".join(html)

    def remove_cdse_tasks(self):
        utility = getUtility(IDownloadToolUtility)

        logger.info("Get downloads tasks list...")
        tasks = utility.datarequest_inspect()

        logger.info("Search for CDSE tasks...")
        cdse_tasks = [
            task for task in tasks if task.get(
                'cdse_task_role', None) is not None]

        logger.info(f"FOUND {len(cdse_tasks)} CDSE download tasks.")

        cdse_task_ids = []
        for task in cdse_tasks:
            task_id = task.get("TaskId", "Unknown TaskId")
            cdse_task_ids.append(task_id)

        remove_all_cdse_tasks(cdse_task_ids)
        logger.info("REMOVED ALL CDSE download tasks.")
