"""Command line interface for the product processing pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import List

from .pipeline import run_pipeline

LOGGER = logging.getLogger(__name__)


def _parse_arguments(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Douyin product image pipeline")
    parser.add_argument("--input", required=True, help="Raw share link or text")
    parser.add_argument(
        "--output",
        default="output",
        help="Directory to store downloaded and processed images",
    )
    parser.add_argument(
        "--select",
        nargs="*",
        type=int,
        help="Indices of images to display (1-based). Defaults to all.",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_arguments(argv)
    output_dir = Path(args.output)
    result = run_pipeline(args.input, output_dir)

    indices = args.select or list(range(1, len(result["processed_images"]) + 1))
    selected = [
        result["processed_images"][i - 1]
        for i in indices
        if 0 < i <= len(result["processed_images"])
    ]

    print(
        json.dumps(
            {
                "product_id": result["product_id"],
                "processed_images": [str(path) for path in selected],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
