"""Admin view to list all CDSE download tasks."""

from Products.Five import BrowserView
from zope.component import getUtility
from clms.downloadtool.utility import IDownloadToolUtility
import json


class CDSEDownloadsView(BrowserView):
    """Show all CDSE download requests"""

    def __call__(self):
        utility = getUtility(IDownloadToolUtility)
        data = utility.datarequest_inspect()
        only_cdse_tasks = [task for task in data if task.get(
            'cdse_task_role', None) is not None]
        self.request.response.setHeader(
            'Content-Type', 'text/html; charset=utf-8')

        html = ["<h1>Download Requests</h1>", "<pre>"]
        html.append(json.dumps(only_cdse_tasks, indent=2, ensure_ascii=False))
        html.append("</pre>")

        return "\n".join(html)
