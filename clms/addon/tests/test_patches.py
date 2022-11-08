""" tests
"""
# -*- coding: utf-8 -*-
import unittest

from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING  # noqa: E501
from clms.addon.patches.restapi import (
    find_path_url_in_catalog,
    resolve_path_to_obj_url,
    uid_to_obj_url,
)
from plone.app.testing import (
    TEST_USER_ID,
    setRoles,
)
from plone import api


class TestPaches(unittest.TestCase):
    """some tests for the restapi link handling patches"""

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.folder = api.content.create(
            type="Document", id="folder", container=self.portal
        )
        self.document = api.content.create(
            type="Document", id="document", container=self.folder
        )
        self.file = api.content.create(
            type="File", id="file", container=self.folder
        )

    def test_find_path_url_in_catalog_with_document(self):
        """test the find_path_url_in_catalog"""
        path = "/folder/document"

        url, download = find_path_url_in_catalog(
            f"/{self.portal.getId()}" + path
        )
        self.assertTrue(url, self.document.absolute_url())
        self.assertFalse(download)

    def test_find_path_url_in_catalog_with_file(self):
        """test the find_path_url_in_catalog"""
        path = "/folder/file"
        url, download = find_path_url_in_catalog(
            f"/{self.portal.getId()}" + path
        )

        self.assertTrue(url, self.document.absolute_url() + "/@@download/file")
        self.assertTrue(download)

    def test_find_path_url_in_catalog_unkown(self):
        """test with an unknown item"""
        path = "/this/is/unkown"
        url, download = find_path_url_in_catalog(path)

        self.assertEqual(url, None)
        self.assertFalse(download)

    def test_resolve_path_to_obj_url_folder(self):
        """test resolve_path_to_obj_url function"""
        path = "/folder"

        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(url, self.folder.absolute_url())
        self.assertFalse(download)

    def test_resolve_path_to_obj_url_page(self):
        """test resolve_path_to_obj_url function"""
        path = "/folder/document"
        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(url, self.document.absolute_url())
        self.assertFalse(download)

    def test_resolve_path_to_obj_url_file(self):
        """test resolve_path_to_obj_url function"""
        path = "/folder/file"
        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(url, self.file.absolute_url() + "/@@download/file")
        self.assertTrue(download)

    def test_resolve_path_to_obj_url_unkown(self):
        """test resolve_path_to_obj_url function"""
        path = "/this/is/unknown"
        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(path, url)
        self.assertFalse(download)

    def test_resolve_path_to_obj_url_http(self):
        """test resolve_path_to_obj_url function"""
        path = "http://www.google.com"
        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(path, url)
        self.assertFalse(download)

    def test_resolve_path_to_obj_url_http_folder(self):
        """test resolve_path_to_obj_url function"""
        path = self.folder.absolute_url()
        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(path, url)
        self.assertFalse(download)

    def test_resolve_path_to_obj_url_http_file(self):
        """test resolve_path_to_obj_url function"""
        path = self.file.absolute_url()
        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(url, path + "/@@download/file")
        self.assertTrue(download)

    def test_resolve_path_to_obj_url_http_file_download(self):
        """test resolve_path_to_obj_url function"""
        path = self.file.absolute_url() + "/@@download/file"
        url, download = resolve_path_to_obj_url(path)
        self.assertEqual(url, path)
        self.assertTrue(download)

    def test_uid_to_obj_url_folder(self):
        """test the uid_to_obj_url function"""
        uid = api.content.get_uuid(self.folder)
        path = f"./resolveuid/{uid}"

        url, download = uid_to_obj_url(path)
        self.assertEqual(url, self.folder.absolute_url())
        self.assertFalse(download)

    def test_uid_to_obj_url_file(self):
        """test the uid_to_obj_url function"""
        uid = api.content.get_uuid(self.file)
        path = f"./resolveuid/{uid}"

        url, download = uid_to_obj_url(path)
        self.assertEqual(url, self.file.absolute_url() + "/@@download/file")
        self.assertTrue(download)

    def test_uid_to_obj_url_emtpy(self):
        """test with an empty string"""
        url, download = uid_to_obj_url("")
        self.assertEqual(url, "")
        self.assertFalse(download)

    def test_uid_to_obj_url_none(self):
        """test with none"""
        url, download = uid_to_obj_url(None)
        self.assertEqual(url, "")
        self.assertFalse(download)

    def test_uid_to_obj_url_no_uid_folder(self):
        """test withouth passing a uid but a folder url"""
        path = "/folder/document"
        url, download = uid_to_obj_url(path)
        self.assertEqual(url, self.document.absolute_url())
        self.assertFalse(download)

    def test_uid_to_obj_url_no_uid_file(self):
        """test withouth passing a uid but a file url"""
        path = "/folder/file"
        url, download = uid_to_obj_url(path)
        self.assertEqual(url, self.file.absolute_url() + "/@@download/file")
        self.assertTrue(download)

    def test_uid_to_obj_url_no_uid_unknown(self):
        """test withouth passing a uid but an unknown url"""
        path = "/this/is/unknown"
        url, download = uid_to_obj_url(path)
        self.assertEqual(path, url)
        self.assertFalse(download)
