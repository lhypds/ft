
ft
==

`ft` is short for **fetch text**.

Tools for fetching, summarizing, and searching text from the web — the readable
content of a page, without the images, video, or other big files.


Install
-------

Linux and macOS, one command — downloads the latest release and installs
`ft` into `~/.local/bin`:

```bash
curl -fsSL https://raw.githubusercontent.com/lhypds/ft/main/get.sh | bash
```

Options: `--version 0.0.2` to pin a release, `--dir PATH` to unpack somewhere
other than `~/.local/share/ft` (`bash -s -- --version 0.0.2` when piping).
Re-run it to upgrade — or just use `ft update`; your settings and virtualenv are
kept either way, the one exception being the move described just below.

Where things go, following the XDG base directory spec:

| Path | Holds |
| ---- | ----- |
| `~/.local/bin/ft` | the command — the only part that needs to be on `PATH` |
| `~/.local/share/ft/` | the program and its virtualenv (`$XDG_DATA_HOME`) |
| `~/.config/ft/.env` | the API keys (`$XDG_CONFIG_HOME`) |

An install from an earlier release sits in `~/.ft`. The installer moves it the
next time it runs — `ft update` included — and rebuilds the virtualenv at the new
path, because a virtualenv records its own location and stops working when moved.
Nothing else changes: the settings file is untouched, and Playwright's browser
download is cached outside the install either way.

From a checkout instead:

`./setup.sh`
`./install.sh`

Uninstall
`./uninstall.sh`


Settings
--------

API keys live in `~/.config/ft/.env` (`$XDG_CONFIG_HOME/ft/.env` if set):

| Key              | Required | Used for                                             |
| ---------------- | -------- | ---------------------------------------------------- |
| `OPENAI_API_KEY` | yes      | `summarize`, and `search` when there is no Brave key |
| `BRAVE_API_KEY`  | no       | `search` — the better backend when set                |

`ft` asks for a missing key the first time it needs one and saves the answer
there. A key exported in your shell always wins, and a `.env` next to the
install or checkout takes precedence over `~/.config`.


Commands
--------

`ft -u [URL]` - Fetch a web page and print its main content text to stdout. No
command name: fetching text is what `ft` is for, so a URL on its own is enough.
`ft search "some text"` - Search the internet using Brave Search; saves the result text.
`ft download -u [URL]` - Fetch a web page and save just its main content text.
`ft summarize -u [URL]` or `-f [FILE]` - Fetch (or read a `.txt` file) and summarize with OpenAI.
`ft update` - Update to the latest GitHub release (`-f` to force; `git clone` users should `git pull` instead).

The default action is the piping counterpart of `download`: it saves nothing,
and the text goes straight to whoever reads `ft`'s stdout — a shell pipeline, or
a program that stores it wherever it wants. Progress and errors go to stderr, so
a pipeline only ever receives the content.

```bash
ft -u "https://example.com/article"                 # the text
ft -u "https://example.com/article" --json          # {"url":…,"title":…,"text":…}
ft -u "https://example.com/article" -m 8000         # truncated to 8000 characters
```

Pages are fetched with a plain HTTP request first; if that returns little or
no readable text (typical of JavaScript single-page apps, e.g. ChatGPT share
links), `ft` retries with a headless Chromium browser via Playwright and
keeps whichever result has more content.

Downloaded pages are saved under a folder named `[web page title]_[url]`
(brackets included, like the `yt` command's folder naming; the URL is
escaped — `/` becomes `_`, etc.), containing a `content.txt` file.
Summaries are written next to the content as `content.summary.md`.

Search results are saved under `[websearch_result]_[keyword]/result.txt` — e.g.
searching `google history` writes to `[websearch_result]_[google_history]/result.txt`.

`search` uses the Brave Search API when `BRAVE_API_KEY` is set, and otherwise
falls back to OpenAI web search with `OPENAI_API_KEY`. Brave defaults to the
`us` country, `en` content language, and at most 8192 characters of result text
(`--country`, `--search-lang`, `--max-chars`, and `--engine brave|openai`
override this). `summarize` always requires `OPENAI_API_KEY` — see Settings
above.

Shortcuts: combine the command's first letter with its flag, e.g.
`ft -du [URL]` == `ft download -u [URL]` (also `-su`, `-sf`). `search` takes
no flag, so its shortcut is just the letter: `ft -w "some text"` ==
`ft search "some text"`.
Run `ft -h` or `ft <command> -h` for full options.


Examples
--------

```bash
ft search "faster whisper transcription"
ft download -u "https://example.com/some/article"
ft summarize -u "https://example.com/some/article"
```


Scripts
-------

Clear  
`./clear.sh`  
Build  
`./build.sh` - Build the wheel and sdist into `dist/`.  
Release  
`./release.sh` - Create a new release on GitHub.  
