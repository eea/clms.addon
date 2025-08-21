"""Admin view to list ALL/CDSE download tasks."""

from Products.Five import BrowserView
from zope.component import getUtility
from clms.downloadtool.utility import IDownloadToolUtility
import json


class CDSEDownloadsView(BrowserView):
    """Show ALL/CDSE download requests"""

    def __call__(self):
        # http://localhost:8080/Plone/en/cdse-status-tasks?options=ALL

        options = self.request.form.get("options", 'CDSE')  # or ALL

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
