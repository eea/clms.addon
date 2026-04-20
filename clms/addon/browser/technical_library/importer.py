"""Technical Library - importer from external source"""

import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import getLogger
from html import unescape
from smtplib import SMTPException

from chameleon import PageTemplateLoader
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.utils import safe_text
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.interface import alsoProvides

from clms.addon.browser.cdse.monitor import get_cdse_monitor_view_token
from clms.addon.browser.cdse.utils import get_env_var

logger = getLogger(__name__)

LIBRARY_SITEMAP_URL = "https://library.land.copernicus.eu/sitemap.xml"
TECHNICAL_LIBRARY_REVIEW_EMAIL_TO_ENV_VAR = (
    "TECHNICAL_LIBRARY_REVIEW_EMAIL_TO"
)


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
            return None

        metadata = self.get_item_metadata(new_url)

        # Keep the view public for the cronjob, but elevate only for the
        # actual content creation step.
        with api.env.adopt_roles(["Manager"]):
            item = api.content.create(
                container=container,
                type="TechnicalLibrary",
                title=metadata.get("title") or "TEST",
                publication_date=metadata.get("publication_date"),
                version=metadata.get("version") or "",
                external_source_url=new_url,
            )
        return {
            "title": item.Title(),
            "url": item.absolute_url().replace("/api/", "/"),
        }

    def _format_review_email(self, created_items):
        """Format the review email for newly created items."""
        portal_title = "CLMS"

        path = os.path.dirname(__file__)
        templates = PageTemplateLoader(path)
        template = templates["technical_library_review_template.pt"]

        return template(
            created_items=created_items,
            item_count=len(created_items),
            date=datetime.utcnow().strftime("%B %d, %Y at %H:%M:%S UTC"),
            portal_title=portal_title,
        )

    def _send_review_email(self, created_items):
        """Send a consolidated review email for newly imported items."""
        if not created_items:
            return False

        email_to = get_env_var(TECHNICAL_LIBRARY_REVIEW_EMAIL_TO_ENV_VAR)
        if not email_to:
            logger.info(
                "Skipping technical library review notification. Missing %s.",
                TECHNICAL_LIBRARY_REVIEW_EMAIL_TO_ENV_VAR,
            )
            return False

        subject = (
            "[Review] {} new Technical Library item(s) imported"
        ).format(len(created_items))
        html_body = self._format_review_email(created_items)

        try:
            registry = getUtility(IRegistry)
            mail_settings = registry.forInterface(
                IMailSchema, prefix="plone"
            )
            from_address = mail_settings.email_from_address
            from_name = (
                mail_settings.email_from_name or "Technical Library Importer"
            )
            source = '"{0}" <{1}>'.format(from_name, from_address)
            encoding = registry.get("plone.email_charset", "utf-8")
            mailhost = api.portal.get_tool("MailHost")

            message = MIMEMultipart("related")
            message["Subject"] = subject
            message["From"] = source
            message["Reply-To"] = from_address
            message.preamble = "This is a multi-part message in MIME format"

            msg_alternative = MIMEMultipart("alternative")
            message.attach(msg_alternative)
            msg_alternative.attach(
                MIMEText(
                    "This email requires HTML support to display properly."
                )
            )
            msg_alternative.attach(MIMEText(safe_text(html_body), "html"))

            recipients = [email.strip() for email in email_to.split(",")]
            for recipient in recipients:
                if not recipient:
                    continue
                mailhost.send(
                    message.as_string(),
                    recipient,
                    source,
                    subject=subject,
                    charset=encoding,
                )
                logger.info(
                    "Technical library review notification sent to %s",
                    recipient,
                )
        except (SMTPException, RuntimeError):
            plone_utils = api.portal.get_tool("plone_utils")
            logger.error(
                "Unable to send technical library review email: %s",
                plone_utils.exceptionString(),
            )
            return False

        return True

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
        with api.env.adopt_roles(["Manager"]):
            existing_items = [
                x.getObject()
                for x in catalog.unrestrictedSearchResults(
                    portal_type="TechnicalLibrary",
                )
            ]
        logger.info("Found in website: %s items" % len(existing_items))

        existing_items_urls = [
            x.external_source_url
            for x in existing_items
            if x.external_source_url is not None
        ]

        created_items = []
        for new_item in external_items:
            new_url = new_item.get('item_url')
            if new_url in existing_items_urls:
                logger.info("SKIP. ALREADY EXISTING: %s" % new_url)
                continue
            logger.info("CREATE ITEM for %s" % new_url)
            created_item = self.create_library_item(new_url)
            if created_item is not None:
                created_items.append(created_item)

        if not created_items:
            logger.info("DONE IMPORT. No new items created.")
            return created_items

        self._send_review_email(created_items)

        logger.info("DONE IMPORT")
        return created_items

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
