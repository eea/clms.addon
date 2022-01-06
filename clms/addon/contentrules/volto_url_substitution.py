"""
Content rule string interpolator to return volto url of a given content item
"""

from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapter

from clms.addon import _
from Products.CMFCore.interfaces import IContentish
from plone import api


@adapter(IContentish)
class VoltoURLSubstitution(BaseSubstitution):

    category = _(u"All Content")
    description = _(u"Volto URL")

    def safe_call(self):
        context_url = self.context.absolute_url()
        plone_domain = api.portal.get().absolute_url()
        frontend_domain = api.portal.get_registry_record(
            "volto.frontend_domain"
        )
        if frontend_domain.endswith("/"):
            frontend_domain = frontend_domain[:-1]

        return context_url.replace(plone_domain, frontend_domain)
