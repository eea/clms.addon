"""
Custom IPurgePathRewriter adapter
"""

from urllib.parse import urlparse

from clms.addon.interfaces import IClmsAddonLayer
from plone.cachepurging.interfaces import (ICachePurgingSettings,
                                           IPurgePathRewriter)
from plone.cachepurging.rewrite import DefaultRewriter as Base
from plone.registry.interfaces import IRegistry
from zope.component import adapter, queryUtility
from zope.interface import implementer


@implementer(IPurgePathRewriter)
@adapter(IClmsAddonLayer)
class CLMSRewriter(Base):
    """
    Rewriter implementation
    """
    def __call__(self, path):
        """
            return the rewriten urls to be purged
        """
        request = self.request

        # No rewriting necessary
        virtualURL = request.get("VIRTUAL_URL", None)
        if virtualURL is None:
            return [path]

        registry = queryUtility(IRegistry)
        if registry is None:
            return [path]

        settings = registry.forInterface(ICachePurgingSettings, check=False)

        #
        # this is the default behavior, so we ignore it
        # we want to produce both VirtualHosted and un-VirtualHosted URLs
        #
        # virtualHosting = settings.virtualHosting

        # # We don't want to rewrite
        # if not virtualHosting:
        #     return [path]

        # We need to reconstruct VHM URLs for each of the domains
        virtualUrlParts = request.get("VIRTUAL_URL_PARTS")
        virtualRootPhysicalPath = request.get("VirtualRootPhysicalPath")

        # Make sure request is compliant
        # pylint: disable=line-too-long
        if (not virtualUrlParts or not virtualRootPhysicalPath or not isinstance(virtualUrlParts, (list, tuple)) or not isinstance(virtualRootPhysicalPath, (list, tuple)) or len(virtualUrlParts) < 2 or len(virtualUrlParts) > 3):  # noqa
            return [path]

        domains = settings.domains
        if not domains:
            domains = [virtualUrlParts[0]]

        # Virtual root, e.g. /Plone. Clear if we don't have any virtual root
        virtualRoot = "/".join(virtualRootPhysicalPath)
        if virtualRoot == "/":
            virtualRoot = ""

        # Prefix, e.g. /_vh_foo/_vh_bar. Clear if we don't have any.
        pathPrefix = len(virtualUrlParts) == 3 and virtualUrlParts[1] or ""
        if pathPrefix:
            pathPrefix = "/" + "/".join(
                ["_vh_%s" % p for p in pathPrefix.split("/")]
            )

        paths = []
        paths.append(path)

        # Path, e.g. /front-page
        if len(path) > 0 and not path.startswith("/"):
            path = "/" + path

        for domain in domains:
            scheme, host = urlparse(domain)[:2]
            paths.append(
                "/VirtualHostBase/%(scheme)s/%(host)s%(root)s/"
                "VirtualHostRoot%(prefix)s%(path)s"
                % {
                    "scheme": scheme,
                    "host": host,
                    "root": virtualRoot,
                    "prefix": pathPrefix,
                    "path": path,
                }
            )
        return paths
