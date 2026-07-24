
ft
==

`ft` is short for **fetch text**.

Tools for fetching, summarizing, and searching text from the web — the readable
content of a page, without the images, video, or other big files.


Setup
-----

`./setup.sh`
`./install.sh`

Uninstall
`./uninstall.sh`


Commands
--------

`ft search "some text"` - Search the internet using OpenAI web search; saves the result text.
`ft download -u [URL]` - Fetch a web page and save just its main content text.
`ft summarize -u [URL]` or `-f [FILE]` - Fetch (or read a `.txt` file) and summarize with OpenAI.

Downloaded pages are saved under a folder named `[web page title]_[url]`
(brackets included, like the `yt` command's folder naming; the URL is
escaped — `/` becomes `_`, etc.), containing a `content.txt` file.
Summaries are written next to the content as `content.summary.md`.

Search results are saved under `[websearch_result]_[keyword]/result.txt` — e.g.
searching `google history` writes to `[websearch_result]_[google_history]/result.txt`.

Both `search` and `summarize` require `OPENAI_API_KEY` — copy `.env.example` to
`.env` and set it.

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
