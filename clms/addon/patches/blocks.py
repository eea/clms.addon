# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from logging import getLogger

from plone.restapi.serializer import blocks

from .restapi import my_uid_to_url


def my__call__(self, value):
    for field in self.fields:
        if field in value.keys():
            link = value.get(field, "")
            if isinstance(link, str):
                value[field] = my_uid_to_url(link)
            elif isinstance(link, list):
                if (
                    len(link) > 0
                    and isinstance(link[0], dict)
                    and "@id" in link[0]
                ):
                    result = []
                    for item in link:
                        item_clone = deepcopy(item)
                        item_clone["@id"] = my_uid_to_url(item_clone["@id"])
                        result.append(item_clone)

                    value[field] = result
                elif len(link) > 0 and isinstance(link[0], str):
                    value[field] = [my_uid_to_url(item) for item in link]
    return value


blocks.ResolveUIDSerializerBase.__call__ = my__call__

log = getLogger(__name__)
log.info("Patched plone.restapi.serializer.blocks.ResolveUIDSerializerBase")
