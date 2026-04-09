#!/usr/bin/env python3
"""
Validate assets that have been added or modified in a PR.

Reads a list of changed file paths from the file passed as argv[1] (one per
line) and validates each one against the rules for its category.

Rules:
  investing/stocks/*.png
    - PNG format
    - exactly 512x512
    - file size < 50 KB
    - filename matches ^[A-Z0-9.]+\\.png$

  liminal/brand/*.svg
    - SVG format with a viewBox attribute
    - file size < 100 KB

  liminal/brand/*.png
    - PNG format, square
    - file size < 200 KB
    - filename matches ^[a-z0-9-]+-(\\d+)\\.png$ where the integer matches
      the actual pixel dimensions

Files outside known category directories are ignored (so meta files like
README, LICENSE, vercel.json, .github/* don't need to pass validation).
"""

import re
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent

STOCK_PATTERN = re.compile(r"^investing/stocks/([A-Z0-9.]+)\.png$")
BRAND_SVG_PATTERN = re.compile(r"^liminal/brand/([a-z0-9-]+)\.svg$")
BRAND_PNG_PATTERN = re.compile(r"^liminal/brand/([a-z0-9-]+)-(\d+)\.png$")

STOCK_MAX_BYTES = 50 * 1024
BRAND_SVG_MAX_BYTES = 100 * 1024
BRAND_PNG_MAX_BYTES = 200 * 1024


class ValidationError(Exception):
    pass


def validate_stock_png(path: Path) -> None:
    size = path.stat().st_size
    if size > STOCK_MAX_BYTES:
        raise ValidationError(
            f"file size {size} bytes exceeds {STOCK_MAX_BYTES} byte limit "
            f"(run pngquant or oxipng to compress)"
        )

    with Image.open(path) as img:
        if img.format != "PNG":
            raise ValidationError(f"format is {img.format}, expected PNG")
        if img.size != (512, 512):
            raise ValidationError(
                f"dimensions are {img.size[0]}x{img.size[1]}, expected 512x512"
            )
        if img.mode not in ("RGBA", "LA"):
            raise ValidationError(
                f"mode is {img.mode}, expected RGBA (transparent background)"
            )


def validate_brand_svg(path: Path) -> None:
    size = path.stat().st_size
    if size > BRAND_SVG_MAX_BYTES:
        raise ValidationError(
            f"file size {size} bytes exceeds {BRAND_SVG_MAX_BYTES} byte limit"
        )

    text = path.read_text(encoding="utf-8", errors="replace")
    if "<svg" not in text:
        raise ValidationError("file does not appear to contain an <svg> element")
    if "viewBox" not in text:
        raise ValidationError(
            "missing viewBox attribute on <svg> — needed for proper scaling"
        )


def validate_brand_png(path: Path, expected_dim: int) -> None:
    size = path.stat().st_size
    if size > BRAND_PNG_MAX_BYTES:
        raise ValidationError(
            f"file size {size} bytes exceeds {BRAND_PNG_MAX_BYTES} byte limit"
        )

    with Image.open(path) as img:
        if img.format != "PNG":
            raise ValidationError(f"format is {img.format}, expected PNG")
        if img.size != (expected_dim, expected_dim):
            raise ValidationError(
                f"dimensions are {img.size[0]}x{img.size[1]}, "
                f"expected {expected_dim}x{expected_dim} (based on filename suffix)"
            )


def validate_one(rel_path: str) -> list[str]:
    """Returns a list of error messages for the given file (empty if valid)."""
    errors: list[str] = []
    path = REPO_ROOT / rel_path

    if not path.exists():
        # Deleted files don't need validation.
        return errors

    if STOCK_PATTERN.match(rel_path):
        try:
            validate_stock_png(path)
        except (ValidationError, OSError) as e:
            errors.append(f"{rel_path}: {e}")
        return errors

    if BRAND_PNG_PATTERN.match(rel_path):
        m = BRAND_PNG_PATTERN.match(rel_path)
        expected_dim = int(m.group(2))
        try:
            validate_brand_png(path, expected_dim)
        except (ValidationError, OSError) as e:
            errors.append(f"{rel_path}: {e}")
        return errors

    if BRAND_SVG_PATTERN.match(rel_path):
        try:
            validate_brand_svg(path)
        except (ValidationError, OSError) as e:
            errors.append(f"{rel_path}: {e}")
        return errors

    # Reject anything that LOOKS like an asset but isn't in a known location.
    if rel_path.startswith(("investing/stocks/", "liminal/brand/")) and not rel_path.endswith(
        (".gitkeep", ".md")
    ):
        errors.append(
            f"{rel_path}: file in known category directory does not match the "
            f"naming convention for that category"
        )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate.py <changed-files-list>", file=sys.stderr)
        return 2

    changed_list = Path(argv[1])
    if not changed_list.exists():
        print(f"changed file list not found: {changed_list}", file=sys.stderr)
        return 2

    files = [
        line.strip()
        for line in changed_list.read_text().splitlines()
        if line.strip()
    ]

    if not files:
        print("no changed files to validate")
        return 0

    all_errors: list[str] = []
    for f in files:
        all_errors.extend(validate_one(f))

    if all_errors:
        print("validation FAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print(f"validated {len(files)} changed file(s) successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
