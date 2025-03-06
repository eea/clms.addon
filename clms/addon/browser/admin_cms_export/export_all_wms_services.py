"""~ 26_export_all_wms_services.py from scripts folder"""

import csv
import io
from plone import api
from clms.addon.browser.admin_cms_export.utils import get_domain


def get_datasets():
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
            "mapviewer_viewservice": getattr(obj, "mapviewer_viewservice", ""),
            "mapviewer_viewservice_domain": get_domain(
                getattr(obj, "mapviewer_viewservice", "")
            ),
        }
        items.append(item_data)

    return items


def export_all_wms_services(request):
    """domains.csv"""
    request.response.setHeader("Content-Type", "text/csv")
    request.response.setHeader(
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

    for dataset in get_datasets():
        writer.writerow(dataset)

    return output.getvalue()
