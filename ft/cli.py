"""ft CLI dispatcher.

Usage: ft <command> [args...]

Forwards all arguments after <command> to ft.commands.<command>'s main().
"""

from __future__ import annotations

import importlib
import sys
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path

# Single-letter command aliases for the URL-taking commands:
# `ft -du <URL>` == `ft download -u <URL>`.
SHORTHANDS: dict[str, str] = {
    "d": "download",
    "s": "summarize",
}

# Single-letter aliases that expand straight to a command with no flag
# letter attached: `ft -w "some text"` == `ft search "some text"`.
DIRECT_SHORTHANDS: dict[str, str] = {
    "w": "search",
}

# One-line description per command shown by `ft -h`. Full per-command
# options are reachable via `ft <command> -h`.
COMMAND_HELP: dict[str, str] = {
    "download": "Download the main content text of a web page (-u <URL>).",
    "summarize": "Summarize a web page (-u <URL>) or text file (-f <FILE>) using OpenAI.",
    "search": 'Search the internet with OpenAI web search: ft search "some text".',
}


def _version_string() -> str:
    root = Path(__file__).resolve().parent.parent
    vf = root / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip()
    try:
        return pkg_version("ft")
    except PackageNotFoundError:
        return "0.0.0"


def _print_help() -> None:
    available = sorted(
        p.stem
        for p in (Path(__file__).resolve().parent / "commands").glob("*.py")
        if not p.stem.startswith("_")
    )
    print("usage: ft <command> [args...]")
    print("       ft -h | --help        Show this help.")
    print("       ft -v | --version     Show the installed version.")
    print()
    print("commands:")
    name_width = max((len(c) for c in available), default=0)
    for cmd in available:
        description = COMMAND_HELP.get(cmd)
        if description is None:
            print(f"  {cmd}")
        else:
            print(f"  {cmd:<{name_width}}  {description}")
    print()
    print("shortcuts: ft -du == ft download -u  (also -su, -sf, -w)")
    print()
    print("Run `ft <command> -h` for the full options of a single command.")


def _expand_shorthand(argv: list[str]) -> list[str]:
    """Expand `-du <URL>` / `-w <query>` style shortcuts into their full form."""
    if not argv:
        return argv
    first = argv[0]
    if len(first) < 2 or first[0] != "-" or not first[1:].isalpha():
        return argv
    letters = first[1:]
    if len(letters) == 1 and letters in DIRECT_SHORTHANDS:
        return [DIRECT_SHORTHANDS[letters], *argv[1:]]
    if len(letters) >= 2 and letters[0] in SHORTHANDS:
        return [SHORTHANDS[letters[0]], f"-{letters[1:]}", *argv[1:]]
    return argv


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-v", "--version"):
        print(_version_string())
        return 0

    argv = _expand_shorthand(argv)

    if len(argv) < 1 or argv[0] in ("-h", "--help"):
        _print_help()
        return 0 if argv else 1

    command, *rest = argv
    try:
        module = importlib.import_module(f"ft.commands.{command}")
    except ModuleNotFoundError:
        print(f"ft: unknown command '{command}'", file=sys.stderr)
        return 2

    return module.main(rest)


def run() -> int:
    """Console script entry point (reads sys.argv)."""
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
