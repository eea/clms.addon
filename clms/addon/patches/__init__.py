""" patches """
# -*- coding: utf-8 -*-

from logging import getLogger
import clms.addon.patches.meeting as a
# import clms.addon.patches.restapi as b
# import clms.addon.patches.blocks as c
import clms.addon.patches.sortable_title as d
import clms.addon.patches.behavior as e
import clms.addon.patches.scale as f

log = getLogger(__name__)

# Stupid logging to avoid pyflakes errors
log.info(a)
# log.info(b)
# log.info(c)
log.info(d)
log.info(e)
log.info(f)
