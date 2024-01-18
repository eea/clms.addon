"""
RichTextField Deserializer
"""
# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.component import adapter
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.services.content.tus import TUSUpload
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
import html as html_parser
from plone.app.textfield.value import RichTextValue

from bs4 import BeautifulSoup
from plone.restapi.deserializer.utils import path2uid


@implementer(IFieldDeserializer)
@adapter(IRichText, IDexterityContent, IBrowserRequest)
class RichTextFieldDeserializer(DefaultFieldDeserializer):
    """ RichTextField Deserializer that handles UID links
        for Slate advanced link plugin
    """
    def __call__(self, value):
        """ call the deserializer"""
        content_type = self.field.default_mime_type
        encoding = "utf8"
        if isinstance(value, dict):
            content_type = value.get("content-type", content_type)
            encoding = value.get("encoding", encoding)
            data = value.get("data", "")
        elif isinstance(value, TUSUpload):
            content_type = value.metadata().get("content-type", content_type)
            with open(value.filepath, "rb") as f:
                data = f.read().decode("utf8")
        else:
            data = value

        new_data = self.convert_links_to_uid(data)

        value = RichTextValue(
            raw=html_parser.unescape(new_data),
            mimeType=content_type,
            outputMimeType=self.field.output_mime_type,
            encoding=encoding,
        )
        self.field.validate(value)
        return value

    def convert_links_to_uid(self, data):
        """ convert internal links to UID based links"""
        soup = BeautifulSoup(data)
        for link in soup.find_all("a"):
            if is_internal_link(link.get("href")):
                new_link = path2uid(self.context, link.get("href"))
                link["href"] = new_link
        return str(soup)


def is_internal_link(href):
    """ check if this link is internal"""
    if (
        href.startswith("http")
        or href.startswith("ftp")
        or href.startswith("mailto")
        or href.startswith("#")
    ):
        return False
    return True
