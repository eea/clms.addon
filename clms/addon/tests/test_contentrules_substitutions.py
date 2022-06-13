""" test string interpolation substitutions for content rules """
# -*- coding: utf-8 -*-
import unittest

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from plone.stringinterp.interfaces import IStringInterpolator
from zope.component import getUtility

from clms.addon.contentrules.event_email_substitution import (
    EventSubscriberSubstitution,
)
from clms.addon.contentrules.newsitem_email_substitution import (
    NewsItemSubscriberSubstitution,
)
from clms.addon.contentrules.volto_portal_url import VoltoPortalURLSubstitution
from clms.addon.contentrules.volto_url_substitution import VoltoURLSubstitution
from clms.addon.testing import (
    CLMS_ADDON_FUNCTIONAL_TESTING,
    CLMS_ADDON_INTEGRATION_TESTING,
)
from clms.addon.utilities.event_notifications_utility import (
    IEventNotificationsUtility,
)
from clms.addon.utilities.newsitem_notifications_utility import (
    INewsItemNotificationsUtility,
)


class TestSubstitutions(unittest.TestCase):
    """ Test case for substitutions"""

    layer = CLMS_ADDON_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_newsitem_notification_subscribers(self):
        """ test for newsitem_notification_subscribers"""
        substitution = NewsItemSubscriberSubstitution(self.portal)()
        self.assertEqual(substitution, "")

        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("one@example.com")
        utility.subscribe_address("two@example.com")
        substitution = NewsItemSubscriberSubstitution(self.portal)()
        self.assertEqual(substitution, "one@example.com,two@example.com")

    def test_event_notification_subscribers(self):
        """ test for event_notification_subscribers"""

        substitution = EventSubscriberSubstitution(self.portal)()
        self.assertEqual(substitution, "")

        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("one@example.com")
        utility.subscribe_address("two@example.com")
        substitution = EventSubscriberSubstitution(self.portal)()
        self.assertEqual(substitution, "one@example.com,two@example.com")

    def test_volto_portal_url(self):
        """ test for volto_portal_url"""

        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        substitution = VoltoPortalURLSubstitution(self.portal)()
        self.assertEqual(substitution, volto_url)

    def test_string_interpolation_newsitem_subscribers(self):
        """ test interpolatin as string """
        string = "${newsitem_notification_subscribers}"
        value = IStringInterpolator(self.portal)(string)
        self.assertEqual(value, "")

        utility = getUtility(INewsItemNotificationsUtility)
        utility.subscribe_address("one@example.com")
        utility.subscribe_address("two@example.com")

        value = IStringInterpolator(self.portal)(string)
        self.assertEqual(value, "one@example.com,two@example.com")

    def test_string_interpolation_event_subscribers(self):
        """ test interpolatin as string """
        string = "${event_notification_subscribers}"
        value = IStringInterpolator(self.portal)(string)
        self.assertEqual(value, "")

        utility = getUtility(IEventNotificationsUtility)
        utility.subscribe_address("one@example.com")
        utility.subscribe_address("two@example.com")

        value = IStringInterpolator(self.portal)(string)
        self.assertEqual(value, "one@example.com,two@example.com")

    def test_string_interpolation_volto_portal_url(self):
        """ test interpolatin as string """
        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        string = "${volto_portal_url}"
        value = IStringInterpolator(self.portal)(string)
        self.assertEqual(value, volto_url)


class TestSubstitutionsFunctional(unittest.TestCase):
    """ Test case for substitutions"""

    layer = CLMS_ADDON_FUNCTIONAL_TESTING

    def setUp(self):
        """ test setup """
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.portal.invokeFactory("Document", id="doc", title="My Document")
        self.document = self.portal.get("doc")

    def test_volto_absolute_url(self):
        """ test for volto_absolute_url"""

        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        portal_url = self.portal.absolute_url()
        context_url = self.document.absolute_url()
        substitution = VoltoURLSubstitution(self.document)()
        self.assertEqual(
            substitution, context_url.replace(portal_url, volto_url)
        )

    def test_string_interpolation_volto_absolute_url(self):
        """ test as string interpolator"""

        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        portal_url = self.portal.absolute_url()
        context_url = self.document.absolute_url()

        string = "${volto_absolute_url}"
        value = IStringInterpolator(self.document)(string)
        self.assertEqual(value, context_url.replace(portal_url, volto_url))
