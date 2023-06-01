"""
Specific Adapter for ILink items to return also the remote URL
"""

from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.interface import implementer


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadataForLink:
    """specific summary serializer to add extra metadata to the summary
    results
    """

    def default_metadata_fields(self):
        """return a set with the metadata fields to be returned"""
        return {"getRemoteUrl"}
