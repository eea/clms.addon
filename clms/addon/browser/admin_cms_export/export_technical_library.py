"""~ 16_export_technical_library.py from scripts folder"""

from clms.addon.browser.admin_cms_export.utils import (
    get_technical_library_items_obj
)
from plone.app.uuid.utils import uuidToObject
import csv
import io


MAX_NUM_OF_RELATIONS = 10


def prepare_item_data(technical_library):
    """ Prepare technical library item data
    """
    item = {}
    item["item_technical_library_id"] = technical_library.UID()
    item["item_technical_library_title"] = technical_library.title
    item["item_technical_library_url"] = technical_library.getId()

    try:
        products = technical_library.products
    except Exception:
        products = []
    if products is None:
        products = []

    # TODO WIP here
    # for i, product_id in enumerate(products):
    #     item[f"related_product_{i}_id"] = product_id
    #     product = uuidToObject(product_id)
    #     product_title = product.title if product is not None else ""
    #     item[f"related_product_{i}_title"] = product_title
    #
    # try:
    #     datasets = technical_library.datasets
    # except Exception:
    #     datasets = []
    # if datasets is None:
    #     datasets = []
    #
    # for i, dataset_id in enumerate(datasets):
    #     item[f"related_dataset_{i}_id"] = dataset_id
    #     dataset = uuidToObject(dataset_id)
    #     dataset_title = dataset.title if dataset is not None else ""
    #     item[f"related_dataset_{i}_title"] = dataset_title
    #
    # # fill with empty columns
    # for i in range(MAX_NUM_OF_RELATIONS):
    #     if f"related_product_{i}_id" not in item:
    #         item[f"related_product_{i}_id"] = ""
    #         item[f"related_product_{i}_title"] = ""
    #     if f"related_dataset_{i}_id" not in item:
    #         item[f"related_dataset_{i}_id"] = ""
    #         item[f"related_dataset_{i}_title"] = ""

    return item


def export_technical_library(request):
    """exported-technical-libraries.csv
    Export technical library documents from Plone to a CSV file.
    """
    technical_library_items = get_technical_library_items_obj()

    libraries = []
    for library in technical_library_items:
        print('Querying: "{}"'.format(library.absolute_url()))
        libraries.append(prepare_item_data(library))

    request.response.setHeader("Content-Type", "text/csv")
    request.response.setHeader(
        "Content-Disposition",
        "attachment; filename=exported-technical-libraries.csv"
    )

    output = io.StringIO()
    fieldnames = libraries[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(libraries)

    return output.getvalue()
