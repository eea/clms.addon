""" patches """
# -*- coding: utf-8 -*-

from logging import getLogger
import clms.addon.patches.meeting as a
import clms.addon.patches.restapi as b
import clms.addon.patches.blocks as c

log = getLogger(__name__)

# Stupid logging to avoid pyflakes errors
log.info(a)
log.info(b)
log.info(c)
