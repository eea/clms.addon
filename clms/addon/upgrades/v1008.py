""" upgrade step implementation """
# -*- coding: utf-8 -*-

from logging import getLogger

from collective.taxonomy.interfaces import ITaxonomy
from zope.i18n.interfaces import ITranslationDomain
from zope.schema.interfaces import IVocabularyFactory
from zope.component.hooks import getSiteManager

logger = getLogger(__name__)

TAXONOMIES = [
    "collective.taxonomy.userprofileinstitutionaldomain",
    "collective.taxonomy.userprofileproductuseintention",
    "collective.taxonomy.userprofileprofessionalthematicdomain",
]


def delete_taxonomies(context=None):
    """unregister taxonomies and related items"""
    sm = getSiteManager()

    for item in TAXONOMIES:
        utility = sm.queryUtility(ITaxonomy, name=item)
        if utility is not None:
            utility.unregisterBehavior()

            sm.unregisterUtility(utility, ITaxonomy, name=item)
            sm.unregisterUtility(utility, IVocabularyFactory, name=item)
            sm.unregisterUtility(utility, ITranslationDomain, name=item)

            logger.info("Unregistered taxonomy: %s", item)


def upgrade(setup_tool=None):
    """upgrade function"""
    logger.info("Running upgrade (Python): v1008")

    delete_taxonomies(setup_tool)
