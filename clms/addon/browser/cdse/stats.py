"""Admin view to list all downloads stats (with all details for CDSE tasks)."""

from Products.Five import BrowserView
from zope.component import getUtility
from clms.statstool.utility import IDownloadStatsUtility
import json


class CDSEStatsView(BrowserView):
    """Show all stats without filters"""

    def __call__(self):
        utility = getUtility(IDownloadStatsUtility)

        soup = utility.get_soup()
        data = [dict(x.attrs) for x in soup.data.values()]

        self.request.response.setHeader(
            'Content-Type', 'text/html; charset=utf-8')

        html = ["<h1>Download statistics</h1>", "<pre>"]
        html.append(json.dumps(data, indent=2, ensure_ascii=False))
        html.append("</pre>")

        return "\n".join(html)
