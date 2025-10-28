"""Background removal utilities using rembg."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Iterable, List

try:  # pragma: no cover - exercised through tests with monkeypatching
    from rembg import remove
except ImportError:  # pragma: no cover
    remove = None  # type: ignore

LOGGER = logging.getLogger(__name__)


def remove_background(image_path: Path, output_path: Path) -> Path:
    """Remove background for a single image keeping PNG format."""

    if remove is None:  # pragma: no cover - environment without rembg
        raise ImportError("rembg is required for background removal")

    raw_bytes = image_path.read_bytes()
    result = remove(raw_bytes)
    try:
        from PIL import Image  # type: ignore
    except ImportError:  # pragma: no cover - fallback when pillow missing
        output_path.write_bytes(result)
        return output_path

    with Image.open(io.BytesIO(result)) as image:
        image.save(output_path, format="PNG")
    return output_path


def process_batch(paths: Iterable[Path], output_dir: Path) -> List[Path]:
    """Process a batch of images and return the paths of successful outputs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    processed: List[Path] = []
    for path in paths:
        try:
            output_path = output_dir / f"{path.stem}_transparent.png"
            remove_background(path, output_path)
            processed.append(output_path)
        except Exception as exc:  # pragma: no cover - logging path
            LOGGER.error("Failed to process %s: %s", path, exc)
    return processed
