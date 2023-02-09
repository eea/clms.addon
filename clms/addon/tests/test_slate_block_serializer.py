""" tesst for specific slate block serializer"""
# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.dexterity.utils import iterSchemata
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IFieldSerializer
from plone.uuid.interfaces import IUUID
from z3c.form.interfaces import IDataManager
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import provideSubscriptionAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

from clms.addon.testing import CLMS_ADDON_INTEGRATION_TESTING

import unittest


class TextSlateExternalLinkBlockSerializerBase(unittest.TestCase):
    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.portal.invokeFactory("Document", id="doc1")
        self.image = self.portal[
            self.portal.invokeFactory(
                "Image", id="image-1", title="Target image"
            )
        ]

    def serialize(self, context, blocks):
        fieldname = "blocks"
        field = None
        for schema in iterSchemata(context):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        if field is None:
            raise ValueError("blocks field not in the schema of %s" % context)
        dm = getMultiAdapter((context, field), IDataManager)
        dm.set(blocks)
        serializer = getMultiAdapter(
            (field, context, self.request), IFieldSerializer
        )
        return serializer()

    def test_external_link_without_target(self):
        """test that when we have an external link without an explicit target
        the serializer sets '_blank' as its target
        """
        external_link = {"external_link": "https://www.google.com"}

        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [
                                            {"text": "slate external link"}
                                        ],
                                        "data": {
                                            "link": {"external": external_link}
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }

        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )

        value = res["2caef9e6-93ff-4edf-896f-8c16654a9923"]["value"]
        link = value[0]["children"][1]["children"][1]

        target = link["data"]["link"]["external"].get("target", None)
        self.assertIsNotNone(target)
        self.assertEqual(target, "_blank")

    def test_external_link_with_target(self):
        """test that when we have an external link with an explicit target
        the serializer leaves the target as it is
        """
        target_text = "_whatever"
        external_link = {
            "external_link": "https://www.google.com",
            "target": target_text,
        }

        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [
                                            {"text": "slate external link"}
                                        ],
                                        "data": {
                                            "link": {"external": external_link}
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }

        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )

        value = res["2caef9e6-93ff-4edf-896f-8c16654a9923"]["value"]
        link = value[0]["children"][1]["children"][1]

        link_target = link["data"]["link"]["external"].get("target", None)
        self.assertIsNotNone(link_target)
        self.assertEqual(link_target, target_text)
