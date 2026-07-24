"""Search the internet for text using OpenAI's web search.

The result is saved (as-is) into ``search_result_<keyword>/result.txt``.
Requires ``OPENAI_API_KEY``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import BadRequestError, OpenAI

from ..utils.fetchUtils import search_folder_name

DEFAULT_MODEL = "gpt-5.5"


def web_search(query: str, model: str) -> str:
    """Run an OpenAI web search for ``query`` and return the result text."""
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
    """Write the search result into ``output_dir/search_result_<keyword>/result.txt``."""
    folder = output_dir / search_folder_name(keyword)
    folder.mkdir(parents=True, exist_ok=True)
    result_path = folder / "result.txt"
    result_path.write_text(text + "\n", encoding="utf-8")
    return result_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search the internet for text using OpenAI's web search."
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
        "--openai-model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use for web search (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args(argv)

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        parser.error(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    query = " ".join(args.query)
    try:
        text = web_search(query, args.openai_model)
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
