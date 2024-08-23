"""
Converter from RichTextValue items to JSON
"""
# -*- coding: utf-8 -*-

from urllib.parse import urlparse

from bs4 import BeautifulSoup
from plone.app.textfield.interfaces import IRichTextValue
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IContextawareJsonCompatible
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.utils import uid_to_url
from zope.component import adapter
from zope.interface import implementer


@adapter(IRichTextValue, IDexterityContent)
@implementer(IContextawareJsonCompatible)
class RichtextDXContextConverter:
    """RichtextValue convert to handle UID based links"""

    def __init__(self, value, context):
        """init the adapter"""
        self.value = value
        self.context = context

    def __call__(self):
        """call the conversion"""
        value = self.value
        output = value.raw

        new_output = self.resolve_uids(output)

        return {
            "data": json_compatible(new_output),
            "content-type": json_compatible(value.mimeType),
            "encoding": json_compatible(value.encoding),
        }

    def resolve_uids(self, data):
        """resolve uids and replace with an absolute link"""
        soup = BeautifulSoup(data, features="lxml")
        for link in soup.find_all("a"):
            href = link.get("href")
            new_href = uid_to_url(href)
            if href != new_href:
                parsed_new_href = urlparse(new_href)
                link["href"] = parsed_new_href._replace(
                    netloc="", scheme="").geturl()
        return str(soup)
