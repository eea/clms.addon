""" @dataset_by_uid endpoint tests tests """
# -*- coding: utf-8 -*-
import unittest

from plone import api
from clms.addon.testing import CLMS_ADDON_RESTAPI_TESTING  # noqa: E501
from plone.app.testing import TEST_USER_ID, setRoles
from plone.restapi.testing import RelativeSession
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

import transaction


class TestDatasetSearch(unittest.TestCase):
    """Test for @dataset_by_uid endpoint"""

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.portal.invokeFactory("Document", id="doc1", title="My Document")
        self.portal.invokeFactory("Document", id="doc2", title="My Document")

        self.doc1 = self.portal["doc1"]
        self.doc2 = self.portal["doc2"]

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        transaction.commit()

    def test_endpoint_allows_list_like_searches(self):
        """the whole idea of the endpoint is to support searching multiple
        values at once, receiving a list of possible values as a
        parameter, something like UID=a1,a2,a3
        """
        response = self.api_session.get(
            "@datasets_by_uid?UID=%s,%s" % (self.doc1.UID(), self.doc2.UID())
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

        results = response.json()
        self.assertEqual(results["items_total"], len(results["items"]))
        self.assertEqual(results["items_total"], 2)

        self.assertIn(
            self.doc1.UID(), [item["UID"] for item in results["items"]]
        )
        self.assertIn(
            self.doc2.UID(), [item["UID"] for item in results["items"]]
        )

    def test_endpoint_allows_list_like_searches_parameter_multiple_times(self):
        """the whole idea of the endpoint is to support searching multiple
        values at once, receiving a list of possible values as a
        parameter, something like UID=a1&UID=a2&UID=a3
        """
        response = self.api_session.get(
            "@datasets_by_uid?UID=%s&UID=%s"
            % (self.doc1.UID(), self.doc2.UID())
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "application/json"
        )

        results = response.json()
        self.assertEqual(results["items_total"], len(results["items"]))
        self.assertEqual(results["items_total"], 2)

        self.assertIn(
            self.doc1.UID(), [item["UID"] for item in results["items"]]
        )
        self.assertIn(
            self.doc2.UID(), [item["UID"] for item in results["items"]]
        )
