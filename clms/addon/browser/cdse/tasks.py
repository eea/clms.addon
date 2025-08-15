"""Admin view to list all download tasks (with all details for CDSE tasks)."""

from Products.Five import BrowserView
from zope.component import getUtility
from clms.downloadtool.utility import IDownloadToolUtility
import json


class CDSEDownloadsView(BrowserView):
    """Show all download requests without filters"""

    def __call__(self):
        utility = getUtility(IDownloadToolUtility)
        data = utility.datarequest_inspect()
        self.request.response.setHeader(
            'Content-Type', 'text/html; charset=utf-8')

        html = ["<h1>Download Requests</h1>", "<pre>"]
        html.append(json.dumps(data, indent=2, ensure_ascii=False))
        html.append("</pre>")

        return "\n".join(html)
