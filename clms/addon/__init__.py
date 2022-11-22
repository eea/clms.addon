""" Main product initializer
"""
from logging import getLogger

import clms.addon.patches as a
from zope.i18nmessageid.message import MessageFactory

_ = MessageFactory("clms.addon")


log = getLogger(__name__)
# Stupid logging to avoid linter errors
log.info(a)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
