"""override DefaultJSONSummarySerializer"""

# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import (
    IFieldSerializer,
    IObjectPrimaryFieldTarget,
    ISerializeToJson,
    ISerializeToJsonSummary,
)
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeToJson
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.serializer.nextprev import NextPrevious
from plone.restapi.serializer.summary import DefaultJSONSummarySerializer
from plone.restapi.serializer.utils import get_portal_type_title
from plone.restapi.services.locking import lock_info
from plone.supermodel.utils import mergedTaggedValueDict
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component import adapter, getMultiAdapter, queryAdapter, queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import Interface, implementer
from zope.schema import getFields

from clms.addon.interfaces import IClmsAddonLayer
from clms.types.content.dataset_accordion import IDataSetAccordion

try:
    # plone.app.iterate is by intend not part of Products.CMFPlone
    # dependencies
    # so we can not rely on having it
    # pylint: disable=ungrouped-imports
    from plone.restapi.serializer.working_copy import WorkingCopyInfo
except ImportError:
    WorkingCopyInfo = None


@implementer(ISerializeToJson)
@adapter(IDataSetAccordion, Interface)
class DataSetAccordionToJsonSerializer(SerializeToJson):
    """custom serializer for DataSetAccordions
    not to render the parent information
    to avoid infinite recursion
    """

    def __call__(self, version=None, include_items=True):
        """serializer implementation
        basically is the same as in the base serializer
        but with the parent handling removed
        """

        version = "current" if version is None else version

        obj = self.getVersion(version)

        #
        # This is the part that we have changed
        #
        # parent = aq_parent(aq_inner(obj))
        # parent_summary = getMultiAdapter(
        #     (parent, self.request), ISerializeToJsonSummary
        # )()
        #
        parent_summary = {}

        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            "@id": obj.absolute_url(),
            "id": obj.id,
            "@type": obj.portal_type,
            "type_title": get_portal_type_title(obj.portal_type),
            "parent": parent_summary,
            "created": json_compatible(obj.created()),
            "modified": json_compatible(obj.modified()),
            "review_state": self._get_workflow_state(obj),
            "UID": obj.UID(),
            "version": version,
            "layout": self.context.getLayout(),
            "is_folderish": False,
        }

        # Insert next/prev information
        try:
            nextprevious = NextPrevious(obj)
            result.update(
                {
                    "previous_item": nextprevious.previous,
                    "next_item": nextprevious.next,
                }
            )
        except ValueError:
            # If we're serializing an old version that was renamed or moved,
            # then its id might not be found inside the current object's
            # container.
            result.update({"previous_item": {}, "next_item": {}})

        # Insert working copy information
        if WorkingCopyInfo is not None:
            baseline, working_copy = WorkingCopyInfo(
                self.context
            ).get_working_copy_info()
            result.update({"working_copy": working_copy,
                          "working_copy_of": baseline})

        # Insert locking information
        result.update({"lock": lock_info(obj)})

        # Insert expandable elements
        result.update(expandable_elements(self.context, self.request))

        # Insert field values
        for schema in iterSchemata(self.context):
            read_permissions = mergedTaggedValueDict(
                schema, READ_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():
                if not self.check_permission(read_permissions.get(name), obj):
                    continue

                # serialize the field
                serializer = queryMultiAdapter(
                    (field, obj, self.request), IFieldSerializer
                )
                value = serializer()
                result[json_compatible(name)] = value

        target_url = getMultiAdapter(
            (self.context, self.request), IObjectPrimaryFieldTarget
        )()
        if target_url:
            result["targetUrl"] = target_url

        result["allow_discussion"] = getMultiAdapter(
            (self.context, self.request), name="conversation_view"
        ).enabled()

        return result


def get_blocks_value(brain):
    """transfrom the block value calling the relevant transformers"""
    obj = brain.getObject()
    serializer = getMultiAdapter((obj, getRequest()), ISerializeToJson)
    serialized = serializer(include_items=False)
    return serialized.get("blocks", {})


@implementer(ISerializeToJsonSummary)
@adapter(Interface, IClmsAddonLayer)
class CLMSDefaultJSONSummarySerializer(DefaultJSONSummarySerializer):
    """Change the default JSONSummarySerializer
    to properly handle the `blocks` field, calling to the
    relevant transformers
    """

    def __call__(self):
        """call the serializer"""
        adapted = queryAdapter(self.context, IContentListingObject)
        if adapted is None:
            obj = self.context
        else:
            obj = adapted

        summary = {}
        for field in self.metadata_fields():
            if field.startswith("_") or field in self.blocklisted_attributes:
                continue
            accessor = self.field_accessors.get(field, field)
            if field == "type_title":
                value = get_portal_type_title(self.context.portal_type)
            elif field == "blocks":
                # Here we want that the blocks attribute is transformed
                # correctly calling its relevant transformers
                value = get_blocks_value(obj)
            else:
                value = getattr(obj, accessor, None)
            try:
                if callable(value):
                    value = value()
            except WorkflowException:
                summary[field] = None
                continue
            summary[field] = json_compatible(value)
        return summary
