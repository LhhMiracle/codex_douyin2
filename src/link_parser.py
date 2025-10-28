"""Utilities to extract product identifiers from various Douyin share texts."""

from __future__ import annotations

import json
import logging
import re
from typing import Iterable, Optional
from urllib.parse import parse_qs, urlparse

try:  # pragma: no cover - fallback for test environment
    import requests
except ImportError:  # pragma: no cover
    from . import _requests_compat as requests

LOGGER = logging.getLogger(__name__)

_URL_PATTERN = re.compile(r"https?://[^\s<>'\"]+")
_JSON_PATTERN = re.compile(r"\{.*?\}")
_PRODUCT_ID_KEYS = ("product_id", "id")


class LinkParserError(RuntimeError):
    """Raised when a product id cannot be extracted."""


def _clean_text(raw_text: str) -> str:
    text = raw_text.replace("\n", " ")
    text = re.sub(r"[\u3000]", " ", text)
    return text


def _iter_candidate_urls(raw_text: str) -> Iterable[str]:
    cleaned = _clean_text(raw_text)
    for match in _URL_PATTERN.finditer(cleaned):
        yield match.group(0)


def _resolve_short_url(url: str) -> Optional[str]:
    try:
        response = requests.get(url, allow_redirects=False, timeout=5)
    except requests.RequestException as exc:
        LOGGER.debug("Failed to resolve short url %s: %s", url, exc)
        return None
    if response.is_redirect or response.status_code in {301, 302, 303, 307, 308}:
        location = response.headers.get("Location")
        if location:
            LOGGER.debug("Resolved short url %s to %s", url, location)
            return location
    if response.history:
        final = response.url
        LOGGER.debug("Resolved via history %s -> %s", url, final)
        return final
    return None


def _extract_from_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key in _PRODUCT_ID_KEYS:
        if key in query and query[key]:
            return query[key][0]

    # inspect fragment as query style
    fragment_query = parse_qs(parsed.fragment)
    for key in _PRODUCT_ID_KEYS:
        if key in fragment_query and fragment_query[key]:
            return fragment_query[key][0]

    # sometimes product id is embedded in json string inside query
    for value_list in query.values():
        for value in value_list:
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                continue
            if isinstance(decoded, dict):
                for key in _PRODUCT_ID_KEYS:
                    if key in decoded:
                        return str(decoded[key])

    # fallback: digits in path
    path_segments = [segment for segment in parsed.path.split("/") if segment]
    for segment in reversed(path_segments):
        if segment.isdigit():
            return segment

    return None


def _extract_from_json(raw_text: str) -> Optional[str]:
    for candidate in _JSON_PATTERN.findall(raw_text):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            for key in _PRODUCT_ID_KEYS:
                value = data.get(key)
                if value:
                    return str(value)
    return None


def extract_product_id(raw_text: str) -> str:
    """Extract product id from different Douyin share texts."""

    for url in _iter_candidate_urls(raw_text):
        parsed = urlparse(url)
        resolved_url = url
        if parsed.netloc.endswith("v.douyin.com"):
            resolved = _resolve_short_url(url)
            if resolved:
                resolved_url = resolved
        product_id = _extract_from_url(resolved_url)
        if product_id:
            return product_id

    # attempt to decode escaped urls
    for url in _iter_candidate_urls(requests.utils.unquote(raw_text)):
        product_id = _extract_from_url(url)
        if product_id:
            return product_id

    cleaned = _clean_text(raw_text)
    # look for explicit product id patterns
    simple_match = re.search(r"(?:product_id|id)[:=]\s*([0-9]+)", cleaned)
    if simple_match:
        return simple_match.group(1)

    product_id = _extract_from_json(cleaned)
    if product_id:
        return product_id

    raise LinkParserError("Unable to extract product id from provided text")
