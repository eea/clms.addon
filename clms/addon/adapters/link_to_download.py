"""
Filter to render some internal links as download links
"""
# -*- coding: utf-8 -*-
from logging import getLogger

import re
import six

from bs4 import BeautifulSoup
from plone import api
from plone.outputfilters.interfaces import IFilter
from Products.CMFPlone.utils import safe_unicode
from six.moves.urllib.parse import urlsplit, urlunsplit
from zope.interface import implementer


@implementer(IFilter)
class DownloadableLinkFilter:
    """adapter implementation"""

    def __init__(self, context=None, request=None):
        """initializer"""
        self.current_status = None
        self.context = context
        self.request = request

    # IFilter implementation
    order = 900
    DOWNLOADABLE_PORTAL_TYPES = ["TechnicalLibrary", "File"]
    singleton_tags = set(
        [
            "area",
            "base",
            "basefont",
            "br",
            "col",
            "command",
            "embed",
            "frame",
            "hr",
            "img",
            "input",
            "isindex",
            "keygen",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        ]
    )

    def is_enabled(self):
        """return whether it is enabled"""
        if self.context is None:
            return False
        else:
            return True

    def _shorttag_replace(self, match):
        """replace short tags"""
        tag = match.group(1)
        if tag in self.singleton_tags:
            return "<" + tag + " />"
        else:
            return "<" + tag + "></" + tag + ">"

    def __call__(self, data):
        """filter implementation"""
        data = re.sub(r"<([^<>\s]+?)\s*/>", self._shorttag_replace, data)
        soup = BeautifulSoup(safe_unicode(data), "html.parser")

        for elem in soup.find_all(["a", "area"]):
            attributes = elem.attrs
            href = attributes.get("href")
            # an 'a' anchor element has no href
            if not href:
                continue
            if (
                not href.startswith("mailto<")
                and not href.startswith("mailto:")
                and not href.startswith("tel:")
                and not href.startswith("#")
            ):
                attributes["href"] = self._render_internal_link(href)
        return six.text_type(soup)

    def resolve_link(self, href):
        """resolve a link into a Plone object"""

        portal = api.portal.get()

        if href.startswith("/"):
            href = href[1:]

        try:
            item = portal.restrictedTraverse(href)
            if item:
                return item, "", ""
        except KeyError:

            log = getLogger(__name__)
            log.info("Item does not exist in portal: %s", href)
        return None, "", ""

    def _render_internal_link(self, href):
        """check whether the link is of a portal item and if so render the proper link"""
        url_parts = urlsplit(href)
        path_parts = urlunsplit(["", ""] + list(url_parts[2:]))
        obj, subpath, appendix = self.resolve_link(path_parts)
        if obj is not None:
            if (
                hasattr(obj, "portal_type")
                and obj.portal_type in self.DOWNLOADABLE_PORTAL_TYPES
            ):
                return f"{obj.absolute_url()}/@@download/file"

            return obj.absolute_url()

        return href
