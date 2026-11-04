"""Prepare optional edits to an authenticated user's own YouTube video."""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, Optional

try:
    from .youtube_api import YouTubeClient
except ImportError:
    from youtube_api import YouTubeClient


def build_edit(video_id: str, title_prefix: str = "", title_suffix: str = "", description_footer: str = "") -> Dict[str, Any]:
    snippet: Dict[str, Any] = {"title": f"{title_prefix}{video_id}{title_suffix}"}
    if description_footer:
        snippet["description"] = description_footer
    return {"id": video_id, "snippet": snippet, "status": {}}


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview or apply an own-video YouTube edit")
    parser.add_argument("--video", required=True)
    parser.add_argument("--title-prefix", default="")
    parser.add_argument("--title-suffix", default="")
    parser.add_argument("--description-footer", default="")
    parser.add_argument("--apply", action="store_true", help="send the OAuth request; otherwise preview only")
    args = parser.parse_args()
    edit = build_edit(args.video, args.title_prefix, args.title_suffix, args.description_footer)
    if not args.apply:
        print(json.dumps({"dry_run": True, "would_send": edit}, indent=2))
        return 0
    result = YouTubeClient().update_video(edit)
    print(json.dumps({"dry_run": False, "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
