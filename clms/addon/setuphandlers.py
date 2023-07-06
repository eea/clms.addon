""" Custom setup
"""
from logging import getLogger
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone import api


@implementer(INonInstallable)
class HiddenProfiles:
    """Hidden profiles"""

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "clms.addon:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["clms.addon.upgrades"]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    portal = api.portal.get()
    setupTool = SetupMultilingualSite()
    output = setupTool.setupSite(portal)

    log = getLogger(__name__)
    log.info(output)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
