"""Secure proxy for the synchronous CDSE Process API."""
# -*- coding: utf-8 -*-
import json
import logging
import threading
import time

import requests
from clms.downloadtool.api.services.cdse.cdse_integration import (
    get_token as get_cdse_token,
)
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service


LOG = logging.getLogger(__name__)

PROCESS_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
PROCESS_TIMEOUT = 120
TOKEN_CACHE_SECONDS = 240

REQUEST_HEADERS = ("Accept", "Accept-Crs", "Cache-Control")
RESPONSE_HEADERS = (
    "Cache-Control",
    "Content-Disposition",
    "Content-Type",
    "ETag",
    "Last-Modified",
    "Retry-After",
    "X-ProcessingUnits-Spent",
    "X-Request-Id",
)

_token_lock = threading.Lock()
_token_cache = {"access_token": None, "expires_at": 0}


def clear_token_cache():
    """Clear the process-local OAuth token cache."""
    with _token_lock:
        _token_cache["access_token"] = None
        _token_cache["expires_at"] = 0


def get_cdse_access_token(force_refresh=False):
    """Return a cached CDSE client-credentials token."""
    now = time.monotonic()
    if (
        not force_refresh
        and _token_cache["access_token"]
        and now < _token_cache["expires_at"]
    ):
        return _token_cache["access_token"]

    with _token_lock:
        now = time.monotonic()
        if (
            not force_refresh
            and _token_cache["access_token"]
            and now < _token_cache["expires_at"]
        ):
            return _token_cache["access_token"]

        access_token = get_cdse_token()
        if not access_token:
            raise RuntimeError("CDSE token helper returned no access token")

        _token_cache["access_token"] = access_token
        _token_cache["expires_at"] = (
            time.monotonic() + TOKEN_CACHE_SECONDS
        )
        return access_token


class CDSEProcessProxy(Service):
    """Forward a Process API payload using server-side credentials."""

    def render(self):
        """Return upstream bytes without plone.restapi JSON serialization."""
        return self.reply()

    def _error(self, status, message):
        response = self.request.response
        response.setStatus(status)
        response.setHeader("Content-Type", "application/json")
        return json.dumps({"error": message}).encode("utf-8")

    def _request_headers(self, access_token):
        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        }
        for name in REQUEST_HEADERS:
            value = self.request.getHeader(name)
            if value:
                headers[name] = value
        headers.setdefault("Accept", "image/png")
        return headers

    def _forward(self, payload, force_refresh=False):
        access_token = get_cdse_access_token(force_refresh=force_refresh)
        return requests.post(
            PROCESS_API_URL,
            json=payload,
            headers=self._request_headers(access_token),
            timeout=PROCESS_TIMEOUT,
        )

    def _relay(self, upstream):
        response = self.request.response
        response.setStatus(upstream.status_code)
        for name in RESPONSE_HEADERS:
            value = upstream.headers.get(name)
            if value is not None:
                response.setHeader(name, value)
        if not upstream.headers.get("Content-Type"):
            response.setHeader("Content-Type", "application/octet-stream")
        return upstream.content

    def reply(self):
        """Validate, authenticate, forward, and relay a PROCESS request."""
        content_type = self.request.getHeader("Content-Type", "")
        if "application/json" not in content_type.lower():
            return self._error(415, "Content-Type must be application/json")

        try:
            payload = json_body(self.request)
        except (TypeError, ValueError):
            return self._error(400, "Request body must contain valid JSON")

        if not isinstance(payload, dict):
            return self._error(400, "Request body must be a JSON object")

        try:
            upstream = self._forward(payload)
            if upstream.status_code == 401:
                clear_token_cache()
                upstream = self._forward(payload, force_refresh=True)
        except (requests.RequestException, RuntimeError, ValueError):
            LOG.exception("CDSE Process API proxy request failed")
            return self._error(502, "CDSE Process API is unavailable")

        return self._relay(upstream)
