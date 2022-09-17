""" patch transfor_links from plone.restapi"""
# -*- coding: utf-8 -*-
# from plone.restapi.deserializer import blocks as des_blocks
from plone.restapi.serializer import blocks as ser_blocks
from logging import getLogger
from plone.outputfilters.browser.resolveuid import uuidToObject
from clms.addon.utils import DIRECT_LINK_PORTAL_TYPES
import re


RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


def my_transform_links(context, value, transformer):
    """ handle internal and external links"""

    data = value.get("data", {})
    if data.get("link", {}).get("internal", {}).get("internal_link"):
        internal_link = data["link"]["internal"]["internal_link"]
        for link in internal_link:
            url, target = uid_to_obj_url(link["@id"])
            if url:
                link['@id'] = url
                if target:
                    link['target'] = "_blank"
            else:
                link["@id"] = transformer(context, link["@id"])

    if data.get("link", {}).get("external", {}).get("external_link"):
        external_link = data["link"]["external"]
        external_link['target'] = "_blank"


log = getLogger(__name__)

# des_blocks.transform_links = my_transform_links
# log.info('Patched plone.restapi.deserializer.blocks.transform_links')

ser_blocks.transform_links = my_transform_links
log.info('Patched plone.restapi.serializer.blocks.transform_links')


def uid_to_obj_url(path):
    """ return the URL of an object, and if it
        should be opened in a new tab"""
    if not path:
        return "", False
    match = RESOLVEUID_RE.match(path)
    if match is None:
        return path, False

    uid, suffix = match.groups()
    target_object = uuidToObject(uid)

    if target_object:
        if target_object.portal_type in DIRECT_LINK_PORTAL_TYPES:
            return f'{target_object.absolute_url()}/@@download/file', True

        if suffix:
            return target_object.absolute_url() + suffix, False

        return target_object.absolute_url(), False
