"""CMS Export Content section in /en/stats
"""

from Products.Five import BrowserView
from clms.addon.browser.admin_cms_export.export_all_wms_services import (
    export_all_wms_services,
)
from clms.addon.browser.admin_cms_export.export_datasets import (
    export_datasets_with_download_information,
)
from clms.addon.browser.admin_cms_export.export_technical_library import (
    export_technical_library,
)


class CMSExportContent(BrowserView):
    """Export Content"""

    def __call__(self):
        """Multiple export types:
        /cms-content-export?q=export_all_wms_services
        /cms-content-export?q=export_datasets_with_download_information
        /cms-content-export?q=export_technical_library
        """
        query_param = self.request.get("q", None)
        if query_param == "export_all_wms_services":
            return export_all_wms_services(self.request)
        elif query_param == "export_datasets_with_download_information":
            return export_datasets_with_download_information(self.request)
        elif query_param == "export_technical_library":
            return export_technical_library(self.request)
        else:
            return "No q param set."
