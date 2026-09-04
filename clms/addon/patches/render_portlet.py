"""Add authorization and input validation to plone.app.portlets render-portlet.

Temporary local hardening; remove once a later plone.app.portlets release
covers it
"""
# -*- coding: utf-8 -*-
from logging import getLogger

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from plone.app.portlets.browser.utils import PortletUtilities
from plone.app.portlets.utils import assignment_from_key
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.utils import unhashPortletInfo
from Products.CMFCore.utils import getToolByName


log = getLogger(__name__)

MANAGE_PORTLETS = "Portlets: Manage portlets"
FORBIDDEN_CLASSIC_CHARS = (":", "|")

_original_render_portlet = PortletUtilities.render_portlet


def _authorize(view, info):
    """Raise Unauthorized unless the caller may render this assignment."""
    context = view.context
    security = getSecurityManager()
    membership = getToolByName(context, "portal_membership")
    category = info.get("category")
    key = info.get("key")

    if category in (USER_CATEGORY, GROUP_CATEGORY):
        # Dashboard portlets are personal: only the owner or a portlet manager.
        if membership.isAnonymousUser():
            raise Unauthorized(
                "render-portlet: anonymous access to dashboard portlets is "
                "not allowed"
            )
        if security.checkPermission(MANAGE_PORTLETS, context):
            return
        member = membership.getAuthenticatedMember()
        if category == USER_CATEGORY and key == member.getId():
            return
        raise Unauthorized(
            "render-portlet: not authorized to render this dashboard portlet"
        )

    # context / content_type assignments: gate on View of the rendered object.
    elif not security.checkPermission("View", context):
        raise Unauthorized(
            "render-portlet: 'View' is required to render this portlet"
        )


def _validate_classic_fields(view, info):
    """Reject Classic template/macro values with disallowed characters."""
    try:
        assignment = assignment_from_key(
            context=view.context,
            manager_name=info["manager"],
            category=info["category"],
            key=info["key"],
            name=info["name"],
        )
    except Exception:
        # Leave resolution failures to the original implementation.
        return
    if assignment is None:
        return
    data = getattr(assignment, "data", assignment)
    for field in ("template", "macro"):
        value = getattr(data, field, None)
        if value and any(char in value for char in FORBIDDEN_CLASSIC_CHARS):
            raise Unauthorized(
                "render-portlet: invalid Classic portlet "
                "'{}' value".format(field)
            )


def render_portlet(self, portlethash, **kw):
    """Authorize and sanity-check before delegating to the original view."""
    info = unhashPortletInfo(portlethash)
    _authorize(self, info)
    _validate_classic_fields(self, info)
    return _original_render_portlet(self, portlethash, **kw)


PortletUtilities.render_portlet = render_portlet

log.info(
    "Hardened plone.app.portlets render-portlet "
    "(authorization + Classic field validation)"
)
