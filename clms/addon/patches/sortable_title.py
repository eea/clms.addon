""" patch the sortable_title max length in Products.CMFPlone"""

from Products.CMFPlone import CatalogTool

CatalogTool.MAX_SORTABLE_TITLE = 99999

from logging import getLogger
log = getLogger(__name__)
log.info('Patched MAX_SORTABLE_TITLE to allow longer sortable_titles')
