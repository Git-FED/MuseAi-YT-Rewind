# MuseAi Rewind Specification

## Input

Each input file is a JSON array. Takeout exports are commonly arrays of objects with an `activity` or `title` field and nested `details`.

The parser accepts these common fields:

- `title` or `video_title`: displayed title.
- `videoId`, `video_id`, or a YouTube URL: stable version identity.
- `time`, `watched_at`, or `timestamp`: ISO 8601 timestamp.
- `channelName`, `channel`, or `uploader`: channel/artist hint.
- `description`, `tags`, `genre`, `lyrics`, and `instrumental`: optional classification hints.

Likes and comments use the same general shape. Their records are candidates only: a liked or commented song with no history record is included with a play count of 0 and marked as `discovered_via` metadata. It is never allowed to inflate a watch count.

## Classification

The default classifier is intentionally conservative and offline. It uses positive music signals such as music keywords, audio-only labels, artist/title patterns, and supplied metadata, while rejecting obvious non-music signals such as tutorials, news, gameplay, and podcasts. The decision and score are retained in JSON output so users can audit or override the heuristic later.

Genre is inferred from explicit metadata first, then title/channel keywords, and otherwise defaults to `Unclassified`. A song is flagged `instrumental/no-lyrics` when an explicit field says so or when title/metadata contains a strong instrumental cue.

## Counting and identity

A version key is the video ID when available. Without a video ID, the normalized title plus channel is used. This keeps different versions separate whenever Takeout provides stable IDs.

History records are counted once per record. Records from likes and comments can add a missing version but do not add plays. The default date window is the most recent 10 years relative to the current date; `--years 0` disables filtering.

## Outputs

The CLI writes:

- `rewind-original.md`: repeat-listen songs, descending play count.
- `rewind-genres.md`: the same repeat-listen songs grouped by inferred genre.
- `rewind-once-only.md`: songs with exactly one watch.
- `rewind.json`: machine-readable records and summary.

The output directory is created if missing. Existing files with those names are replaced.

## Privacy and API boundaries

The core never calls YouTube. The optional API modules use the public Data API only for channel scanning and OAuth only for edits to the authenticated user's own videos. API keys and OAuth tokens must come from environment variables; they are never stored in this repository.
