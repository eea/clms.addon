""" utils for clms.addon """
# -*- coding: utf-8 -*-

from json import dumps

try:
    from urllib import unquote, urlencode

    from urlparse import ParseResult, parse_qsl, urlparse
except ImportError:
    # Python 3 fallback
    from urllib.parse import (
        ParseResult,
        parse_qsl,
        unquote,
        urlencode,
        urlparse,
    )


DIRECT_LINK_PORTAL_TYPES = ["File", "TechnicalLibrary"]


CLMS_DOMAINS = [
    "localhost",
    "backend",
    "clmsdemo.devel6cph.eea.europa.eu",
    "clms-staging.eea.europa.eu",
    "clms-prod.eea.europa.eu",
    "land.copernicus.eu"
]


def add_url_params(url, params):
    """Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'https://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'https://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't lose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {
            k: dumps(v)
            for k, v in parsed_get_args.items()
            if isinstance(v, (bool, dict))
        }
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside urlparse.
    new_url = ParseResult(
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        encoded_get_args,
        parsed_url.fragment,
    ).geturl()

    return new_url
