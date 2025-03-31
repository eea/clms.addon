"""~ 16_export_technical_library.py from scripts folder"""

from clms.addon.browser.admin_cms_export.utils import (
    get_technical_library_items_obj
)
from plone.app.uuid.utils import uuidToObject
import csv
import io


def related_datasets_number(technical_library):
    """ Number of related datasets in given technical library item
    """
    try:
        datasets = technical_library.datasets
    except Exception:
        datasets = []
    if datasets is None:
        datasets = []

    return len(datasets)


def related_products_number(technical_library):
    """ Number of related products in given technical library item
    """
    try:
        products = technical_library.products
    except Exception:
        products = []
    if products is None:
        products = []

    return len(products)


def relations_number(technical_library):
    """ Number of relations for given technical library
    """
    return related_datasets_number(
        technical_library) + related_products_number(technical_library)


def prepare_item_data(technical_library, max_relations_number):
    """Prepare technical library item data"""
    item = {}
    item["item_technical_library_id"] = technical_library.UID()
    item["item_technical_library_title"] = technical_library.title
    item["item_technical_library_url"] = technical_library.absolute_url()

    try:
        products = technical_library.products
    except Exception:
        products = []
    if products is None:
        products = []

    for i, product_id in enumerate(products):
        item[f"related_product_{i}_id"] = product_id
        product = uuidToObject(product_id)
        product_title = product.title if product is not None else ""
        item[f"related_product_{i}_title"] = product_title

    try:
        datasets = technical_library.datasets
    except Exception:
        datasets = []
    if datasets is None:
        datasets = []

    for i, dataset_id in enumerate(datasets):
        item[f"related_dataset_{i}_id"] = dataset_id
        dataset = uuidToObject(dataset_id)
        dataset_title = dataset.title if dataset is not None else ""
        item[f"related_dataset_{i}_title"] = dataset_title

    # fill with empty columns
    for i in range(max_relations_number):
        if f"related_product_{i}_id" not in item:
            item[f"related_product_{i}_id"] = ""
            item[f"related_product_{i}_title"] = ""
        if f"related_dataset_{i}_id" not in item:
            item[f"related_dataset_{i}_id"] = ""
            item[f"related_dataset_{i}_title"] = ""

    return item


def export_technical_library(request):
    """exported-technical-libraries.csv
    Export technical library documents from Plone to a CSV file.
    """
    technical_library_items = get_technical_library_items_obj()

    max_relations_number = 0
    for library in technical_library_items:
        rel_number = relations_number(library)
        if rel_number > max_relations_number:
            max_relations_number = rel_number

    print('Max relations: "{}"'.format(max_relations_number))

    libraries = []
    for library in technical_library_items:
        print('Querying: "{}"'.format(library.absolute_url()))
        libraries.append(prepare_item_data(library, max_relations_number))

    request.response.setHeader("Content-Type", "text/csv")
    request.response.setHeader(
        "Content-Disposition",
        "attachment; filename=exported-technical-libraries.csv"
    )

    output = io.StringIO()

    csv.DictWriter(output, sorted(libraries[0].keys())).writeheader()
    csv.DictWriter(output, sorted(libraries[0].keys())).writerows(libraries)

    return output.getvalue()
