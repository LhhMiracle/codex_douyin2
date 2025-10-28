"""Client for fetching product information from Douyin endpoints."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

try:  # pragma: no cover - fallback when requests is unavailable
    import requests
except ImportError:  # pragma: no cover
    from . import _requests_compat as requests

LOGGER = logging.getLogger(__name__)

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://haohuo.jinritemai.com/",
}


def _ensure_ratio_parameter(url: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if query.get("ratio") == "1":
        return url
    query.setdefault("ratio", "1")
    new_query = urlencode(query)
    return urlunparse(parsed._replace(query=new_query))


@dataclass
class DouyinClient:
    """Simple wrapper around the Douyin product detail endpoint."""

    session: requests.Session = field(default_factory=requests.Session)

    def __post_init__(self) -> None:
        self.session.headers.setdefault("Cookie", "")
        self.session.headers.update(_DEFAULT_HEADERS)

    def fetch_product_detail(self, product_id: str) -> Dict:
        """Fetch product detail structure.

        The implementation targets the public H5 endpoint used inside the Douyin
        storefront. The returned data structure is normalised to expose the
        product name and a list of high-resolution image URLs.
        """

        url = "https://ec.snssdk.com/product/info/v2/"
        params = {
            "product_id": product_id,
            "app_id": "1128",
            "item_source": "0",
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            LOGGER.error("Failed to fetch product %s: %s", product_id, exc)
            raise

        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        if not data:
            raise ValueError(f"No product data found for {product_id}")

        detail = data.get("product_info") or data
        title = detail.get("title") or detail.get("name") or ""

        image_candidates: List[str] = []
        for key in ("detail_image", "detail_images", "images", "image"):
            value = detail.get(key)
            if isinstance(value, list):
                image_candidates.extend(str(item.get("url", item)) for item in value)
            elif isinstance(value, dict):
                image_candidates.extend(str(v) for v in value.values())
            elif isinstance(value, str):
                image_candidates.append(value)

        if not image_candidates:
            gallery = detail.get("product_images") or data.get("product_images")
            if isinstance(gallery, list):
                for item in gallery:
                    if isinstance(item, dict):
                        image_candidates.append(
                            str(item.get("url") or item.get("uri") or "")
                        )

        images = []
        for img in image_candidates:
            if not img:
                continue
            img = img.strip()
            if img.startswith("//"):
                img = f"https:{img}"
            images.append(_ensure_ratio_parameter(img))

        images = [url for url in images if url]
        if not images:
            raise ValueError(f"Product {product_id} does not have image data")

        return {
            "product_id": product_id,
            "title": title,
            "images": images,
        }
