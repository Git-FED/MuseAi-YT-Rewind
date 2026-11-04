# Optional YouTube API tools

The rewind core uses Google Takeout because the YouTube Data API cannot read private watch history. The modules in `src/` are deliberately separate from the local rewind path.

## Access model

| Credential | Useful for | Not useful for |
| --- | --- | --- |
| `YOUTUBE_API_KEY` | Public channel info, uploads, public video details | Private history, likes, comments, edits |
| `YOUTUBE_OAUTH_TOKEN` | OAuth-authorized edits to your own videos | Sharing access with this repository or another person |

Never commit either credential. Use environment variables or a local untracked `.env` file.

## Implemented endpoints

- `GET channels?part=snippet,statistics,contentDetails&id=...` — channel details and uploads playlist.
- `GET playlistItems?part=snippet&playlistId=...` — paged uploads.
- `GET videos?part=snippet,statistics,contentDetails&id=...` — details in batches.
- `PUT videos?part=snippet,status&id=...` — own-video edits, OAuth only.

The expensive `search` endpoint is intentionally not used by the channel scanner. A channel scan of hundreds of videos is normally much cheaper than a search-heavy workflow. The default project quota is 10,000 units/day, but exact costs can change; check Google's current API documentation before large runs.

## Examples

```bash
YOUTUBE_API_KEY=... python3 src/channel_scan.py --channel UCxxxx --out scan.json
YOUTUBE_OAUTH_TOKEN=... python3 src/channel_edit.py --video VIDEO_ID --title-prefix "[MuseAi] "
YOUTUBE_OAUTH_TOKEN=... python3 src/channel_edit.py --video VIDEO_ID --title-suffix " | MuseAi" --apply
```

Editing is dry-run by default and only sends a request with `--apply`. The module does not provide a bulk-edit command.
