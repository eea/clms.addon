"""patches"""
# -*- coding: utf-8 -*-

from logging import getLogger

import clms.addon.patches.behavior as e
import clms.addon.patches.contextnavigation as g
import clms.addon.patches.meeting as a
import clms.addon.patches.scale as f
import clms.addon.patches.sortable_title as d
import clms.addon.patches.catalog as h
import clms.addon.patches.validate_form_file as i
import clms.addon.patches.jwkest_accept_secp256k1 as j
import clms.addon.patches.volto_indexers as k

log = getLogger(__name__)

# Stupid logging to avoid pyflakes errors
log.info(a)
log.info(d)
log.info(e)
log.info(f)
log.info(g)
log.info(h)
log.info(i)
log.info(j)
log.info(k)
