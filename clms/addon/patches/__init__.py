""" patches """
# -*- coding: utf-8 -*-

from logging import getLogger
import clms.addon.patches.meeting
import clms.addon.patches.restapi

log = getLogger(__name__)

# Stupid logging to avoid pyflakes errors
log.info(clms.addon.patches.meeting)
log.info(clms.addon.patches.restapi)
