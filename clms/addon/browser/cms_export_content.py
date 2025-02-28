"""CMS Export Content section in /en/stats
Credits: 26_export_all_wms_services.py from import scripts folder

TODO:
    Normally export web services and export datasets lists
    with different filters such us the source (EEA, JRC...), for example
    also export metadata identifiers list or something like this.
    One can think what lists are useful to export.
    also based on the coverage: Global/European
"""

from Products.Five import BrowserView
from plone import api
from urllib.parse import urlparse
import csv
import io


def get_domain(url):
    if url and url.strip():
        data = urlparse(url)
        return data.hostname

    return ""


class CMSExportContent(BrowserView):
    """Export Content"""

    def get_datasets(self):
        """Get datasets"""
        catalog = api.portal.get_tool(name="portal_catalog")
        results = catalog.searchResults(
            portal_type="DataSet", sort_on="modified", sort_order="descending"
        )

        items = []
        for brain in results:
            obj = brain.getObject()
            item_data = {
                "@id": obj.absolute_url(),
                "title": obj.title,
                "mapviewer_viewservice": getattr(
                    obj, "mapviewer_viewservice", ""),
                "mapviewer_viewservice_domain": self.get_domain(
                    getattr(obj, "mapviewer_viewservice", "")
                ),
            }
            items.append(item_data)

        return items

    def get_domain(self, url):
        """Extrage domeniul dintr-un URL."""
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def __call__(self):
        self.request.response.setHeader("Content-Type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=domains.csv"
        )

        output = io.StringIO()
        fieldnames = [
            "@id",
            "title",
            "mapviewer_viewservice",
            "mapviewer_viewservice_domain",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for dataset in self.get_datasets():
            writer.writerow(dataset)

        return output.getvalue()
