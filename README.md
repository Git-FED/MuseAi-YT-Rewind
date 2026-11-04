# MuseAi YouTube Rewinds

> Rebuild a repeat-listen rewind from your own Google Takeout watch history — locally, transparently, and without an API key.

[![Python >=3.9](https://img.shields.io/badge/Python-%E2%89%A53.9-3776AB?logo=python&logoColor=white)](pyproject.toml) [![Version 0.1.0](https://img.shields.io/badge/version-0.1.0-6C4BFF)](pyproject.toml) [![Core is offline](https://img.shields.io/badge/core-offline-2EA44F)](SPEC.md)

## Why this exists

A platform-generated “rewind” is usually a polished summary of what an algorithm wants to show you. It can flatten live recordings, remixes, lyric videos, and official audio into one vague title—or bury the song you played three times next to something you clicked once.

MuseAi YouTube Rewinds reads your exported history on your machine. It keeps video versions separate, counts history records as plays, treats likes and comments as discovery signals only, and puts one-off listens in an appendix instead of pretending they define your taste.

The core is deliberately small and offline. No login, scraper, YouTube API key, upload path, or network request is needed to build the rewind.

## See it work

**Live demo:** not published yet. The repository does include a static marketing/sample site under [`site/`](site/), but it is not a hosted replacement for running the CLI.

The quickest working demo is:

```bash
python3 src/main.py \
  --history examples/watch-history-sample.json \
  --likes examples/likes-sample.json \
  --comments examples/comments-sample.json \
  --years 10 \
  --out /tmp/museai-rewind
```

Then inspect the main result:

```bash
cat /tmp/museai-rewind/rewind-original.md
```

The bundled sample produces **5 total versions**, **1 repeat-listen version**, **3 once-only versions**, **6 total history plays**, and **4 artists**. The liked-only “Northern Lights” candidate is retained as a zero-play discovery rather than inflating the count.

Main example inputs:

- [`watch-history-sample.json`](examples/watch-history-sample.json) — repeated official audio, a separate live version, an instrumental, non-music content, and a one-off song.
- [`likes-sample.json`](examples/likes-sample.json) — a missing song discovered through a like plus a repeated history item.
- [`comments-sample.json`](examples/comments-sample.json) — optional comment-based discovery.

## The visual idea

These are the real promotional images used by the HTML landing page in [`site/index.html`](site/index.html). They are intentionally playful: the project is a serious local data tool with a sense of humor about listening habits.

| The algorithm is tangled | One listen is not a personality |
| --- | --- |
| ![Frazzled paper-bag algorithm tangled in music cables and surrounded by records, a cassette, headphones, and music notes](site/assets/promo-algorithm-paper-bag.png) | ![Dramatic goldfish wearing headphones and listening to a single glowing music note](site/assets/promo-one-listen.png) |

## Quick start

The rewind core uses only the Python standard library.

```bash
# from the repository root
python3 src/main.py \
  --history examples/watch-history-sample.json \
  --likes examples/likes-sample.json \
  --comments examples/comments-sample.json \
  --years 10 \
  --out outputs/demo
```

Export the repeat-listen Markdown file into portable formats:

```bash
python3 src/export.py \
  --original outputs/demo/rewind-original.md \
  --out outputs/demo/rewind
```

This creates `rewind.csv`, `rewind.json`, `rewind-stats.json`, and `rewind-playlist.txt` beside the Markdown outputs.

### Test it

The repository includes a dependency-free runner, so this works in a clean Python environment:

```bash
python3 tests/run.py
```

Pytest is also supported when installed:

```bash
python3 -m pytest tests/ -q
```

The five test functions use only the standard library and do not make network requests.

## What it produces

For a normal run, the CLI writes:

- `rewind-original.md` — repeat-listen songs, ranked by play count.
- `rewind-genres.md` — those repeat-listen songs grouped by inferred genre.
- `rewind-once-only.md` — songs with exactly one history listen.
- `rewind.json` — machine-readable records, sources, classification reasoning, and summary counts.

The exporter adds CSV, JSON, artist stats, and a simple playlist of version IDs. The output directory is created automatically and existing files with those names are replaced.

## How it decides what counts

- **Music filter:** explainable offline heuristics look for music signals and reject obvious tutorials, news, gameplay, and podcasts.
- **Identity:** a YouTube video ID is the version key. Without one, the normalized title and channel are used.
- **Counting:** every history record counts once. Likes and comments can discover a missing version, but never add a play.
- **Date window:** the default is the most recent 10 years. Use `--years 0` to disable the window.
- **Classification:** genre and instrumental/no-lyrics flags are retained in the JSON so the result can be audited.

The full input and behavior contract is in [`SPEC.md`](SPEC.md).

## Optional YouTube tools

The local rewind is independent of the optional channel tools:

```bash
YOUTUBE_API_KEY=... python3 src/channel_scan.py --channel UCxxxx --out scan.json

YOUTUBE_OAUTH_TOKEN=... python3 src/channel_edit.py \
  --video VIDEO_ID \
  --title-prefix "[MuseAi] "
```

The scanner reads public channel data. The editor is dry-run by default and only changes an authenticated user's own video when `--apply` is supplied. Credentials must come from environment variables; see [`API.md`](API.md) and [`.env.example`](.env.example).

## Static site and deployment

The [`site/`](site/) directory is a no-build animated landing page and sample walkthrough. It includes the favicon, demo page, privacy/about pages, age-gated support integrations, community page, Join Email List page, custom `404.html`, `.nojekyll`, Cloudflare `_headers`, Cloudflare `_redirects`, and a route manifest.

Preview it locally:

```bash
python3 -m http.server 8080 --directory site
```

Open <http://localhost:8080/index.html>. GitHub Pages and Cloudflare Pages/Workers are supported by the file layout, but this repository currently contains **no GitHub Actions deployment workflow, no custom domain, no Git remote, and no already-published live URL**. To deploy manually, publish `site/` as the static output directory.

## Privacy and boundaries

The rewind core reads local files and writes local outputs. It has no upload endpoint, scraper, analytics, or API requirement. Do not commit Google Takeout exports, generated personal outputs, API keys, OAuth tokens, or service-role credentials.

The optional static-site payment, community, and email-list pages load third-party widgets only when a visitor opens those pages. Payment details stay with the payment provider. The email-list page uses the supplied Supabase publishable browser key; no Supabase service-role key is included here.

## Repository map

```text
src/main.py              local rewind CLI entry point
src/classify.py          offline music, genre, and instrumental heuristics
src/export.py            Markdown-to-CSV/JSON/stats/playlist exporter
src/channel_scan.py      optional public YouTube channel scanner
src/channel_edit.py      optional dry-run own-video editor
examples/                small runnable JSON fixtures
outputs/                 generated-output examples/placeholders
site/assets/             favicon and promotional images used by the HTML site
site/                    static marketing and sample site
tests/run.py             dependency-free test runner
tests/test_main.py       test functions
SPEC.md                  input/output and behavior contract
API.md                   optional YouTube API boundaries
```

## Status

Version `0.1.0`. The core CLI, exporter, optional channel modules, examples, tests, and static site are present. There is no license file in the repository yet, and no hosted demo or automated deployment workflow is currently configured.

## License

No license has been declared in this repository yet. Treat the code as all-rights-reserved until a license is added.
