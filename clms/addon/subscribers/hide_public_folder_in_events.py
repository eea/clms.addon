""" Subscriber to set expiration date of the 'public' folder
    that is automatically created in Meetings
"""
from logging import getLogger

from Acquisition import aq_parent
from DateTime import DateTime
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


def set_folder_expired(context, event):
    """subscriber implementation"""
    log = getLogger(__name__)
    parent = aq_parent(context)
    default_folder_blocks = {
        "90c2b0ff-483b-4253-8a40-4a9c56be4a9f": {
            "@type": "title"
        }
    }

    default_folder_blocks_layout = {
        "items": [
            "90c2b0ff-483b-4253-8a40-4a9c56be4a9f"
        ]
    }

    if context.Title() == "Public" and parent.portal_type == "eea.meeting":
        context.setEffectiveDate(DateTime("1990-01-01T09:00:00Z"))
        context.expires = DateTime("1990-01-01T10:00:00Z")
        context.setExpirationDate(DateTime("1990-01-01T10:00:00Z"))
        context.blocks = default_folder_blocks
        context.blocks_layout = default_folder_blocks_layout
        notify(ObjectModifiedEvent(context))
        log.info(
            "Expiration date set for public folder in event %s", parent.id
        )
