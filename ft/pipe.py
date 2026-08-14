"""The default action: fetch a URL's main content text and write it to stdout.

Not a command under ``ft/commands`` on purpose — there is no ``ft pipe`` and no
``ft fetch``. Fetching text is what ``ft`` is for, so a URL on its own is enough:

    ft -u https://example.com/article          the text
    ft -u https://example.com/article --json   {"url":…,"title":…,"text":…}
    ft -u https://example.com/article -m 8000  truncated to 8000 characters

Nothing is saved anywhere (that is ``ft download``): the text goes straight to
whoever reads ``ft``'s stdout — a shell pipeline, or a program that stores it
wherever it wants. Progress and errors go to stderr, so a pipeline only ever
receives the content.
"""

from __future__ import annotations

import argparse
import json
import sys

from .utils.fetchUtils import fetch_page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ft",
        description="Fetch the main content text of a web page and print it to stdout.",
    )
    parser.add_argument("-u", "--url", required=True, help="Web page URL")
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Print a JSON object with the url, title and text instead of the bare text",
    )
    parser.add_argument(
        "-m",
        "--max-chars",
        type=int,
        default=0,
        help="Truncate the text to this many characters (default: no limit)",
    )
    args = parser.parse_args(argv)

    try:
        page = fetch_page(args.url)
    except RuntimeError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    text = page.text
    if args.max_chars > 0:
        text = text[: args.max_chars]

    if args.json:
        # ensure_ascii=False: the text is whatever language the page is in, and a reader that
        # already deals in UTF-8 should not have to decode escapes to see it.
        json.dump({"url": page.url, "title": page.title, "text": text}, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print(text)
    return 0
