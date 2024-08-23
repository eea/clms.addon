"""Automaticallly expand contextnavigation on context that has cclFAQ blocks"""

from plone.restapi.blocks import visit_blocks
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services.contextnavigation.get import (
    ContextNavigation as BaseContextNavigation,
)
from zope.component import adapter
from zope.interface import Interface, implementer

from clms.addon.interfaces import IClmsAddonLayer


@implementer(IExpandableElement)
@adapter(Interface, IClmsAddonLayer)
class ContextNavigation(BaseContextNavigation):
    """ContextNavigation expander"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False, prefix="expand.contextnavigation."):
        context = self.context

        if getattr(self.request, "expand_contextnavigation", False):
            # super(ContextNavigation, self).__call__(expand=expand, prefix=prefix)
            return {}

        self.request.expand_contextnavigation = True

        if hasattr(context.aq_inner.aq_self, "blocks"):
            blocks = context.blocks
            for block in visit_blocks(context, blocks):
                if not block:
                    continue
                if block.get("@type") == "cclFAQ":
                    return super().__call__(expand=True, prefix=prefix)

        return super(ContextNavigation, self).__call__(expand=expand, prefix=prefix)
