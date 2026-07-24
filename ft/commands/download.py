"""Download the main content text of a web page given its URL.

Only readable text is saved — images, video, scripts, and other large assets
are ignored. Output lands in ``[web page title]_[escaped url]/content.txt``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..utils.fetchUtils import fetch_page, save_page


def download(url: str, output_dir: Path) -> Path:
    """Fetch ``url`` and save its content text, returning the file path."""
    page = fetch_page(url)
    content_path = save_page(page, output_dir)
    return content_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download the main content text of a web page (no images or big files)."
    )
    parser.add_argument("-u", "--url", required=True, help="Web page URL")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to save the content into (default: current directory)",
    )
    args = parser.parse_args(argv)

    try:
        content_path = download(args.url, args.output_dir)
    except RuntimeError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"==> Saved {content_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
