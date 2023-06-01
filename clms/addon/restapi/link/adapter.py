"""
Specific Adapter for ILink items to return also the remote URL
"""

from zope.interface import implementer
from zope.component import adapter
from zope.interface import Interface
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.app.contenttypes.interfaces import ILink
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from plone.restapi.interfaces import IJSONSummarySerializerMetadata


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadataForLink:
    """specific summary serializer to add extra metadata to the summary
    results
    """

    def default_metadata_fields(self):
        """return a set with the metadata fields to be returned"""
        return {"getRemoteUrl"}


# @implementer(ISerializeToJsonSummary)
# @adapter(ILink, Interface)
# class LinkJSONSummarySerializer(DefaultJSONSummarySerializer):
#     """ISerializeToJsonSummary adapter for the Plone Site root."""

#     def __call__(self):
#         import pdb

#         pdb.set_trace()
#         a = 1

#         summary = super().__call__()
#         summary["getRemoteUrl"] = self.context.getRemoteUrl()
#         return summary
