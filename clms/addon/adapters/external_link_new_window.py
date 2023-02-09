"""
Filter to render some internal links as download links
"""
# -*- coding: utf-8 -*-
import re

import six
from bs4 import BeautifulSoup
from clms.addon.utils import CLMS_DOMAINS
from plone.outputfilters.interfaces import IFilter
from Products.CMFPlone.utils import safe_unicode
from six.moves.urllib.parse import urlsplit
from zope.interface import implementer


@implementer(IFilter)
class ExternalLinkNewWindowFilter:
    """adapter implementation. This should catch all external links and
    configure them to open in new window if they are not otherwise configured
    """

    def __init__(self, context=None, request=None):
        """initializer"""
        self.current_status = None
        self.context = context
        self.request = request

    # IFilter implementation
    order = 950
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
        return self.context is not None

    def _shorttag_replace(self, match):
        """replace short tags"""
        tag = match.group(1)
        if tag in self.singleton_tags:
            return "<" + tag + " />"

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

            if self.is_external_link(href):
                target = attributes.get("target")
                if target is None:
                    attributes["target"] = "_blank"

        return six.text_type(soup)

    def is_external_link(self, url):
        """ check if this url is external """
        url_parts = urlsplit(url)
        # pylint: disable=line-too-long
        if url_parts.hostname and url_parts.hostname in CLMS_DOMAINS or not url_parts.hostname:  # noqa
            return False

        return True
