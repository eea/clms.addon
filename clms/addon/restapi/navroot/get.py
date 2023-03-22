# -*- coding: utf-8 -*-
"""
@navroot endpoint
"""
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Navroot:
    """Navroot endpoint"""

    def __init__(self, context, request):
        """initialize"""
        self.context = context
        self.request = request

    def __call__(self, expand=True):
        "implementation"
        expand = True
        result = {
            "navroot": {"@id": f"{self.context.absolute_url()}/@navroot"}
        }
        if not expand:
            return result

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        result["navroot"].update(
            {
                "url": portal_state.navigation_root_url(),
                "title": portal_state.navigation_root_title(),
            }
        )

        return result


class NavrootGet(Service):
    """endpoint"""

    def reply(self):
        """reply"""
        navroot = Navroot(self.context, self.request)
        return navroot(expand=True)["navroot"]
