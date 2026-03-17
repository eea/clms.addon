"""Technical Library - importer from external source"""

from logging import getLogger
from Products.Five.browser import BrowserView
from clms.addon.browser.cdse.monitor import get_cdse_monitor_view_token
from datetime import datetime
from html import unescape
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
import re
from zope.interface import alsoProvides
import requests
import xml.etree.ElementTree as ET

logger = getLogger(__name__)

LIBRARY_SITEMAP_URL = "https://library.land.copernicus.eu/sitemap.xml"


class TechnicalLibraryImporter(BrowserView):
    """Import items from external source"""

    def _extract_text(self, html_content, pattern):
        """Return cleaned text from first regex group match."""
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if not match:
            return None

        value = re.sub(r"<[^>]+>", "", match.group(1))
        value = unescape(value).strip()
        return value or None

    def get_external_items_from_sitemap(self):
        """Import items from external source sitemap"""
        external_items = []
        response = requests.get(LIBRARY_SITEMAP_URL)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        for url in root.findall("sm:url", ns):
            item_url = url.find("sm:loc", ns).text
            item_modified = url.find("sm:lastmod", ns).text
            external_items.append({
                'item_url': item_url,
                'item_modified': item_modified
            })
        return external_items

    def create_library_item(self, new_url):
        """Create a new library item for external new_url"""
        container = api.portal.get().restrictedTraverse(
            "en/technical-library", None)
        if container is None:
            logger.warning("Target folder not found: /en/technical-library")
            return

        metadata = self.get_item_metadata(new_url)

        # Keep the view public for the cronjob, but elevate only for the
        # actual content creation step.
        with api.env.adopt_roles(["Manager"]):
            api.content.create(
                container=container,
                type="TechnicalLibrary",
                title=metadata.get("title") or "TEST",
                publication_date=metadata.get("publication_date"),
                version=metadata.get("version") or "",
                external_source_url=new_url,
            )

    def get_item_metadata(self, item_url):
        """Fetch title, publication date and version from external page."""
        metadata = {
            "title": None,
            "publication_date": None,
            "version": None,
        }

        try:
            response = requests.get(item_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("Failed to fetch metadata for %s", item_url)
            return metadata

        html_content = response.text

        metadata["title"] = self._extract_text(
            html_content,
            r'<h1[^>]*class="[^"]*\btitle\b[^"]*"[^>]*>(.*?)</h1>',
        )

        publication_date_text = self._extract_text(
            html_content,
            r'<div[^>]*quarto-title-meta-heading[^>]*>\s*Published\s*</div>\s*'
            r'<div[^>]*quarto-title-meta-contents[^>]*>\s*'
            r'<p[^>]*class="[^"]*\bdate\b[^"]*"[^>]*>(.*?)</p>',
        )
        if publication_date_text:
            try:
                metadata["publication_date"] = datetime.strptime(
                    publication_date_text,
                    "%B %d, %Y",
                ).date()
            except ValueError:
                logger.warning(
                    "Could not parse publication date '%s' for %s",
                    publication_date_text,
                    item_url,
                )

        metadata["version"] = self._extract_text(
            html_content,
            r'<div[^>]*quarto-title-meta-heading[^>]*>\s*Version\s*</div>\s*'
            r'<div[^>]*quarto-title-meta-contents[^>]*>\s*<p[^>]*>(.*?)</p>',
        )

        return metadata

    def import_technical_library_items(self):
        """Import items"""
        logger.info("START import Technical Library items.")

        external_items = self.get_external_items_from_sitemap()
        logger.info("Found in sitemap: %s items" % len(external_items))

        catalog = self.context.portal_catalog
        existing_items = [
            x.getObject() for x in catalog(portal_type="TechnicalLibrary")]
        logger.info("Found in website: %s items" % len(existing_items))

        existing_items_urls = [
            x.external_source_url
            for x in existing_items
            if x.external_source_url is not None
        ]

        for new_item in external_items:
            new_url = new_item.get('item_url')
            if new_url in existing_items_urls:
                logger.info("SKIP. ALREADY EXISTING: %s" % new_url)
                continue
            logger.info("CREATE ITEM for %s" % new_url)
            self.create_library_item(new_url)

        logger.info("DONE IMPORT")

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        # It is safe to reuse this ENV var
        view_token_env_value = get_cdse_monitor_view_token()

        if view_token_env_value is None:
            logger.info("Cancelled. Missing view token ENV.")
            return "missing env var"

        view_token = self.request.form.get("token", None)
        if view_token is None:
            logger.info("Cancelled: missing view token.")
            return "missing view token"

        if view_token != view_token_env_value:
            logger.info("Cancelled: invalid view token.")
            return "invalid view token"

        self.import_technical_library_items()
        return "ok"
