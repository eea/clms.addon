""" CMS export content utils"""
from urllib.parse import urlparse
from plone import api


def get_domain(url):
    """Extract domain"""
    if url and url.strip():
        data = urlparse(url)
        return data.hostname

    return ""


def get_datasets_obj():
    """Get datasets as objects"""
    catalog = api.portal.get_tool(name="portal_catalog")
    results = catalog.searchResults(
        portal_type="DataSet", sort_on="modified", sort_order="descending"
    )

    return [x.getObject() for x in results]
