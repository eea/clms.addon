"""
testing basics
"""

# -*- coding: utf-8 -*-
import clms.addon
import collective.MockMailHost
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    SITE_OWNER_NAME,
    SITE_OWNER_PASSWORD,
    TEST_USER_ID,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    applyProfile,
    login,
    quickInstallProduct,
    setRoles,
)
from plone.testing.zope import WSGI_SERVER_FIXTURE


class ClmsAddonLayer(PloneSandboxLayer):
    """base layer"""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """setup zope"""
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        # pylint: disable=import-outside-toplevel
        import plone.restapi
        import Products.CMFCore

        self.loadZCML(package=Products.CMFCore)
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=clms.addon)
        self.loadZCML(package=collective.MockMailHost)

    def setUpPloneSite(self, portal):
        """setup Plone site"""
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])
        applyProfile(portal, "clms.addon:default")
        quickInstallProduct(portal, "collective.MockMailHost")
        applyProfile(portal, "collective.MockMailHost:default")


CLMS_ADDON_FIXTURE = ClmsAddonLayer()


CLMS_ADDON_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CLMS_ADDON_FIXTURE,),
    name="ClmsAddonLayer:IntegrationTesting",
)


CLMS_ADDON_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CLMS_ADDON_FIXTURE,),
    name="ClmsAddonLayer:FunctionalTesting",
)


CLMS_ADDON_RESTAPI_TESTING = FunctionalTesting(
    bases=(CLMS_ADDON_FIXTURE, WSGI_SERVER_FIXTURE),
    name="ClmsAddonLayer:RestApiTesting",
)


CLMS_ADDON_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        CLMS_ADDON_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="ClmsAddonLayer:AcceptanceTesting",
)
