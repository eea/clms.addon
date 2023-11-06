"""
Patch @contextnavigation endpoint to expose blocks and blocks_layout
"""
# -*- coding: utf-8 -*-
from logging import getLogger
import copy


from plone.restapi.services.contextnavigation.get import (
    NavigationPortletRenderer,
)
from plone.restapi.serializer.blocks import (
    apply_block_serialization_transforms,
)

def own_recurse(self, children, level, bottomLevel):
    """ recursion"""

    res = []

    show_thumbs = not self.data.no_thumbs
    show_icons = not self.data.no_icons

    thumb_scale = self.thumb_scale()

    for node in children:
        brain = node["item"]

        icon = ""

        if show_icons:
            if node["portal_type"] == "File":
                icon = self.getMimeTypeIcon(node)

        has_thumb = brain.getIcon
        thumb = ""

        if show_thumbs and has_thumb and thumb_scale:
            thumb = "{}/@@images/image/{}".format(
                node["item"].getURL(), thumb_scale
            )

        show_children = node["show_children"]
        item_remote_url = node["getRemoteUrl"]
        use_remote_url = node["useRemoteUrl"]
        item_url = node["getURL"]

        value = copy.deepcopy(brain.getObject().blocks)

        for id, block_value in value.items():
            value[id] = apply_block_serialization_transforms(
                block_value, self.context
            )

        item = {
            "@id": item_url,
            "description": node["Description"],
            "href": item_remote_url if use_remote_url else item_url,
            "icon": icon,
            "is_current": node["currentItem"],
            "is_folderish": node["show_children"],
            "is_in_path": node["currentParent"],
            "items": [],
            "normalized_id": node["normalized_id"],
            "review_state": node["review_state"] or "",
            "thumb": thumb,
            "title": node["Title"],
            "type": node["normalized_portal_type"],
            "blocks": value,
            "blocks_layout": brain.getObject().blocks_layout,
        }

        if node.get("nav_title", False):
            item.update({"title": node["nav_title"]})

        nodechildren = node["children"]

        # pylint: disable=line-too-long
        if (nodechildren and show_children and ((level < bottomLevel) or (bottomLevel == 0))):  # noqa
            item["items"] = self.recurse(
                nodechildren, level=level + 1, bottomLevel=bottomLevel
            )

        res.append(item)

    return res


NavigationPortletRenderer.recurse = own_recurse


log = getLogger(__name__)


log.info(
    "Patched @contextnavigation endpoint to include blocks and blocks_layout"
    " attributes"
)
