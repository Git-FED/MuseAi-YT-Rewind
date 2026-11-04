"""Scan a public YouTube channel using an API key; no edits are made."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .youtube_api import YouTubeClient
except ImportError:
    from youtube_api import YouTubeClient


def scan(channel_id: str, client: Optional[YouTubeClient] = None) -> Dict[str, Any]:
    client = client or YouTubeClient()
    channel = client.channel(channel_id)
    uploads_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    upload_items = client.uploads(uploads_id)
    ids = [item.get("contentDetails", {}).get("videoId") for item in upload_items]
    videos = client.videos([video_id for video_id in ids if video_id])
    rows: List[Dict[str, Any]] = []
    for video in videos:
        snippet = video.get("snippet", {})
        rows.append({"video_id": video.get("id"), "title": snippet.get("title", ""), "published_at": snippet.get("publishedAt"), "views": video.get("statistics", {}).get("viewCount"), "likes": video.get("statistics", {}).get("likeCount"), "missing_description": not bool(snippet.get("description", "").strip()), "missing_tags": not bool(snippet.get("tags")), "has_thumbnail": bool(snippet.get("thumbnails"))})
    return {"channel": channel.get("snippet", {}), "video_count": len(rows), "videos": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a public YouTube channel")
    parser.add_argument("--channel", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = scan(args.channel)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
