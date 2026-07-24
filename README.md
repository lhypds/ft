
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

Downloaded pages are saved under a folder named `[web page title]_[url]` (the
URL is escaped — `/` becomes `_`, etc.), containing a `content.txt` file.
Summaries are written next to the content as `content.summary.md`.

Search results are saved under `search_result_[keyword]/result.txt` — e.g.
searching `google history` writes to `search_result_google_history/result.txt`.

Both `search` and `summarize` require `OPENAI_API_KEY` — copy `.env.example` to
`.env` and set it.

Shortcuts: combine the command's first letter with its flag, e.g.
`ft -du [URL]` == `ft download -u [URL]` (also `-su`, `-sf`).
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
