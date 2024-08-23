"""userschema endpoint"""

# -*- coding: utf-8 -*-
from logging import getLogger

from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

log = getLogger(__name__)


class DataSetSearch(Service):
    """Service definition"""

    def reply(self):
        """handle special queries with list items in query"""
        catalog = getToolByName(self.context, "portal_catalog")
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)

        new_query = {}
        for k, v in query.items():
            if isinstance(v, list):
                new_query[k] = []
                for item in v:
                    if "," in item:
                        new_query[k].extend(item.split(","))
                    else:
                        new_query[k].append(item)
            else:
                if "," in v:
                    new_query[k] = v.split(",")
                else:
                    new_query[k] = v

        lazy_resultset = catalog.searchResults(**new_query)

        batch = HypermediaBatch(self.request, lazy_resultset)

        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        links = batch.links
        if links:
            results["batching"] = links

        results["items"] = []
        for brain in batch:
            try:
                obj = brain.getObject()
            except KeyError:
                # Guard in case the brain returned refers to an object that
                # doesn't
                # exists because it failed to uncatalog itself or the catalog
                # has
                # stale cataloged objects for some reason
                log.warning(
                    "Brain getObject error: %s doesn't exist anymore",
                    brain.getPath(),
                )
                continue

            result = getMultiAdapter((obj, self.request), ISerializeToJson)(
                include_items=False
            )

            results["items"].append(get_needed_values(result))

        return results


def get_needed_values(res):
    """return only the attribute and properties that are needed to identify
    the dataset"""
    return dict(
        title=res.get("title", ""),
        UID=res.get("UID", ""),
        dataset_download_information=res.get("dataset_download_information", {}),
        downloadable_files=res.get("downloadable_files", {}),
        original_projection=res.get("characteristics_projection", ""),
        download_show_auxiliary_calendar=res.get(
            "download_show_auxiliary_calendar", False
        ),
    )
