"""Summarize the text content of a web page (or a local text file) with OpenAI."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from ..utils.fetchUtils import fetch_page, save_page

DEFAULT_MODEL = "gpt-5.5"

PROMPT = (
    "You are reading the text content of a web page. Extract the most "
    "informational content — the specific facts, claims, numbers, names, "
    "events, and conclusions a reader would actually want to take away. "
    "Skip navigation text, boilerplate, ads, and filler. Write it as natural "
    "prose, not a bulleted list. Be faithful to the source and do not invent "
    "details. Then summarize and list out the most important points."
)


def summarize_text(text: str, model: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content or ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch a web page (or read a local .txt file) and summarize it with OpenAI."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-u", "--url", help="Web page URL")
    source.add_argument(
        "-f",
        "--file",
        type=Path,
        help="Path to a local text file to summarize",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to save content and summary (default: derived from the "
        "page title for URLs, or the file's folder for files)",
    )
    parser.add_argument(
        "--openai-model",
        default=DEFAULT_MODEL,
        help=f"OpenAI chat model to use for summarization (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args(argv)

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        parser.error(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    if args.url:
        try:
            page = fetch_page(args.url)
        except RuntimeError as err:
            print(f"error: {err}", file=sys.stderr)
            return 1
        base_dir = args.output_dir or Path.cwd()
        content_path = save_page(page, base_dir)
        output_dir = content_path.parent
        stem = content_path.stem
    else:
        if not args.file.is_file():
            parser.error(f"file not found: {args.file}")
        output_dir = args.output_dir or args.file.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = args.file.stem
        content_path = args.file

    text = content_path.read_text(encoding="utf-8").strip()
    if not text:
        print(f"error: {content_path} is empty", file=sys.stderr)
        return 1

    print(f"==> Summarizing {content_path.name} with {args.openai_model}")
    summary = summarize_text(text, args.openai_model)

    summary_path = output_dir / f"{stem}.summary.md"
    summary_path.write_text(summary + "\n", encoding="utf-8")
    print(f"==> Wrote {summary_path}")
    print()
    print(summary)

    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.run([opener, str(summary_path)], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
