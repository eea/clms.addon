""" patch catalog to handle parenthesis inside quotes
    see https://github.com/plone/Products.CMFPlone/issues/3879
    for further reference
"""
# -*- coding: utf-8 -*-

from logging import getLogger


from Products.CMFPlone.browser import search
from Products.CMFPlone.browser.search import BAD_CHARS, quote_chars
from plone.app.querystring import querybuilder
import re


def my_quote(term):
    """ quote """
    # The terms and, or and not must be wrapped in quotes to avoid
    # being parsed as logical query atoms.
    if term.lower() in ("and", "or", "not"):
        term = '"%s"' % term
    return quote_chars(term)


def my_munge_search_term(query):
    """ munge_search term"""
    original_query = query

    for char in BAD_CHARS:
        query = query.replace(char, " ")

    # extract quoted phrases first
    quoted_phrases = re.findall(r'"([^"]*)"', query)
    r = []
    for qp in quoted_phrases:
        # remove from original query
        query = query.replace(f'"{qp}"', "")
        # replace with cleaned leading/trailing whitespaces
        # and skip empty phrases
        clean_qp = qp.strip()
        if not clean_qp:
            continue
        r.append(f'"{clean_qp}"')

    r += map(my_quote, query.strip().split())
    r = " AND ".join(r)
    r = r + ("*" if r and not original_query.endswith('"') else "")
    return r


search.quote = my_quote
search.munge_search_term = my_munge_search_term

querybuilder._quote = my_quote
querybuilder.munge_search_term = my_munge_search_term

log = getLogger(__name__)
log.info('Patched Products.CMFPlone.browser.search')
