""" Override Plone's default resolve_uid_and_caption filter
    not to interfere with our later filter that adds /@@download/file
    URL to File and TechnicalLibrary items in edition mode
"""
# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone import api
from plone.outputfilters.filters.resolveuid_and_caption import \
    ResolveUIDAndCaptionFilter as Base
from plone.outputfilters.filters.resolveuid_and_caption import resolveuid_re
from six.moves.urllib.parse import urljoin, urlsplit, urlunsplit


class ResolveUIDAndCaptionFilter(Base):
    def _render_resolveuid(self, href):
        url_parts = urlsplit(href)
        scheme = url_parts[0]
        path_parts = urlunsplit(["", ""] + list(url_parts[2:]))
        obj, subpath, appendix = self.resolve_link(path_parts)
        if obj is not None:
            href = obj.absolute_url()
            if subpath:
                href += "/" + subpath
            href += appendix
        # pylint: disable=line-too-long
        elif (resolveuid_re.match(href) is None and not scheme and not href.startswith("/")):  # noqa
            # absolutize relative URIs; this text isn't necessarily
            # being rendered in the context where it was stored
            relative_root = self.context
            if not getattr(self.context, "isPrincipiaFolderish", False):
                relative_root = aq_parent(self.context)
            actual_url = relative_root.absolute_url()
            href = urljoin(actual_url + "/", subpath) + appendix

            # This is the actual override. The method creates an absolute URL
            # of the link, but we want this to be a relative URL, this way the
            # editor gets a relative URL and the Volto editor handles it as an
            # internal link
            portal_url = api.portal.get().absolute_url()
            href = href.replace(portal_url, "")

        return href
