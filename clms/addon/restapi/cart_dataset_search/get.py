""" userschema endpoint """
# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


class DataSetSearch(Service):
    """ Service definition"""

    def reply(self):
        """ handle special queries with list items in query """
        self.catalog = getToolByName(self.context, "portal_catalog")
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        new_query = {}
        for k, v in query.items():
            if isinstance(v, list):
                new_query[k] = []
                for item in v:
                    if "," in v:
                        new_query[k].extend(item.split(","))
                    else:
                        new_query[k].append(v)
            else:
                if "," in v:
                    new_query[k] = v.split(',')
                else:
                    new_query[k] = v
        lazy_resultset = self.catalog.searchResults(**new_query)
        results = getMultiAdapter((lazy_resultset, self.request), ISerializeToJson)(
            fullobjects=True
        )

        return results
