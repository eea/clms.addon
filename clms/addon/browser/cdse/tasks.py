"""Admin view to list ALL/CDSE download tasks."""

from Products.Five import BrowserView
from zope.component import getUtility
from clms.downloadtool.utility import IDownloadToolUtility
from clms.downloadtool.asyncjobs.queues import queue_job
from datetime import datetime
import json
import logging
import transaction


logger = logging.getLogger("clms.addon")


def remove_task(task_id):
    """ Delete a task from downloadtool
    """
    queue_job("downloadtool_jobs", "downloadtool_updates", {
        'operation': 'datarequest_remove_task',
        'updates': task_id
    })
    logger.info(f"Task will be removed: {task_id}")


def remove_tasks_from_downloadtool(task_ids):
    """ Remove a list of tasks from downloadtool
    """
    for task_id in task_ids:
        remove_task(task_id)


class CDSEDownloadsView(BrowserView):
    """Show ALL/CDSE download requests"""

    def __call__(self):
        """
        See all tasks, not only CDSE:
        http://localhost:8080/Plone/en/cdse-status-tasks?options=ALL

        Remove all CDSE tasks
        ...:8080/Plone/en/cdse-status-tasks?options=DELETE-CDSE&token=20250827

        Remove all tasks (not only CDSE) before given date
        ...?options=DELETE-ALL-TASKS-BEFORE&date_to=20240101&token=20250902
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

        if options == "DELETE-ALL-TASKS-BEFORE":
            token = self.request.form.get('token', None)
            date_to = self.request.form.get('date_to', None)
            today_str = datetime.today().strftime("%Y%m%d")
            if date_to is None:
                return "Missing date_to parameter. Add &date_to=YYYYMMDD"
            if token is None:
                return "Missing token. Add &token=YYYYMMDD"
            elif token == today_str:
                self.remove_tasks_before(date_to)
                return "REMOVED ALL download tasks before given date."
            else:
                return "Invalid token. Use &token=YYYYMMDD"

        utility = getUtility(IDownloadToolUtility)
        data = utility.datarequest_inspect()
        cdse_tasks = [task for task in data if task.get(
            'cdse_task_role', None) is not None]

        if options == "ALL":
            results = data
        else:
            results = cdse_tasks

        if options == "FILTER":
            date_filter = self.request.form.get('date', None)
            filter_date = datetime.strptime(date_filter, "%Y%m%d").date()
            if date_filter is None:
                return "Missing date. Add &date=YYYYMMDD"
            filtered_tasks = []
            for task in cdse_tasks:
                reg_time = task.get("RegistrationDateTime")
                if reg_time:
                    reg_dt = datetime.fromisoformat(
                        reg_time.replace("Z", "+00:00")).date()
                    if reg_dt == filter_date:
                        filtered_tasks.append(task)
            results = filtered_tasks

        self.request.response.setHeader(
            'Content-Type', 'text/html; charset=utf-8')

        html = ["<h1>Download Requests</h1>", "<pre>"]
        html.append(json.dumps(results, indent=2, ensure_ascii=False))
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

        remove_tasks_from_downloadtool(cdse_task_ids)
        logger.info("REMOVED ALL CDSE download tasks.")

    def remove_tasks_before(self, date_to):
        """Remove all download tasks before given date"""
        utility = getUtility(IDownloadToolUtility)

        logger.info("Get downloads tasks list...")
        tasks = utility.datarequest_inspect()

        logger.info("Search for old tasks...")

        date_to_dt = datetime.strptime(date_to, "%Y%m%d")

        found = []
        for task in tasks:
            reg_time = task.get('RegistrationDateTime', None)
            if reg_time:
                registration_dt = datetime.fromisoformat(reg_time)
                if registration_dt.date() < date_to_dt.date():
                    found.append(task)

        logger.info(f"FOUND {len(found)} old download tasks.")

        task_ids = []
        for task in found:
            task_id = task.get("TaskId", "Unknown TaskId")
            task_ids.append(task_id)

        remove_tasks_from_downloadtool(task_ids)
        logger.info("REMOVED ALL old download tasks.")
