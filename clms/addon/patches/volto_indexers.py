"""Patch eea.volto.policy indexers to support older plone.volto import path."""

from zope.interface import Interface


def _apply_patch():
    try:
        from eea.volto.policy import indexers as policy_indexers
    except ImportError:
        return

    if (policy_indexers.plone_image_field_indexer
            and policy_indexers.ploneHasPreviewImage):
        return

    try:
        from plone.volto.indexers import (
            image_field_indexer as plone_image_field_indexer,
            hasPreviewImage as ploneHasPreviewImage,
        )
        from plone.volto.behaviors.preview import IPreview
    except ImportError:
        return

    policy_indexers.plone_image_field_indexer = plone_image_field_indexer
    policy_indexers.ploneHasPreviewImage = ploneHasPreviewImage
    policy_indexers.IPreview = IPreview or Interface


_apply_patch()
