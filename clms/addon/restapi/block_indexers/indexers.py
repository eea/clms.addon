# -*- coding: utf-8 -*-
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockSearchableText
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.restapi.indexers import extract_text


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class TabSearchableText(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block_value):
        blocks = block_value.get('blocks', {})
        blocks_layout = block_value.get('blocks_layout', {})

        blocks_text = []
        for block_id in blocks_layout.get("items", []):
            block = blocks.get(block_id, {})
            blocks_text.append(extract_text(block, self.context, self.request))

        # # Extract text using the base plone.app.contenttypes indexer
        # std_text = SearchableText(obj)
        # blocks_text.append(std_text)
        return " ".join([text.strip() for text in blocks_text if text.strip()])
