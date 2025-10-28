"""Minimal fallback implementation mimicking :mod:`requests`.

This is not a full HTTP client – it only exists so unit tests can run in
restricted environments without the real dependency installed. Real usage
should install the ``requests`` package.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict
from urllib.parse import unquote as _unquote

import sys


class RequestException(Exception):
    """Base exception matching :class:`requests.RequestException`."""


@dataclass
class Response:
    status_code: int = 200
    headers: Dict[str, str] | None = None
    content: bytes = b""
    url: str = ""
    history: list | None = None

    @property
    def is_redirect(self) -> bool:
        return self.status_code in {301, 302, 303, 307, 308}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RequestException(f"HTTP error {self.status_code}")

    def json(self):
        return json.loads(self.content.decode("utf-8"))


class Session:
    def __init__(self) -> None:
        self.headers: Dict[str, str] = {}

    def get(self, *_, **__) -> Response:  # pragma: no cover - runtime only
        raise RequestException("requests library not available")

    def mount(self, *_, **__):  # pragma: no cover - runtime only
        return None


class HTTPAdapter:  # pragma: no cover - simple placeholder
    def __init__(self, *_, **__):
        pass


class utils:  # pragma: no cover - mimic requests.utils
    unquote = staticmethod(_unquote)


def get(*_, **__):  # pragma: no cover - runtime only
    raise RequestException("requests library not available")


sys.modules.setdefault("requests", sys.modules[__name__])
