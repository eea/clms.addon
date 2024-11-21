"""
Cleanup: find unused images
"""

from Products.Five.browser import BrowserView
from zope.schema import getFieldsInOrder
from plone.dexterity.utils import iterSchemata
from plone.app.uuid.utils import uuidToObject
import re
from logging import getLogger


def convert_uid_to_path(uid):
    """Return url for resolve uid item"""
    try:
        obj = uuidToObject(uid)
        path = obj.absolute_url()
        return path
    except Exception:
        return None


resolveuid_pattern = re.compile(r"resolveuid/([a-f0-9]{32})")


def extract_urls(text):
    """Extract urls from text"""
    urls = re.findall(r'["\'](https?://\S+)["\']', text)

    return urls


def extract_resolveuids(text):
    """Extract uid from resolve uid str"""
    return resolveuid_pattern.findall(text)


def get_all_images_urls(catalog):
    """Prepare a dict containing all images from website
    images_dict: {
         'http....image.png': False,
         'image.png': False,
         ...
     }

     original: {
         'image.png': 'http....image.png',
         ...
     }
    """
    images = catalog(portal_type="Image")
    images_urls = [brain.getURL() for brain in images]
    images_dict = {}

    original = {}
    for url in images_urls:
        filename = url.split("/")[-1]
        images_dict[url] = False
        images_dict[filename] = False
        original[filename] = url
    return {"images_dict": images_dict, "original": original}


def is_img_used(images_dict, original, path, context):
    """Search for given path in images_dict"""
    if path in images_dict:
        if "//" in path:
            return (True, path)
        return (True, original[path])

    return (False, None)


class FindUnusedImages(BrowserView):
    """Callback view"""

    def __call__(self):
        """custom __call__ method"""
        catalog = self.context.portal_catalog
        images = get_all_images_urls(catalog)
        images_dict = images["images_dict"]
        original = images["original"]

        all_brains = catalog()
        for brain in all_brains:
            try:
                obj = brain.getObject()
            except Exception:
                continue

            try:
                if obj.portal_type == "Image":
                    continue
            except Exception:
                continue

            for schema in iterSchemata(obj):
                for k, v in getFieldsInOrder(schema):
                    if k != "blocks":
                        if "file" in str(v) or "image" in str(v):
                            value = getattr(obj, k, None)
                            if value is not None:
                                try:
                                    res = is_img_used(
                                        images_dict, original,
                                        value.filename, obj
                                    )
                                    if res[0]:
                                        images_dict[res[1]] = True
                                except Exception:
                                    pass
                        continue
                    value = getattr(obj, k, None)

                    if k == "blocks" and isinstance(value, dict):
                        for block in value.values():
                            if block.get("@type", None) is not None:
                                if block["@type"] == "image":
                                    try_url = block.get("url", None)
                                    if try_url is not None:
                                        if "resolveuid" in try_url:
                                            uids = extract_resolveuids(try_url)
                                            if uids:
                                                for uid in uids:
                                                    path = convert_uid_to_path(
                                                        uid)
                                                    if path is None:
                                                        continue
                                                    res = is_img_used(
                                                        images_dict, original,
                                                        path, obj
                                                    )
                                                    if res[0]:
                                                        images_dict[res[1]
                                                                    ] = True
                                        else:
                                            try_path = try_url.split("/")[-1]
                                            res = is_img_used(
                                                images_dict, original,
                                                try_path, obj
                                            )
                                            if res[0]:
                                                images_dict[res[1]] = True

                            block_str = str(block)
                            uids = extract_resolveuids(block_str)
                            if uids:
                                for uid in uids:
                                    path = convert_uid_to_path(uid)
                                    if path is None:
                                        continue
                                    res = is_img_used(
                                        images_dict, original, path, obj)
                                    if res[0]:
                                        images_dict[res[1]] = True

                            urls = extract_urls(block_str)
                            if urls:
                                for url in urls:
                                    res = is_img_used(
                                        images_dict, original, url, obj)
                                    if res[0]:
                                        images_dict[res[1]] = True

                                    try_path = url.split("/")[-1]
                                    res = is_img_used(
                                        images_dict, original, try_path, obj
                                    )
                                    if res[0]:
                                        images_dict[res[1]] = True

        final_dict = {key: value for key,
                      value in images_dict.items() if "//" in key}
        # used_images = [
        # path for path, is_used in final_dict.items() if is_used]
        unused_images = [
            path
            for path, is_used in final_dict.items()
            if not is_used and "/assets/" not in path
        ]
        # print("NOT USED", unused_images)
        # print("NOT USED", len(unused_images))
        log = getLogger(__name__)
        log.info(unused_images)
        # print("USED", len(used_images))

        return unused_images
