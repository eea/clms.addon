"""CMS Export Content section in /en/stats

TODO:
    Normally export web services and export datasets lists
    with different filters such us the source (EEA, JRC...), for example
    also export metadata identifiers list or something like this.
    One can think what lists are useful to export.
    also based on the coverage: Global/European
"""

from Products.Five import BrowserView
from clms.addon.browser.admin_cms_export.export_all_wms_services import (
    export_all_wms_services,
)


class CMSExportContent(BrowserView):
    """Export Content"""

    def __call__(self):
        """Multiple export types here"""
        query_param = self.request.get("q", None)
        if query_param == "export_all_wms_services":
            return export_all_wms_services(self.request)
        else:
            return "No q param set."
