"""~ 34_export_datasets_with_download_information from scripts folder"""

from clms.addon.browser.admin_cms_export.utils import get_datasets_obj
from clms.types.restapi.mapviewer_service.lrf_get import (
    RootMapViewerServiceGet
)
import csv
import io

EEA_GEONETWORK_BASE_URL = (
    "https://sdi.eea.europa.eu/catalogue/copernicus/"
    "api/records/{uid}/formatters/xml?approved=true"
)
VITO_GEONETWORK_BASE_URL = (
    "https://land.copernicus.vgt.vito.be/geonetwork/"
    "srv/api/records/{uid}/formatters/xml?approved=true"
)


def export_datasets_with_download_information(request):
    """datasets-export.csv"""
    datasets = get_datasets_obj()
    items = []

    for dataset in datasets:
        print(f'Checking dataset "{dataset.title}"')
        product = dataset.aq_parent
        print(f'Product "{product.title}" found')
        geonetwork_identifiers = dataset.geonetwork_identifiers
        geonetwork_ids = []
        if geonetwork_identifiers:
            geonetwork_ids = geonetwork_identifiers.get("items", [])

        if geonetwork_ids:
            dataset_geonetwork_type = geonetwork_ids[0].get("type")
            if dataset_geonetwork_type == "EEA":
                dataset_geonetwork_id = EEA_GEONETWORK_BASE_URL.format(
                    uid=geonetwork_ids[0].get("id")
                )
            elif dataset_geonetwork_type == "VITO":
                dataset_geonetwork_id = VITO_GEONETWORK_BASE_URL.format(
                    uid=geonetwork_ids[0].get("id")
                )
            else:
                dataset_geonetwork_id = geonetwork_ids[0].get("id")
        else:
            dataset_geonetwork_id = ""
            dataset_geonetwork_type = ""

        ddi_raw = dataset.dataset_download_information

        service = RootMapViewerServiceGet()
        component_info = service.get_component_info(product)
        component_title = component_info[0]

        dataset_full_path = ""
        try:
            dataset_full_path = dataset.dataset_full_path
        except Exception:
            print("ERROR dataset_full_path")

        dataset_full_format = ""
        try:
            a_dataset_full_format = dataset.dataset_full_format
            dataset_full_format = a_dataset_full_format.get("token")
        except Exception:
            pass

        dataset_full_source = ""
        try:
            a_dataset_full_source = dataset.dataset_full_source
            dataset_full_source = a_dataset_full_source.get("token")
        except Exception:
            pass

        mapviewer_timeseriesservice = ""
        try:
            mapviewer_timeseriesservice = dataset.mapviewer_timeseriesservice
        except Exception:
            pass

        if dataset_geonetwork_id is not None:
            dataset_geonetwork_id = dataset_geonetwork_id.replace(
                "/formatters/xml?approved=true", "")

        for ddi in ddi_raw.get("items", []):
            items.append(
                {
                    "component_title": component_title,
                    "product_id": product.UID(),
                    "product_title": product.title,
                    "product_show_in_mapviewer_link":
                        product.show_in_mapviewer_link,
                    "dataset_id": dataset.UID(),
                    "dataset_title": dataset.title,
                    "dataset_geonetwork_id": dataset_geonetwork_id,
                    "dataset_geonetwork_type": dataset_geonetwork_type,
                    "dataset_full_path": dataset_full_path,
                    "dataset_full_format": dataset_full_format,
                    "dataset_full_source": dataset_full_source,
                    "downloadable_dataset": dataset.downloadable_dataset,
                    "downloadable_full_dataset":
                        dataset.downloadable_full_dataset,
                    "mapviewer_viewservice": dataset.mapviewer_viewservice,
                    "mapviewer_default_active":
                        dataset.mapviewer_default_active,
                    "mapviewer_istimeseries": dataset.mapviewer_istimeseries,
                    "mapviewer_timeseriesservice": mapviewer_timeseriesservice,
                    "dataset_download_information_id": ddi.get("@id"),
                    "dataset_download_information_full_format": ddi.get(
                        "full_format", {}
                    ).get("token")
                    if isinstance(ddi.get("full_format", {}), dict)
                    else ddi.get("full_format"),
                    "dataset_download_information_full_path": ddi.get(
                        "full_path"),
                    "dataset_download_information_full_source": ddi.get(
                        "full_source"),
                    "dataset_download_information_name": ddi.get("@name"),
                }
            )

        # Refs #288680 - include all datasets in this export
        if len(ddi_raw.get("items", [])) == 0:
            items.append(
                {
                    "component_title": component_title,
                    "product_id": product.UID(),
                    "product_title": product.title,
                    "product_show_in_mapviewer_link":
                        product.show_in_mapviewer_link,
                    "dataset_id": dataset.UID(),
                    "dataset_title": dataset.title,
                    "dataset_geonetwork_id": dataset_geonetwork_id,
                    "dataset_geonetwork_type": dataset_geonetwork_type,
                    "dataset_full_path": dataset_full_path,
                    "dataset_full_format": dataset_full_format,
                    "dataset_full_source": dataset_full_source,
                    "downloadable_dataset": dataset.downloadable_dataset,
                    "downloadable_full_dataset":
                        dataset.downloadable_full_dataset,
                    "mapviewer_viewservice": dataset.mapviewer_viewservice,
                    "mapviewer_default_active":
                        dataset.mapviewer_default_active,
                    "mapviewer_istimeseries": dataset.mapviewer_istimeseries,
                    "mapviewer_timeseriesservice": mapviewer_timeseriesservice,
                    "dataset_download_information_id": "",
                    "dataset_download_information_full_format": "",
                    "dataset_download_information_full_path": "",
                    "dataset_download_information_full_source": "",
                    "dataset_download_information_name": "",
                }
            )

    items.sort(
        key=lambda x: (
            x.get("component_title", ""),
            x.get("product_title", ""),
            x.get("dataset_title", ""),
        )
    )

    request.response.setHeader("Content-Type", "text/csv")
    request.response.setHeader(
        "Content-Disposition", "attachment; filename=datasets-export.csv"
    )

    output = io.StringIO()
    fieldnames = items[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(items)

    return output.getvalue()
