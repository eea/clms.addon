""" ZCatalogCompatibleQueryAdapter override to handle
multiple sort_on and sort_order values
"""
# -*- coding: utf-8 -*-
import logging

from plone.restapi.interfaces import (
    IIndexQueryParser,
    IZCatalogCompatibleQuery,
)
from plone.restapi.search.query import ZCatalogCompatibleQueryAdapter as Base
from zope.component import adapter, getMultiAdapter
from zope.interface import Interface, implementer

log = logging.getLogger(__name__)


@implementer(IZCatalogCompatibleQuery)
@adapter(Interface, Interface)
class ZCatalogCompatibleQueryAdapter(Base):
    """adapter class"""

    global_query_params = {
        "sort_limit": int,
        "b_start": int,
        "b_size": int,
    }

    multiple_types_global_query_params = {
        "sort_on": {list: list, tuple: list, str: str},
        "sort_order": {list: list, tuple: list, str: str},
    }

    def parse_multiple_types_param(self, idx_name, idx_query):
        """these indexes can contain single str values or a list of strings"""
        possible_values = self.multiple_types_global_query_params[idx_name]
        for current_value, future_value in possible_values.items():
            if isinstance(idx_query, current_value):
                return future_value(idx_query)

    def __call__(self, query):
        """call the adapter"""
        for idx_name, idx_query in query.items():
            if idx_name in self.global_query_params:
                # It's a query-wide parameter like 'sort_on'
                query[idx_name] = self.parse_query_param(idx_name, idx_query)
                continue

            if idx_name in self.multiple_types_global_query_params:
                query[idx_name] = self.parse_multiple_types_param(
                    idx_name, idx_query
                )

            # Then check for each index present in the query if there is an
            # IIndexQueryParser that knows how to deserialize any values
            # that could not be serialized in a query string or JSON
            index = self.get_index(idx_name)
            if index is None:
                if idx_name not in self.ignore_query_params:
                    log.warning("No such index: %r" % idx_name)
                continue

            query_opts_parser = getMultiAdapter(
                (index, self.context, self.request), IIndexQueryParser
            )

            if query_opts_parser is not None:
                idx_query = query_opts_parser.parse(idx_query)

            query[idx_name] = idx_query
        return query
