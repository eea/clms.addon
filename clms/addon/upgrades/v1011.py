""" upgrade step implementation """
# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from zope.component import getMultiAdapter

import json
from logging import getLogger
from urllib.parse import urlparse

from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import (
    SlateBlockTransformer,
    iterate_children,
)
from plone.restapi.deserializer.utils import path2uid
from plone.restapi.interfaces import (
    IBlockFieldDeserializationTransformer,
    IDeserializeFromJson,
)
from zope.component import (
    adapter,
    getGlobalSiteManager,
    getMultiAdapter,
    provideSubscriptionAdapter,
)
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from clms.addon.utils import CLMS_DOMAINS

logger = getLogger(__name__)

OK = 1
ERROR = 2


green = "\033[32m"
red = "\033[31m"

reset = "\033[0m"


def path2title(context, link):
    """use the origina path2uid to get the objects Title"""
    # unrestrictedTraverse requires a string on py3. see:
    # https://github.com/zopefoundation/Zope/issues/674
    if not link:
        return ""
    portal = getMultiAdapter(
        (context, context.REQUEST), name="plone_portal_state"
    ).portal()
    portal_url = portal.portal_url()
    portal_path = "/".join(portal.getPhysicalPath())
    path = link
    context_url = context.absolute_url()
    relative_up = len(context_url.split("/")) - len(portal_url.split("/"))
    if path.startswith(portal_url):
        path = path[len(portal_url)+1:]
    if not path.startswith(portal_path):
        path = "{portal_path}/{path}".format(
            portal_path=portal_path, path=path.lstrip("/")
        )
    obj = portal.unrestrictedTraverse(path, None)
    if obj is None or obj == portal:
        return ""
    segments = path.split("/")
    suffix = ""
    while not IUUIDAware.providedBy(obj):
        obj = aq_parent(obj)
        if obj is None:
            break
        suffix += "/" + segments.pop()
    # check if obj is wrong because of acquisition
    if not obj or "/".join(obj.getPhysicalPath()) != "/".join(segments):
        return ""

    return obj.Title()


def is_url_in_portal(url):
    """check if this URL is in portal"""
    portal_url = api.portal.get_tool("portal_url")
    if portal_url.isURLInPortal(url):
        return True

    # Let's handle this manually
    if url.startswith("http"):
        parsed = urlparse(url)
        if parsed.hostname in CLMS_DOMAINS:
            # This could be an internal link
            return True

        if url.startswith(".") or url.startswith("/"):
            # Explicit internal links starting with .. or /
            return True

    return False


def remove_domain(url):
    """remove domain from URL and return only the path"""
    parsed = urlparse(url)
    return parsed.path


def transform_external_links(context, value):
    """check if the link is marked as an external link, if so, check if it is
    really external such as checking that starts with portal_url, if so,
    convert it to internal
    """
    data = value.get("data", {})
    if data.get("link", {}).get("external", {}).get("external_link"):
        external_link = data["link"]["external"]["external_link"]
        # logger.info(f"{green}External link{reset}: %s", external_link)
        explicit_target = data["link"]["external"].get("target", None)
        # If an external link that points to the current portal has an explicit
        # target, means that it has been entered on purpose as external to be
        # opened in a new window, so we need to leave it as it is
        if explicit_target in [None, "_self"]:
            if is_url_in_portal(external_link):
                # We need to remove the external link marker and mark it as
                # an internal
                external_link_without_domain = remove_domain(external_link)
                # remove leading ../ and add a leading /
                external_link_without_domain = (
                    external_link_without_domain.replace("../", "")
                )
                external_link_without_domain = (
                    f"/{external_link_without_domain}"
                )
                # Remove trailing /@@download/file
                external_link_without_domain = (
                    external_link_without_domain.replace(
                        "/@@download/file", ""
                    )
                )

                uid_link = path2uid(context, external_link_without_domain)
                uid_title = path2title(context, external_link_without_domain)

                data["link"]["internal"] = {
                    "internal_link": [{"@id": uid_link, "title": uid_title}]
                }
                del data["link"]["external"]
                logger.info(
                    f"{green}%s. External -> internal:{reset} %s -> %s",
                    context.absolute_url(),
                    external_link,
                    uid_link,
                )

        if "url" in value:
            logger.info(
                f"{green}%s. Remove wrong url:{reset} %s ",
                context.absolute_url(),
                value["url"],
            )
            del value["url"]

    # if data.get("link", {}).get("internal", {}).get("internal_link"):
    #     internal_link = data["link"]["internal"]["internal_link"]
    #     for link in internal_link:
    #         link["@id"] = transformer(context, link["@id"])


