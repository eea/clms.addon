"""~ 26_export_all_wms_services.py from scripts folder"""

import csv
import io
from plone import api
from clms.addon.browser.admin_cms_export.utils import get_domain


def metadata_wms_wmts_urls(dataset):
    """Prepare list of links from fields metadata_wms_url, metadata_wmts_url"""
    wms_url = getattr(dataset, "metadata_wms_url", ()),
    wmts_url = getattr(dataset, "metadata_wmts_url", ()),

    res = []
    for url in wms_url:
        if url != "" and url is not None:
            res.append(url)

    for url in wmts_url:
        if url != "" and url is not None:
            res.append(url)

    return "\n".join(res)


def get_datasets():
    """Get datasets"""
    catalog = api.portal.get_tool(name="portal_catalog")
    datasets = catalog.searchResults(
        portal_type="DataSet", sort_on="modified", sort_order="descending"
    )

    results = []
    for brain in datasets:
        dataset = brain.getObject()
        dataset_data = {
            "@id": dataset.absolute_url(),
            "title": dataset.title,
            "mapviewer_viewservice": getattr(
                dataset, "mapviewer_viewservice", ""),
            "service_getcapability_path": metadata_wms_wmts_urls(dataset),
            "mapviewer_viewservice_domain": get_domain(
                getattr(dataset, "mapviewer_viewservice", "")
            ),
        }
        results.append(dataset_data)

    return results


def export_all_wms_services(request):
    """services.csv"""
    request.response.setHeader("Content-Type", "text/csv")
    request.response.setHeader(
        "Content-Disposition", "attachment; filename=services.csv"
    )

    output = io.StringIO()
    fieldnames = [
        "@id",
        "title",
        "mapviewer_viewservice",
        "service_getcapability_path",
        "mapviewer_viewservice_domain",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for dataset in get_datasets():
        writer.writerow(dataset)

    return output.getvalue()
