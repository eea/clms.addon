"""upgrade step implementation"""

# -*- coding: utf-8 -*-
from logging import getLogger

from plone import api
from zope.component import queryMultiAdapter


logger = getLogger(__name__)


def upgrade(setup_tool=None):
    """Migrate teaserGrid to gridBlock."""
    logger.info("Running upgrade (Python): v1015")
    portal = api.portal.get()
    request = getattr(
        setup_tool, "REQUEST", None) or getattr(portal, "REQUEST", None)
    view = queryMultiAdapter((portal, request), name="teaser-migrate")

    if view is None:
        logger.warning("Migration view 'teaser-migrate' not found")
        return

    count = view.migrate()
    logger.info(
        "Migrated %s content objects from teaserGrid to gridBlock",
        count,
    )
    logger.info("done")
