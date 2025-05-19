from Products.Five.browser import BrowserView
from plone.app.uuid.utils import uuidToObject
import csv
import io
from logging import getLogger


def convert_uid_to_path(uid):
    """Return url for uid"""
    try:
        obj = uuidToObject(uid)
        path = obj.absolute_url()
        return path
    except Exception:
        return None


def get_tech_docs_urls(catalog):
    tech_docs = catalog(portal_type="TechnicalLibrary")
    tech_docs_deleted_datasets = []

    for tech_doc in tech_docs:
        obj = tech_doc.getObject()
        uids = obj.datasets or []

        if not uids:
            continue

        deleted_uids = [uid for uid in uids if convert_uid_to_path(uid) is None]

        if len(deleted_uids) == len(uids):
            tech_docs_deleted_datasets.append(
                {
                    "Technical Document Title": obj.title,
                    "Technical Document URL": tech_doc.getURL(),
                }
            )

    return tech_docs_deleted_datasets


class FindTechDocsRelatedToDeletedDatasets(BrowserView):
    """Find Technical Documents related only to a dataset/list of datasets that no longer exist"""

    def __call__(self):
        """custom __call__ method"""
        catalog = self.context.portal_catalog
        tech_docs = get_tech_docs_urls(catalog)

        log = getLogger(__name__)
        log.info(tech_docs)

        if not tech_docs:
            return "No technical documents related to deleted datasets found."

        self.request.response.setHeader("Content-Type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=tech-docs-cleanup.csv"
        )

        output = io.StringIO()
        fieldnames = tech_docs[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tech_docs)

        return output.getvalue()
