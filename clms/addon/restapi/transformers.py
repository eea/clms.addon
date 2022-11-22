""" transformers for slateTable blocks"""
# -*- coding: utf-8 -*-
from collections import deque

from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.serializer.blocks import SlateBlockSerializerBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


def iterate_children(value):
    """iterate_children.

    :param value:
    """
    queue = deque(value)
    while queue:
        child = queue.pop()
        yield child
        if child.get("children"):
            queue.extend(child["children"] or [])


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
                        # if node_type == "a":
                        #     import pdb

                        #     pdb.set_trace()
                        #     a = 1
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
