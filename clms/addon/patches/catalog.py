""" patch catalog to handle parenthesis inside quotes
    see https://github.com/plone/Products.CMFPlone/issues/3879
    for further reference
"""
# -*- coding: utf-8 -*-

from Products.CMFPlone.browser.search import BAD_CHARS, quote_chars
import re


def quote(term):
    # The terms and, or and not must be wrapped in quotes to avoid
    # being parsed as logical query atoms.
    if term.lower() in ("and", "or", "not"):
        term = '"%s"' % term
    return term


def munge_search_term(query):
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

    r += map(quote, query.strip().split())
    r = " AND ".join(r)
    r = quote_chars(r) + ("*" if r and not r.endswith('"') else "")
    return r
