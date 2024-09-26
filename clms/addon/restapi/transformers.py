"""transformers for slateTable blocks"""

# -*- coding: utf-8 -*-
from logging import getLogger
from plone import api

from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import (
    SlateBlockDeserializerBase,
    SlateBlockTransformer,
    iterate_children,
)
from plone.restapi.interfaces import (
    IBlockFieldDeserializationTransformer,
    IBlockFieldSerializationTransformer,
)
from plone.restapi.serializer.blocks import SlateBlockSerializerBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class CCLFaqSerializer:
    """Serializer for FAQ blocks"""

    order = 100
    block_type = "cclFAQ"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        print("block", block, self.context)
        return block


class SlateTableBlockSerializerBase(SlateBlockSerializerBase):
    """SlateBlockSerializerBase."""

    order = -100
    block_type = "slateTable"

    def __call__(self, block):
        """call"""
        rows = block.get("table", {}).get("rows", [])
        for row in rows:
            cells = row.get("cells", [])

            for cell in cells:
                cellvalue = cell.get("value", [])
                children = iterate_children(cellvalue or [])
                for child in children:
                    node_type = child.get("type")
                    if node_type:
                        if node_type == "a":
                            handle_links(child)
                        handler = getattr(self, f"handle_{node_type}", None)
                        if handler:
                            handler(child)

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateTableBlockSerializer(SlateTableBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateTableBlockSerializerRoot(SlateTableBlockSerializerBase):
    """Serializer for site root"""


DOWNLOADABLE_TYPES = ["File", "TechnicalLibrary", "Image"]

FILE_FIELDS = {"File": "file", "TechnicalLibrary": "file", "Image": "image"}


def handle_links(child):
    """Solve a href cases"""
    external = child.get("data", {}).get("link", {}).get("external", {})

    internal = child.get("data", {}).get("link", {}).get("internal", {})

    if external:
        # Check if it has an explicit target
        target = external.get("target", None)
        if target is None:
            # It has no explicit target, mark it to be
            # opened in a new window with target=_blank
            child["data"]["link"]["external"]["target"] = "_blank"

            # self.log.info(
            #     "Link converted to target=_blank: %s",
            #     child["data"]["link"]["external"]["external_link"],
            # )
    elif internal:
        # {
        #     "children": [
        #         {"text": "What is the European Ground Motion Service?"}
        #     ],
        #     "data": {
        #         "link": {
        #             "internal": {
        #                 "internal_link": [
        #                     {
        #                         "@id": "../../../resolveuid/53b80c704a814502bd088e617ac11afc",
        #                         "title": "Introduction to EGMS",
        #                     }
        #                 ]
        #             }
        #         }
        #     },
        #     "type": "a",
        # }
        internal_link = internal.get("internal_link", [])
        for info in internal_link:
            oid = info.get("@id", "")
            if oid and "resolveuid" in oid:
                uid = oid.split("/resolveuid/")[1]
                obj = api.content.get(UID=uid)
                if obj is None:
                    # self.log.info("Could not find obj for uid %s", uid)
                    continue

                if obj.portal_type in DOWNLOADABLE_TYPES:
                    info["download"] = True
                    info["file_field"] = FILE_FIELDS[obj.portal_type]
                    # print("setting to download", info)

                # print(obj, obj.portal_type)
                # if hasattr(obj, "file"):
                #     info["download"] = True


class SlateExternalLinkBlockSerializerBase:
    """Slate block serializer to handle external links that are not
    explicitely marked to be opened in a given target.

    They will be modified here to be opened in a new window
    """

    field = "value"
    order = -200
    block_type = "slate"

    log = getLogger(__name__)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        """execute the serializer"""
        value = (block or {}).get(self.field, [])
        children = iterate_children(value or [])

        for child in children:
            node_type = child.get("type")
            if node_type == "a":
                handle_links(child)

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateExternalLinkBlockSerializer(SlateExternalLinkBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateExternalLinkBlockSerializerRoot(SlateExternalLinkBlockSerializerBase):
    """Serializer for site root"""


class SlateTableBlockTransformer(SlateBlockTransformer):
    """Salte table block transformer base"""

    def __call__(self, block):
        rows = block.get("table", {}).get("rows", [])
        for row in rows:
            cells = row.get("cells", [])

            for cell in cells:
                cellvalue = cell.get("value", [])
                children = iterate_children(cellvalue or [])
                for child in children:
                    node_type = child.get("type")
                    if node_type:
                        if node_type == "a":
                            handle_links(child)
                        handler = getattr(self, f"handle_{node_type}", None)
                        if handler:
                            handler(child)

        return block


class SlateTableBlockDeserializerBase(
    SlateTableBlockTransformer, SlateBlockDeserializerBase
):
    """SlateTableBlockDeserializerBase."""

    order = 100
    block_type = "slateTable"


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateTableBlockDeserializer(SlateTableBlockDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateTableBlockDeserializerRoot(SlateTableBlockDeserializerBase):
    """Deserializer for site root"""
