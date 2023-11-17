""" Main product initializer
"""
from logging import getLogger

import clms.addon.patches as a
from plone.app.upgrade.utils import alias_module
from zope.i18nmessageid.message import MessageFactory
from zope.interface import Interface

_ = MessageFactory("clms.addon")


log = getLogger(__name__)
# Stupid logging to avoid linter errors
log.info(a)


class IDummy(Interface):
    """Dummy interface to alias eea.api.taxonomy.interfaces.IEeaApiTaxonomyLayer"""


try:
    from eea.api.taxonomy.interfaces import IEeaApiTaxonomyLayer  # noqa
except ImportError:
    alias_module("eea.api.taxonomy.interfaces.IEeaApiTaxonomyLayer", IDummy)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
