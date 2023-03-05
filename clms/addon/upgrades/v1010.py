""" upgrade step implementation """
# -*- coding: utf-8 -*-
from logging import getLogger
from uuid import uuid4

from collective.relationhelpers import api as relapi
from plone import api
from plone.app.upgrade.utils import alias_module
from zope.lifecycleevent import modified

logger = getLogger(__name__)


class BBB:
    """BBB object"""


try:
    from Products.contentmigration.basemigrator.migrator import CMFItemMigrator

    # pylint: disable=pointless-statement
    CMFItemMigrator
except ImportError:
    alias_module(
        "Products.contentmigration.basemigrator.migrator.CMFItemMigrator", BBB
    )

try:
    from Products.contentmigration.basemigrator.walker import CatalogWalker

    # pylint: disable=pointless-statement
    CatalogWalker
except ImportError:
    alias_module(
        "Products.contentmigration.basemigrator.walker.CatalogWalker", BBB
    )

# pylint: disable=wrong-import-position
# pylint: disable=ungrouped-imports
try:
    from plone.app.contenttypes.migration.dxmigration import (  # noqa
        migrate_base_class_to_new_class,  # noqa
    )  # noqa
except ImportError:

    def migrate_base_class_to_new_class(*args, **kwargs):
        print("Dummy function")


def upgrade(setup_tool=None):
    """upgrade function"""
    logger.info("Running upgrade (Python): v1010")
    # upgrade_folders_to_pages()
    logger.info("done")


def upgrade_folders_to_pages():
    """convert all folders of the site to be pages"""
    brains = api.content.find(portal_type="Folder", sort_on="path", path="/")
    for brain in brains:
        obj = brain.getObject()
        obj = make_document(obj)


def make_document(obj):
    """Convert any item to a FolderishDocument.
    Taken from plone.volto.browser.migrate_to_volto"""
    blocks = {}
    blocks_layout = {"items": []}

    # set title
    obj.title = obj.title
    uuid = str(uuid4())
    blocks[uuid] = {"@type": "title"}
    blocks_layout["items"].insert(0, uuid)

    # set description
    if obj.description:
        uuid = str(uuid4())
        blocks[uuid] = {"@type": "description"}
        blocks_layout["items"].insert(1, uuid)

    relations = relapi.export_relations(obj)
    migrate_base_class_to_new_class(
        obj,
        new_class_name=(
            "collective.folderishtypes.dx.content.FolderishDocument"
        ),
    )
    # Drop any custom layout because Documents display blocks!
    if getattr(obj.aq_base, "layout", None) is not None:
        del obj.layout

    obj.portal_type = "Document"
    # Invalidate cache to find the behaviors
    del obj._v__providedBy__

    if not obj.blocks:
        obj.blocks = blocks
    else:
        obj.blocks.update(blocks)

    if not obj.blocks_layout["items"]:
        obj.blocks_layout = blocks_layout
    else:
        obj.blocks_layout["items"] += blocks_layout

    modified(obj)
    if relations:
        relapi.restore_relations(all_relations=relations)
    return obj
