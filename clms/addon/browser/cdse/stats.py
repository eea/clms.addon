"""Admin view to list all downloads stats (with all details for CDSE tasks).

Example of task in statstool
{'Dataset': ['70903c20fc2a4a...'],
 'End': '2025-07-15T13:14:27.631333',
 'Start': '2025-07-15T13:14:12.553921',
 'Status': 'Finished_ok',
 'TaskID': '4204...',
 'TransformationData': {'Datasets': [{'DatasetFormat': 'GPKG',
                                      'DatasetID': '70903c20f...',
                                      'DatasetPath': 'SDpcV...lVUUzM=',
                                      'DatasetSource': 'EEA',
                                      'DatasetTitle': 'Urban Atlas Land '
                                                      'Cover/Land Use 2018 '
                                                      '(vector), Europe, '
                                                      '6-yearly',
                                      'Metadata': ['https://sdi.e...ved=true'],
                                      'NUTSID': 'DE712',
                                      'NUTSName': 'DE712',
                                      'OutputFormat': 'GPKG',
                                      'OutputGCS': 'EPSG:3035',
                                      'WekeoChoices': ''}]},
 'TransformationDuration': '',
 'TransformationResultData': '',
 'TransformationSize': 5173388,
 'User': 'someoneredacted',
 'item_registration_date': '2025-07-15',
 'item_registration_datetime': '2025-07-15T13:14:12.682576',
 'item_update_date': '2025-07-15',
 'item_update_datetime': '2025-07-15T13:14:27.631580',
 'user_affiliation': 'Research and education organisations (other users)',
 'user_country': 'Romania',
 'user_sector_of_activity': 'Policy support - support to EU policy or EU '
                            'national or regional policy',
 'user_thematic_activity': 'Land (includes e.g. land use, land cover, regional '
                           'and urban policies, soils, inland water, '
                           'agriculture, forestry, GHG emissions, '
                           'biodiversity, plant health, cultural heritage)'}
"""

from Products.Five import BrowserView
from zope.component import getUtility
from clms.statstool.utility import IDownloadStatsUtility
from datetime import datetime
import json
import logging
import transaction


logger = logging.getLogger("clms.addon")


def remove_task(task_id):
    """ Delete a task from statstool
    """
    utility = getUtility(IDownloadStatsUtility)
    logger.info(f"Removing task {task_id}")
    utility.delete_item(task_id)


def remove_tasks_from_statstool(task_ids):
    """ Remove a list of tasks from statstool
    """
    for task_id in task_ids:
        remove_task(task_id)

    transaction.commit()  # else the changes are not saved (why?)


class CDSEStatsView(BrowserView):
    """Show all stats without filters"""

    def __call__(self):
        utility = getUtility(IDownloadStatsUtility)

        options = self.request.form.get("options", '')
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
                return "REMOVED ALL tasks before given date from stats."
            else:
                return "Invalid token. Use &token=YYYYMMDD"

        soup = utility.get_soup()
        data = [dict(x.attrs) for x in soup.data.values()]

        self.request.response.setHeader(
            'Content-Type', 'text/html; charset=utf-8')

        html = ["<h1>Download statistics</h1>", "<pre>"]
        html.append(json.dumps(data, indent=2, ensure_ascii=False))
        html.append("</pre>")

        return "\n".join(html)

    def remove_tasks_before(self, date_to):
        """Remove all download tasks before given date"""
        utility = getUtility(IDownloadStatsUtility)

        logger.info("Get downloads tasks list...")
        soup = utility.get_soup()
        tasks = [dict(x.attrs) for x in soup.data.values()]

        logger.info("Search for old tasks...")

        date_to_dt = datetime.strptime(date_to, "%Y%m%d")

        found = []
        for task in tasks:
            reg_time = task.get('item_registration_datetime', None)
            if reg_time:
                registration_dt = datetime.fromisoformat(reg_time)
                if registration_dt.date() < date_to_dt.date():
                    found.append(task)

        logger.info(f"FOUND {len(found)} old download tasks.")

        task_ids = []
        for task in found:
            task_id = task.get("TaskId", None)
            if task_id is None:
                task_id = task.get("TaskID", "Unknown TaskId")
            task_ids.append(task_id)

        remove_tasks_from_statstool(task_ids)
        logger.info("REMOVED ALL old download tasks.")
