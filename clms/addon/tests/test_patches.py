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
