""" transformers for slateTable blocks"""
# -*- coding: utf-8 -*-
from logging import getLogger

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


class SlateTableBlockSerializerBase(SlateBlockSerializerBase):
    """SlateBlockSerializerBase."""

    order = 100
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


class SlateExternalLinkBlockSerializerBase:
    """Slate block serializer to handle external links that are not
    explicitely marked to be opened in a given target.

    They will be modified here to be opened in a new window
    """

    field = "value"
    order = 200
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
                external = (
                    child.get("data", {}).get("link", {}).get("external", {})
                )
                if external:
                    # Check if it has an explicit target
                    target = external.get("target", None)
                    if target is None:
                        # It has no explicit target, mark it to be
                        # opened in a new window with target=_blank
                        child["data"]["link"]["external"]["target"] = "_blank"

                        self.log.info(
                            "Link converted to target=_blank: %s",
                            child["data"]["link"]["external"]["external_link"],
                        )

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateExternalLinkBlockSerializer(SlateExternalLinkBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateExternalLinkBlockSerializerRoot(
    SlateExternalLinkBlockSerializerBase
):
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
