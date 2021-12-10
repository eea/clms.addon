""" upgrade step implementation """
# -*- coding: utf-8 -*-

from logging import getLogger
from plone import api

logger = getLogger(__name__)


def upgrade(setup_tool=None):
    """upgrade function"""
    logger.info("Running upgrade (Python): Add user profile configuration")
    setup = api.portal.get_tool("portal_setup")
    setup.runImportStepFromProfile("clms.addon:default", "collective.taxonomy")
    setup.runImportStepFromProfile("clms.addon:default", "usersschema")
    setup.runImportStepFromProfile(
        "clms.addon:default", "memberdata-properties"
    )
