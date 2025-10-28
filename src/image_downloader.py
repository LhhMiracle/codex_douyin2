"""Helpers to download product images with retry and quality validation."""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import List, Sequence

try:  # pragma: no cover - fallback when requests is unavailable
    import requests
    from requests import Response
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:  # pragma: no cover
    from . import _requests_compat as requests

    Response = requests.Response  # type: ignore

    class HTTPAdapter:  # type: ignore
        def __init__(self, *_, **__):
            pass

    class Retry:  # type: ignore
        def __init__(self, *_, **__):
            pass


DEFAULT_TIMEOUT = 10
MIN_RESOLUTION = (1080, 1080)


def _filename_from_url(url: str, index: int) -> str:
    ext = os.path.splitext(url.split("?")[0])[1]
    if ext.lower() not in {".jpg", ".jpeg", ".png"}:
        guessed = mimetypes.guess_extension(
            mimetypes.guess_type(url)[0] or "image/jpeg"
        )
        ext = guessed or ".jpg"
    return f"image_{index:02d}{ext}"


def _create_session(retries: int) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _validate_resolution(path: Path) -> bool:
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:  # pragma: no cover - requires pillow at runtime
        raise RuntimeError("Pillow is required for resolution validation") from exc

    with Image.open(path) as image:
        width, height = image.size
    return width >= MIN_RESOLUTION[0] and height >= MIN_RESOLUTION[1]


def _upgrade_url(url: str) -> str:
    if "ratio=" in url:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}ratio=1"


def _download_single(
    session: requests.Session, url: str, dest: Path, timeout: int
) -> Response:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    dest.write_bytes(response.content)
    return response


def download_images(
    image_urls: Sequence[str],
    dest_dir: Path,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = 3,
) -> List[Path]:
    """Download a sequence of image URLs into ``dest_dir``.

    The function enforces a minimum resolution defined by ``MIN_RESOLUTION``. If
    the downloaded file does not meet the requirement it retries with a "ratio"
    query parameter typically used by Douyin to request original quality.
    """

    dest_dir.mkdir(parents=True, exist_ok=True)
    session = _create_session(retries)
    stored_paths: List[Path] = []

    for index, url in enumerate(image_urls, start=1):
        filename = _filename_from_url(url, index)
        path = dest_dir / filename
        try:
            _download_single(session, url, path, timeout)
            if not _validate_resolution(path):
                upgraded = _upgrade_url(url)
                if upgraded != url:
                    _download_single(session, upgraded, path, timeout)
                if not _validate_resolution(path):
                    raise ValueError(f"Image from {url} below minimum resolution")
        except Exception:
            if path.exists():
                path.unlink()
            raise
        stored_paths.append(path)

    return stored_paths
