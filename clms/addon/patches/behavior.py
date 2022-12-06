"""
Patch plone.behavior.registration to add an attribute that collective.taxonomy
behaviors lack

"""
# -*- coding: utf-8 -*-
from logging import getLogger

from plone.behavior import logger, registration
from plone.behavior.interfaces import IBehavior
from zope.component import ComponentLookupError, getUtilitiesFor, getUtility


def my_lookup_behavior_registration(
    name=None, identifier=None, warn_about_fallback=True
):
    """Look up behavior registration either by name or interface identifier.
       Fall back to checking the former_dotted_names if the lookup is not
       successful.

    ``ValueError`` is thrown if function call is incomplete.
    ``BehaviorRegistrationNotFound`` is thrown if lookup fails.
    """
    try:
        assert name or identifier
    except AssertionError:
        # pylint: disable=raise-missing-from
        raise ValueError("Either ``name`` or ``identifier`` must be given")
    # identifier rules if given
    if identifier:
        name = identifier
    try:
        return getUtility(IBehavior, name=name)
    except ComponentLookupError:
        # pylint: disable=unused-variable
        for id_, behavior in getUtilitiesFor(IBehavior):
            # Before we raise an error, iterate over all behaviors and check
            # if the requested name is registered as a former dotted name.
            if (
                # pylint: disable=line-too-long
                hasattr(behavior, "former_dotted_names") and name in behavior.former_dotted_names  # noqa
            ):
                if warn_about_fallback:
                    logger.warn(
                        'The dotted name "{0}" is deprecated. It has been '
                        'changed to "{1}"'.format(
                            name,
                            behavior.interface.__identifier__,
                        )
                    )
                return behavior

        # pylint: disable=raise-missing-from
        raise registration.BehaviorRegistrationNotFound(name)


registration.lookup_behavior_registration = my_lookup_behavior_registration

log = getLogger(__name__)
log.info("Patched plone.behavior.registration.lookup_behavior_registration")