def transform_internal_links_to_uid(context, value):
    """check if the link is marked as an internal link, if so, check if it is
    really internal (it uses resolveuid) or it contains a URL.
    If it contains a URL, convert it to a uid
    """
    data = value.get("data", {})
    if data.get("link", {}).get("internal", {}).get("internal_link"):
        internal_links = data["link"]["internal"]["internal_link"]
        new_internal_links = []
        for internal_link in internal_links:
            internal_link_url = internal_link.get("@id")
            if internal_link_url.find("resolveuid") == -1:
                # it doesn't contain the resolveuid marker,
                # we have to convert it.
                if is_url_in_portal(internal_link_url):
                    internal_link_url_without_domain = remove_domain(
                        internal_link_url
                    )
                    # remove leading ../ and add a leading /
                    internal_link_url_without_domain = (
                        internal_link_url_without_domain.replace("../", "")
                    )
                    internal_link_url_without_domain = (
                        f"/{internal_link_url_without_domain}"
                    )
                    # Remove trailing /@@download/file
                    internal_link_url_without_domain = (
                        internal_link_url_without_domain.replace(
                            "/@@download/file", ""
                        )
                    )
                    import pdb

                    pdb.set_trace()
                    if internal_link_url_without_domain.startswith("//"):
                        internal_link_url_without_domain = (
                            internal_link_url_without_domain.replace("//", "/")
                        )

                    if internal_link_url_without_domain.startswith("/api"):
                        internal_link_url_without_domain = (
                            internal_link_url_without_domain.replace(
                                "/api", "/"
                            )
                        )
                    uid_link = path2uid(
                        context, internal_link_url_without_domain
                    )
                    uid_title = path2title(
                        context, internal_link_url_without_domain
                    )

                    new_internal_links.append(
                        {"@id": uid_link, "title": uid_title}
                    )

                    logger.info(
                        f"{green}%s. External -> internal:{reset} %s -> %s",
                        context.absolute_url(),
                        internal_link_url,
                        uid_link,
                    )
                else:
                    new_internal_links.append(internal_link)
            else:
                new_internal_links.append(internal_link)

        data["link"]["internal"] = {"internal_link": new_internal_links}


@implementer(IBlockFieldDeserializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateBlockExternalLinkDetector(SlateBlockTransformer):
    """a deserializer to detect external links and fix them
    if they are internal
    """

    field = "value"
    order = 200
    block_type = "slate"

    def handle_a(self, child):
        """handle a type nodes"""
        transform_external_links(self.context, child)
        transform_internal_links_to_uid(self.context, child)


def deserialize(blocks=None, validate_all=False, context=None):
    blocks = blocks or ""
    request = getRequest()
    request["BODY"] = json.dumps({"blocks": blocks})
    deserializer = getMultiAdapter((context, request), IDeserializeFromJson)
    return deserializer(validate_all=validate_all)


def upgrade_links_in_object(item):
    try:
        deserialize(blocks=item.blocks, context=item)
        return OK
    except Exception as e:
        return ERROR


def upgrade_links():
    provideSubscriptionAdapter(
        SlateBlockExternalLinkDetector,
        (IBlocks, IBrowserRequest),
    )

    brains = api.content.find(context=api.portal.get(), Language="en")
    for brain in brains:
        obj = brain.getObject()
        if IBlocks.providedBy(obj):
            upgrade_links_in_object(brain.getObject())

    sm = getGlobalSiteManager()
    sm.adapters.unsubscribe(
        (IBlocks, IBrowserRequest),
        IBlockFieldDeserializationTransformer,
        SlateBlockExternalLinkDetector,
    )


def upgrade(setup_tool=None):
    """upgrade function"""
    logger.info("Running upgrade (Python): v1011")
    upgrade_links()
    logger.info("done")
