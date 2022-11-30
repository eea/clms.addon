""" patch transfor_links from plone.restapi"""
# -*- coding: utf-8 -*-
# from plone.restapi.deserializer import blocks as des_blocks
import re
from logging import getLogger

from clms.addon.utils import DIRECT_LINK_PORTAL_TYPES
from plone import api
from plone.outputfilters.browser.resolveuid import uuidToObject
from plone.restapi.serializer import blocks as ser_blocks

RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


def my_transform_links(context, value, transformer):
    """handle internal and external links"""
    data = value.get("data", {})
    if data.get("link", {}).get("internal", {}).get("internal_link"):
        internal_link = data["link"]["internal"]["internal_link"]
        for link in internal_link:
            url, target = uid_to_obj_url(link["@id"])
            if url:
                link["@id"] = url
                if target:
                    # We set to open in a new tab when
                    # the previous function has returned True
                    # That function checks if the item is downloadable
                    link["target"] = "_blank"
            else:
                link["@id"] = transformer(context, link["@id"])

    if data.get("link", {}).get("external", {}).get("external_link"):
        external_link = data["link"]["external"]
        if "target" not in external_link:
            # Open external links by default in new tabs
            # If they have some kind of target set manually
            # we leave it as it is
            external_link["target"] = "_blank"


def my_uid_to_url(path):
    """uid to url"""
    return uid_to_obj_url(path)[0]


log = getLogger(__name__)


ser_blocks.transform_links = my_transform_links
log.info("Patched plone.restapi.serializer.blocks.transform_links")


def uid_to_obj_url(path):
    """return the URL of an object, and if it
    should be opened in a new tab checking its content-type"""
    if not path:
        return "", False
    match = RESOLVEUID_RE.match(path)
    if match is None:
        return resolve_path_to_obj_url(path)

    uid, suffix = match.groups()
    target_object = uuidToObject(uid)

    if target_object:
        if target_object.portal_type in DIRECT_LINK_PORTAL_TYPES:
            return (
                "{}/@@download/file".format(
                    remove_portal_url_from_url(target_object.absolute_url())
                ),
                True,
            )

        if suffix:
            return (
                remove_portal_url_from_url(
                    target_object.absolute_url() + suffix
                ),
                False,
            )

        return remove_portal_url_from_url(target_object.absolute_url()), False

    return "", False


def remove_portal_url_from_url(url):
    """replace the portal_url from url"""
    portal_url = api.portal.get().absolute_url()
    value = url.replace(portal_url, "")
    if value.startswith("/api/"):
        value = value.replace("/api/, " / "")

    return value


def resolve_path_to_obj_url(path):
    """try to resolve the path as if it was a Plone object path"""
    portal = api.portal.get()
    portal_url = portal.absolute_url()
    # Replace the /api marker
    if portal_url.endswith("/api"):
        portal_url = portal_url.replace("/api", "")

    # Is an absolute URL with http?
    if path.startswith("http"):
        if path.startswith("http://backend:8080/Plone/"):
            path = path.replace("http://backend:8080/Plone", portal_url)
        # Check if it ends with a download marker
        if path.endswith("@@download/file"):
            return remove_portal_url_from_url(path), True

        if path.startswith(portal_url):
            # This is a portal_url entered as if it was an external link
            # So remove the domain part, and try to find the object in the DB
            newpath = path.replace(portal_url, "")
            newpath = f"/{portal.getId()}" + newpath

            url, newwindow = find_path_url_in_catalog(newpath)
            if url is not None:
                return remove_portal_url_from_url(url), newwindow

        return remove_portal_url_from_url(path), False

    if path.startswith("/"):
        # This is an absolute path to an object in the DB
        # Try to get the object and render the link
        newpath = path
        if not path.startswith(f"/{portal.getId()}"):
            newpath = f"/{portal.getId()}" + path

        url, newwindow = find_path_url_in_catalog(newpath)

        if url is not None:
            return remove_portal_url_from_url(url), newwindow

    return path, False


def find_path_url_in_catalog(path):
    """find the given path in the catalog, and return the object
    url and whether it should be opened in a new window"""
    brains = api.content.find(path=path)
    if brains:
        for brain in brains:
            target_object = brain.getObject()
            if target_object.portal_type in DIRECT_LINK_PORTAL_TYPES:
                return (
                    f"{target_object.absolute_url()}/@@download/file",
                    True,
                )

            return target_object.absolute_url(), False

    return None, False
