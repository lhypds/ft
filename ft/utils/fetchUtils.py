"""Fetch a web page and extract just its main content text.

``ft`` deliberately avoids downloading images, video, scripts, and other big
binaries — it only wants the readable text of a page. ``trafilatura`` handles
both the HTTP fetch and the boilerplate-stripping content extraction, and also
exposes the page title used to name the output folder.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import trafilatura

# Characters that are illegal (or awkward) in file/folder names on the common
# platforms, plus control characters.
_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
# Anything that looks like a URL separator, collapsed to a single underscore.
_URL_SEP = re.compile(r'[/\\:?#&=<>"|*\s]+')


@dataclass
class Page:
    """A fetched page reduced to its readable essentials."""

    url: str
    title: str
    text: str


def sanitize(text: str, *, keep_spaces: bool = True) -> str:
    """Make ``text`` safe to use as a single path component."""
    text = _ILLEGAL.sub("_", text)
    if not keep_spaces:
        text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text).strip().strip("._ ")
    return text or "untitled"


def escape_url(url: str) -> str:
    """Turn a URL into a filename-safe token.

    Drops the scheme and replaces separators like ``/`` with ``_`` so the
    original URL is still recognizable in the folder name.
    """
    without_scheme = re.sub(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", "", url)
    token = _URL_SEP.sub("_", without_scheme)
    token = re.sub(r"_+", "_", token).strip("._")
    return token or "url"


def folder_name(title: str, url: str, *, max_len: int = 150) -> str:
    """Build the ``[title]_[url]`` folder name for a page (bracketed, yt-style)."""
    title_part = sanitize(title)
    url_part = escape_url(url)
    budget = max_len - len(title_part) - 5  # "[" + "]_[" + "]"
    if 0 < budget < len(url_part):
        url_part = url_part[:budget].rstrip("._")
    name = f"[{title_part}]_[{url_part}]"
    if len(name) > max_len:
        name = name[:max_len].rstrip("._ ")
    return name


def search_folder_name(keyword: str, *, max_len: int = 150) -> str:
    """Build the ``search_result_<keyword>`` folder name for a search."""
    slug = sanitize(keyword, keep_spaces=False)
    name = f"search_result_{slug}"
    if len(name) > max_len:
        name = name[:max_len].rstrip("._")
    return name


def fetch_page(url: str) -> Page:
    """Fetch ``url`` and return its title and main content text.

    Raises ``RuntimeError`` when the page cannot be fetched or no readable
    content could be extracted.
    """
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise RuntimeError(f"failed to fetch {url}")

    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
    )
    if not text or not text.strip():
        raise RuntimeError(f"no readable content extracted from {url}")

    title = ""
    metadata = trafilatura.extract_metadata(downloaded)
    if metadata and metadata.title:
        title = metadata.title.strip()

    return Page(url=url, title=title, text=text.strip())


def save_page(page: Page, output_dir: Path) -> Path:
    """Write ``page`` into ``output_dir/[title]_[url]/content.txt``.

    Returns the path to the written ``content.txt``.
    """
    folder = output_dir / folder_name(page.title, page.url)
    folder.mkdir(parents=True, exist_ok=True)
    content_path = folder / "content.txt"
    content_path.write_text(page.text + "\n", encoding="utf-8")
    return content_path
