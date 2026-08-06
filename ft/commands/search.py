"""Search the internet for text.

Uses the Brave Search API by default; falls back to OpenAI's web search when
``BRAVE_API_KEY`` is not set. The result is saved (as-is) into
``[websearch_result]_[keyword]/result.txt``.

Requires ``BRAVE_API_KEY`` (preferred) or ``OPENAI_API_KEY``.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from ..utils.fetchUtils import search_folder_name

DEFAULT_MODEL = "gpt-5.6"

BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
# Brave's `country` takes a 2-character country code (there is no "en" country),
# so the English-region default is US with English as both the content and the
# response-metadata language.
DEFAULT_COUNTRY = "us"
DEFAULT_SEARCH_LANG = "en"
DEFAULT_UI_LANG = "en-US"
# Upper bound on the assembled result text; whole results are dropped rather
# than cut mid-way, so the output never ends on half a snippet.
DEFAULT_MAX_CHARS = 8192
# Brave caps a single page of web results at 20.
BRAVE_COUNT = 20
BRAVE_TIMEOUT = 30

_TAG = re.compile(r"<[^>]+>")


def _plain(text: str) -> str:
    """Strip any residual markup and entities from a Brave field."""
    return html.unescape(_TAG.sub("", text or "")).strip()


def brave_search(
    query: str,
    *,
    api_key: str,
    country: str = DEFAULT_COUNTRY,
    search_lang: str = DEFAULT_SEARCH_LANG,
    ui_lang: str = DEFAULT_UI_LANG,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> str:
    """Run a Brave web search for ``query`` and return the result text."""
    params = urllib.parse.urlencode(
        {
            "q": query,
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "count": BRAVE_COUNT,
            "text_decorations": 0,
        }
    )
    request = urllib.request.Request(
        f"{BRAVE_ENDPOINT}?{params}",
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=BRAVE_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace").strip()
        raise RuntimeError(f"Brave API returned {err.code}: {detail}") from err

    results = (payload.get("web") or {}).get("results") or []
    return _format_results(results, max_chars=max_chars)


def _format_results(results: list[dict], *, max_chars: int) -> str:
    """Render Brave's result objects as plain text, capped at ``max_chars``."""
    blocks: list[str] = []
    used = 0
    for index, result in enumerate(results, start=1):
        title = _plain(result.get("title", "")) or "(untitled)"
        url = (result.get("url") or "").strip()
        description = _plain(result.get("description", ""))
        lines = [f"{index}. {title}", url]
        if description:
            lines.append(description)
        block = "\n".join(line for line in lines if line)
        # +2 for the blank line joining this block to the previous one.
        cost = len(block) + (2 if blocks else 0)
        if blocks and used + cost > max_chars:
            break
        blocks.append(block)
        used += cost
    return "\n\n".join(blocks)[:max_chars].strip()


def openai_search(query: str, model: str) -> str:
    """Run an OpenAI web search for ``query`` and return the result text."""
    from openai import BadRequestError, OpenAI

    client = OpenAI()
    try:
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            input=query,
        )
    except BadRequestError:
        # Older API surfaces expose the tool as "web_search_preview".
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search_preview"}],
            input=query,
        )
    return (response.output_text or "").strip()


def save_result(keyword: str, text: str, output_dir: Path) -> Path:
    """Write the search result into ``output_dir/[websearch_result]_[keyword]/result.txt``."""
    folder = output_dir / search_folder_name(keyword)
    folder.mkdir(parents=True, exist_ok=True)
    result_path = folder / "result.txt"
    result_path.write_text(text + "\n", encoding="utf-8")
    return result_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search the internet for text using Brave Search (or OpenAI web search)."
    )
    parser.add_argument("query", nargs="+", help="Text to search for")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to save the result into (default: current directory)",
    )
    parser.add_argument(
        "--engine",
        choices=("auto", "brave", "openai"),
        default="auto",
        help="Search backend (default: auto — Brave when BRAVE_API_KEY is set, else OpenAI)",
    )
    parser.add_argument(
        "--country",
        default=DEFAULT_COUNTRY,
        help=f"Brave result country, 2-letter code (default: {DEFAULT_COUNTRY})",
    )
    parser.add_argument(
        "--search-lang",
        default=DEFAULT_SEARCH_LANG,
        help=f"Brave content language (default: {DEFAULT_SEARCH_LANG})",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Maximum characters of Brave result text (default: {DEFAULT_MAX_CHARS})",
    )
    parser.add_argument(
        "--openai-model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use when falling back to OpenAI (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args(argv)

    load_dotenv()
    brave_key = os.getenv("BRAVE_API_KEY", "").strip()

    engine = args.engine
    if engine == "auto":
        engine = "brave" if brave_key else "openai"
    if engine == "brave" and not brave_key:
        parser.error(
            "BRAVE_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    if engine == "openai" and not os.getenv("OPENAI_API_KEY"):
        parser.error(
            "Neither BRAVE_API_KEY nor OPENAI_API_KEY is set. "
            "Copy .env.example to .env and add a key."
        )

    query = " ".join(args.query)
    try:
        if engine == "brave":
            text = brave_search(
                query,
                api_key=brave_key,
                country=args.country,
                search_lang=args.search_lang,
                max_chars=args.max_chars,
            )
        else:
            text = openai_search(query, args.openai_model)
    except Exception as err:  # noqa: BLE001 - surface any backend failure cleanly
        print(f"error: search failed: {err}", file=sys.stderr)
        return 1

    if not text:
        print(f"No results for {query!r}.")
        return 0

    result_path = save_result(query, text, args.output_dir)
    print(f"==> Saved {result_path}")
    print()
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
