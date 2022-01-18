"""
Content rule string interpolator to return volto url of a given content item
"""

from plone import api
from plone.stringinterp.adapters import BaseSubstitution
from Products.CMFCore.interfaces import IContentish
from zope.component import adapter

from clms.addon import _


@adapter(IContentish)
class VoltoPortalURLSubstitution(BaseSubstitution):
    """ URL Substitution adapter """

    category = _(u"All Content")
    description = _(u"Volto Portal URL")

    def safe_call(self):
        """ get the url """
        frontend_domain = api.portal.get_registry_record(
            "volto.frontend_domain"
        )
        return frontend_domain
