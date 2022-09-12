""" custom indexers for special blocks"""
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
    """ Tab content searchable text """
    def __init__(self, context, request):
        """ constructor """
        self.context = context
        self.request = request

    def __call__(self, block_value):
        """ implementation"""
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


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class AccordionSearchableText(object):
    """ Accordion searchable text """
    def __init__(self, context, request):
        """ constructor """
        self.context = context
        self.request = request

    def __call__(self, block_value):
        """ implementation"""

        data = block_value.get('data', {})

        blocks = data.get('blocks', {})
        blocks_layout = data.get('blocks_layout', {})

        blocks_text = []
        for block_id in blocks_layout.get("items", []):
            block = blocks.get(block_id, {})
            blocks_text.append(extract_text(block, self.context, self.request))

        return " ".join([text.strip() for text in blocks_text if text.strip()])


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class AccordionPanelSearchableText(object):
    """ accordion panel searchable text"""
    def __init__(self, context, request):
        """ constructor """
        self.context = context
        self.request = request

    def __call__(self, block_value):
        """ implementation"""

        blocks = block_value.get('blocks', {})
        blocks_layout = block_value.get('blocks_layout', {})

        blocks_text = []
        for block_id in blocks_layout.get("items", []):
            block = blocks.get(block_id, {})
            blocks_text.append(extract_text(block, self.context, self.request))

        blocks_text.append(block_value.get('title', ''))

        return " ".join([text.strip() for text in blocks_text if text.strip()])



