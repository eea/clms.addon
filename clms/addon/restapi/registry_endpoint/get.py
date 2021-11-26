""" Plone registry endpoint override to allow anonymous users
request keys under clms.*
"""
# -*- coding: utf-8 -*-
from plone import api
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.registry.get import RegistryGet as Base
from zope.component import getMultiAdapter, getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class RegistryGet(Base):
    """ base class """

    def reply(self):
        """ return the real response """
        registry = getUtility(IRegistry)
        if self.params:
            if self._get_record_name.startswith("clms."):  # noqa
                value = registry[self._get_record_name]
                return value
            if api.user.has_permission(
                user=api.user.get_current(), permission="cmf.ManagePortal"
            ):
                value = registry[self._get_record_name]
                return value

            self.request.response.setStatus(401)
            return None

        # batched listing
        if api.user.has_permission(
            user=api.user.get_current(), permission="cmf.ManagePortal"
        ):
            serializer = getMultiAdapter(
                (registry, self.request), ISerializeToJson
            )
            return serializer()

        self.request.response.setStatus(401)
        return None
