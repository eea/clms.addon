# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import clms.addon


class ClmsAddonLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=clms.addon)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "clms.addon:default")


CLMS_ADDON_FIXTURE = ClmsAddonLayer()


CLMS_ADDON_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CLMS_ADDON_FIXTURE,),
    name="ClmsAddonLayer:IntegrationTesting",
)


CLMS_ADDON_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CLMS_ADDON_FIXTURE,),
    name="ClmsAddonLayer:FunctionalTesting",
)


CLMS_ADDON_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        CLMS_ADDON_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ClmsAddonLayer:AcceptanceTesting",
)
