"""High level pipeline orchestrating product download and background removal."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from .background_removal import process_batch
from .douyin_client import DouyinClient
from .image_downloader import download_images
from .link_parser import extract_product_id

LOGGER = logging.getLogger(__name__)
_LOG_PATH = Path("logs/pipeline.log")
if not _LOG_PATH.parent.exists():  # pragma: no cover - filesystem setup
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

if not LOGGER.handlers:  # pragma: no cover - side effect guard
    _handler = logging.FileHandler(_LOG_PATH)
    _handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    LOGGER.addHandler(_handler)
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False


def run_pipeline(raw_text: str, output_dir: Path) -> Dict:
    """Execute the whole pipeline and return processed result information."""

    LOGGER.info("Starting pipeline for input: %s", raw_text[:200])
    product_id = extract_product_id(raw_text)
    LOGGER.info("Extracted product id: %s", product_id)

    client = DouyinClient()
    product_detail = client.fetch_product_detail(product_id)
    LOGGER.info("Fetched product detail for %s", product_id)

    download_dir = output_dir / product_id / "original"
    downloaded_paths = download_images(product_detail["images"], download_dir)
    LOGGER.info("Downloaded %d images", len(downloaded_paths))

    processed_dir = output_dir / product_id / "processed"
    processed_paths = process_batch(downloaded_paths, processed_dir)
    LOGGER.info("Processed %d images", len(processed_paths))

    return {
        "product_id": product_id,
        "product_detail": product_detail,
        "download_dir": download_dir,
        "processed_dir": processed_dir,
        "downloaded_images": downloaded_paths,
        "processed_images": processed_paths,
    }
