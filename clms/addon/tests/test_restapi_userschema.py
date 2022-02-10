""" @userschema endpoint tests. Taken from plone.restapi PR"""
# -*- coding: utf-8 -*-
import unittest

import transaction
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    setRoles,
)
from plone.app.users.setuphandlers import import_schema
from plone.restapi.testing import RelativeSession
from Products.GenericSetup.tests.common import DummyImportContext

from clms.addon.testing import CLMS_ADDON_RESTAPI_TESTING


class TestUserSchemaEndpoint(unittest.TestCase):
    """ test the @userschema endpoint. """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """ setup method"""
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        """ tear down"""
        self.api_session.close()

    def test_userschema_get(self):
        """ get the user schema which has been modified by the installation of this product"""
        response = self.api_session.get("/@userschema")

        self.assertEqual(200, response.status_code)
        response = response.json()

        self.assertIn("fullname", response["fieldsets"][0]["fields"])
        self.assertIn("email", response["fieldsets"][0]["fields"])
        self.assertIn("country", response["fieldsets"][0]["fields"])
        self.assertIn(
            "are_you_registering_on_behalf_on_an_organisation_",
            response["fieldsets"][0]["fields"],
        )
        self.assertIn(
            "how_do_you_intend_to_use_the_products",
            response["fieldsets"][0]["fields"],
        )
        self.assertIn(
            "professional_thematic_domain", response["fieldsets"][0]["fields"]
        )
        self.assertIn("organisation_url", response["fieldsets"][0]["fields"])
        self.assertIn("organisation_name", response["fieldsets"][0]["fields"])
        self.assertIn(
            "organisation_institutional_domain",
            response["fieldsets"][0]["fields"],
        )

        self.assertTrue("object", response["type"])


class TestCustomUserSchema(unittest.TestCase):
    """test userschema endpoint with a custom defined schema.
    we have taken the same example as in plone.app.users, thatç
    handles all kind of schema fields
    """

    layer = CLMS_ADDON_RESTAPI_TESTING

    def setUp(self):
        """ setup """
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        xml = """<model xmlns:lingua="http://namespaces.plone.org/supermodel/lingua" xmlns:users="http://namespaces.plone.org/supermodel/users" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns="http://namespaces.plone.org/supermodel/schema" i18n:domain="plone">
  <schema name="member-fields">
    <field name="home_page" type="zope.schema.URI" users:forms="In User Profile">
      <description i18n:translate="help_homepage">
          The URL for your external home page, if you have one.
      </description>
      <required>False</required>
      <title i18n:translate="label_homepage">Home Page</title>
    </field>
    <field name="description" type="zope.schema.Text" users:forms="In User Profile">
      <description i18n:translate="help_biography">
          A short overview of who you are and what you do. Will be displayed
          on your author page, linked from the items you create.
      </description>
      <required>False</required>
      <title i18n:translate="label_biography">Biography</title>
    </field>
    <field name="location" type="zope.schema.TextLine" users:forms="In User Profile">
      <description i18n:translate="help_location">
          Your location - either city and country - or in
          a company setting, where your office is located.
      </description>
      <required>False</required>
      <title i18n:translate="label_biography">Location</title>
    </field>
    <field name="portrait" type="plone.namedfile.field.NamedBlobImage" users:forms="In User Profile">
      <description i18n:translate="help_portrait">
          To add or change the portrait: click the "Browse" button; select a
          picture of yourself. Recommended image size is 75 pixels wide by
          100 pixels tall.
      </description>
      <required>False</required>
      <title i18n:translate="label_portrait">Portrait</title>
    </field>
    <field name="birthdate" type="zope.schema.Date" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Birthdate</title>
    </field>
    <field name="another_date" type="zope.schema.Datetime" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Another date</title>
    </field>
    <field name="age" type="zope.schema.Int" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Age</title>
    </field>
    <field name="department" type="zope.schema.Choice" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Department</title>
      <values>
        <element>Marketing</element>
        <element>Production</element>
        <element>HR</element>
      </values>
    </field>
    <field name="skills" type="zope.schema.Set" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Skills</title>
      <value_type type="zope.schema.Choice">
        <values>
          <element>Programming</element>
          <element>Management</element>
        </values>
      </value_type>
    </field>
    <field name="pi" type="zope.schema.Float" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Pi</title>
    </field>
    <field name="vegetarian" type="zope.schema.Bool" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Vegetarian</title>
    </field>
  </schema>
</model>
"""
        context = DummyImportContext(self.portal, purge=False)
        context._files = {"userschema.xml": xml}
        import_schema(context)
        transaction.commit()

    def tearDown(self):
        """ tear down """
        self.api_session.close()

    def test_userschema_get(self):
        """ get the user schema"""
        response = self.api_session.get("/@userschema")

        self.assertEqual(200, response.status_code)
        response = response.json()
        # Default fields
        self.assertIn("fullname", response["fieldsets"][0]["fields"])
        self.assertIn("email", response["fieldsets"][0]["fields"])
        self.assertIn("home_page", response["fieldsets"][0]["fields"])
        self.assertIn("description", response["fieldsets"][0]["fields"])
        self.assertIn("location", response["fieldsets"][0]["fields"])

        # added fields
        self.assertIn("portrait", response["fieldsets"][0]["fields"])
        self.assertIn("birthdate", response["fieldsets"][0]["fields"])
        self.assertIn("another_date", response["fieldsets"][0]["fields"])
        self.assertIn("age", response["fieldsets"][0]["fields"])
        self.assertIn("department", response["fieldsets"][0]["fields"])
        self.assertIn("skills", response["fieldsets"][0]["fields"])
        self.assertIn("pi", response["fieldsets"][0]["fields"])
        self.assertIn("vegetarian", response["fieldsets"][0]["fields"])