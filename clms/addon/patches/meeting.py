""" patch eea.meeting to move a field"""
# -*- coding: utf-8 -*-
from logging import getLogger
from eea.meeting.interfaces.meeting import IMeeting
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset


def move_field(
    schema, fieldname,
    to_fieldset_name,
    label=None,
    description=None,
    order=None
):
    """Moves a field named "fieldname" on a Zope "schema" to a new fieldset
        "to_field_name".

    - creates a new fieldset on demand (then label, description and order are
        passed to the new one).
    - if value of "to_fieldset_name" is "default", then the field sticks on the
        main form.
    """
    # find schema with field in inheritance tree
    schema_with_field = None
    for pschema in reversed(schema.__iro__):
        if pschema.direct(fieldname):
            schema_with_field = pschema
            break
    if schema_with_field is None:
        raise KeyError(f"field '{fieldname}' does not exist on {schema}.")

    # remove field from fieldset (if in any)
    fieldsets_direct = schema_with_field.queryDirectTaggedValue(FIELDSETS_KEY)
    if fieldsets_direct is not None:
        for fieldset in fieldsets_direct:
            if fieldname in fieldset.fields:
                fieldset.fields.remove(fieldname)
                break

    if to_fieldset_name == "default":
        # default means to fieldset, but on main form
        return

    if fieldsets_direct is None:
        # no tagged value set so far!
        fieldsets_direct = list()
        schema.setTaggedValue(FIELDSETS_KEY, fieldsets_direct)

    # try to find the fieldset, append and exit
    for fieldset in fieldsets_direct:
        if fieldset.__name__ == to_fieldset_name:
            fieldset.fields.append(fieldname)
            return

    # not found, need to create new fieldset
    new_fieldset = Fieldset(
        to_fieldset_name,
        fields=[fieldname],
    )
    if label is not None:
        new_fieldset.label = label
    if description is not None:
        new_fieldset.description = description
    if order is not None:
        new_fieldset.order = order
    fieldsets_direct.append(new_fieldset)
    # Done!


move_field(IMeeting, "meeting_level", "Event Level")

log = getLogger(__name__)
log.info("Patched eea.meeting interface to move field")
