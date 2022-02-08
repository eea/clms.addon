"""
testing basics
"""
# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    quickInstallProduct
)
from plone.testing import z2

import clms.addon
import collective.MockMailHost


class ClmsAddonLayer(PloneSandboxLayer):
    """ base layer"""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """ setup zope """
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        # pylint: disable=import-outside-toplevel
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=clms.addon)
        self.loadZCML(package=collective.MockMailHost)

    def setUpPloneSite(self, portal):
        """ setup Plone site"""
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
    bases=(CLMS_ADDON_FIXTURE, z2.ZSERVER_FIXTURE),
    name="ClmsAddonLayer:RestApiTesting",
)


CLMS_ADDON_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        CLMS_ADDON_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ClmsAddonLayer:AcceptanceTesting",
)
