"""Build MuseAi rewind lists from local Takeout-style JSON files."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from .classify import classify, genre_for, instrumental_for
except ImportError:  # pragma: no cover - supports `python src/main.py`
    from classify import classify, genre_for, instrumental_for


def load_records(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("items", data.get("activities", []))
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {path}")
    return [item for item in data if isinstance(item, dict)]


def title_of(record: Dict[str, Any]) -> str:
    title = record.get("title") or record.get("video_title") or "Untitled"
    return str(title).strip()


def video_id_of(record: Dict[str, Any]) -> str:
    for key in ("videoId", "video_id", "id"):
        if record.get(key):
            return str(record[key])
    url = str(record.get("url", ""))
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{6,})", url)
    if match:
        return match.group(1)
    channel = record.get("channelName") or record.get("channel") or record.get("uploader") or ""
    return f"title:{title_of(record).lower()}|channel:{str(channel).lower()}"


def parse_time(record: Dict[str, Any]) -> Optional[datetime]:
    raw = record.get("time") or record.get("watched_at") or record.get("timestamp")
    if not raw:
        return None
    value = str(raw).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _recent_enough(record: Dict[str, Any], years: int, now: datetime) -> bool:
    if years <= 0:
        return True
    stamp = parse_time(record)
    return stamp is None or stamp >= now - timedelta(days=365.2425 * years)


def build_rewind(history: Iterable[Dict[str, Any]], likes: Iterable[Dict[str, Any]] = (), comments: Iterable[Dict[str, Any]] = (), years: int = 10, now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    records: Dict[str, Dict[str, Any]] = {}
    for source, items in (("history", history), ("like", likes), ("comment", comments)):
        for raw in items:
            if not _recent_enough(raw, years, now):
                continue
            is_music, confidence, reason = classify(raw)
            if not is_music:
                continue
            key = video_id_of(raw)
            entry = records.setdefault(key, {
                "version_id": key, "title": title_of(raw),
                "artist": str(raw.get("artist") or raw.get("channelName") or raw.get("channel") or "Unknown artist"),
                "genre": genre_for(raw), "instrumental": instrumental_for(raw),
                "plays": 0, "sources": set(), "classification": {"confidence": confidence, "reason": reason},
            })
            entry["sources"].add(source)
            entry["genre"] = genre_for(raw) if entry["genre"] == "Unclassified" else entry["genre"]
            entry["instrumental"] = entry["instrumental"] or instrumental_for(raw)
            if source == "history":
                entry["plays"] += 1
    songs = []
    for entry in records.values():
        entry["sources"] = sorted(entry["sources"])
        entry["discovered_via"] = [s for s in entry["sources"] if s != "history"]
        songs.append(entry)
    songs.sort(key=lambda song: (-song["plays"], song["title"].casefold(), song["version_id"]))
    repeat = [song for song in songs if song["plays"] > 1]
    once = [song for song in songs if song["plays"] == 1]
    return {"songs": songs, "repeat": repeat, "once_only": once, "summary": {
        "total_versions": len(songs), "repeat_versions": len(repeat), "once_only_versions": len(once),
        "total_plays": sum(song["plays"] for song in songs), "artists": len({song["artist"] for song in songs}),
    }}


def _line(song: Dict[str, Any]) -> str:
    flag = " — instrumental/no-lyrics" if song["instrumental"] else ""
    return f"- **{song['title']}** — {song['artist']} · {song['plays']} plays · `{song['version_id']}`{flag}"


def render_original(result: Dict[str, Any]) -> str:
    lines = ["# MuseAi Rewind — Original List", "", "Repeat listens only; ranked most-played first.", ""]
    lines += [_line(song) for song in result["repeat"]] or ["_No repeat-listen songs found._"]
    return "\n".join(lines) + "\n"


def render_genres(result: Dict[str, Any]) -> str:
    groups = defaultdict(list)
    for song in result["repeat"]:
        groups[song["genre"]].append(song)
    lines = ["# MuseAi Rewind — Genre List", "", "The same repeat-listen songs grouped by inferred genre.", ""]
    for genre in sorted(groups, key=str.casefold):
        lines += [f"## {genre}", ""] + [_line(song) for song in groups[genre]] + [""]
    return "\n".join(lines) if groups else "# MuseAi Rewind — Genre List\n\n_No repeat-listen songs found._\n"


def render_once(result: Dict[str, Any]) -> str:
    lines = ["# MuseAi Rewind — Once-only Appendix", "", "Songs with exactly one history listen; excluded from the main list.", ""]
    lines += [_line(song) for song in result["once_only"]] or ["_No once-only songs found._"]
    return "\n".join(lines) + "\n"


def write_outputs(result: Dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "rewind-original.md").write_text(render_original(result), encoding="utf-8")
    (out / "rewind-genres.md").write_text(render_genres(result), encoding="utf-8")
    (out / "rewind-once-only.md").write_text(render_once(result), encoding="utf-8")
    serializable = {**result, "songs": result["songs"], "repeat": result["repeat"], "once_only": result["once_only"]}
    (out / "rewind.json").write_text(json.dumps(serializable, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build local MuseAi YouTube rewind lists")
    parser.add_argument("--history", required=True, type=Path)
    parser.add_argument("--likes", type=Path)
    parser.add_argument("--comments", type=Path)
    parser.add_argument("--years", type=int, default=10)
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    args = parser.parse_args(argv)
    result = build_rewind(load_records(args.history), load_records(args.likes) if args.likes else (), load_records(args.comments) if args.comments else (), args.years)
    write_outputs(result, args.out)
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
