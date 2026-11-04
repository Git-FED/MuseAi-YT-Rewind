"""Export rewind Markdown or JSON into portable formats."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def parse_markdown(path: Path) -> List[Dict[str, Any]]:
    rows = []
    pattern = re.compile(r"^- \*\*(.*?)\*\* — (.*?) · (\d+) plays · `([^`]+)`(?: — instrumental/no-lyrics)?$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if match:
            rows.append({"title": match.group(1), "artist": match.group(2), "plays": int(match.group(3)), "version_id": match.group(4), "instrumental": "instrumental/no-lyrics" in line})
    return rows


def export(original: Path, out_prefix: Path) -> Dict[str, Any]:
    rows = parse_markdown(original)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    with (out_prefix.with_suffix(".csv")).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["title", "artist", "plays", "version_id", "instrumental"])
        writer.writeheader(); writer.writerows(rows)
    out_prefix.with_suffix(".json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    artists = {}
    for row in rows:
        artists[row["artist"]] = artists.get(row["artist"], 0) + row["plays"]
    summary = {"total_versions": len(rows), "total_plays": sum(row["plays"] for row in rows), "top_artists": sorted(artists.items(), key=lambda item: (-item[1], item[0]))[:10]}
    out_prefix.with_name(out_prefix.name + "-stats.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    playlist = "\n".join(row["version_id"] for row in rows) + ("\n" if rows else "")
    out_prefix.with_name(out_prefix.name + "-playlist.txt").write_text(playlist, encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a rewind Markdown list")
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(export(args.original, args.out), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
