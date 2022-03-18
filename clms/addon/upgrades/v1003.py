""" upgrade step implementation """
# -*- coding: utf-8 -*-

from logging import getLogger
from plone import api

logger = getLogger(__name__)

PROFILE_ID = "clms.addon:default"


def upgrade(setup_tool=None):
    """upgrade function"""
    logger.info("Running upgrade (Python): Add user profile configuration")
    setup = api.portal.get_tool("portal_setup")
    setup.runImportStepFromProfile(PROFILE_ID, "collective.taxonomy")
    setup.runImportStepFromProfile(PROFILE_ID, "usersschema")
    setup.runImportStepFromProfile(PROFILE_ID, "memberdata-properties")
