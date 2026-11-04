"""Explainable, dependency-free heuristics for classifying YouTube records."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Tuple

MUSIC_TERMS = {
    "official video", "official audio", "music video", "lyrics", "lyric video",
    "audio", "remix", "live", "cover", "soundtrack", "ost", "instrumental",
    "piano", "ambient", "mix", "single", "album", "ep", "session",
}
NON_MUSIC_TERMS = {
    "how to", "tutorial", "review", "news", "gameplay", "walkthrough",
    "podcast", "interview", "reaction", "unboxing", "lecture", "vlog",
}
INSTRUMENTAL_TERMS = {"instrumental", "no lyrics", "without vocals", "piano", "study music", "ambient"}
GENRE_TERMS = {
    "rock": "Rock", "metal": "Metal", "jazz": "Jazz", "classical": "Classical",
    "piano": "Classical", "ambient": "Ambient", "lofi": "Lo-fi", "lo-fi": "Lo-fi",
    "hip hop": "Hip-hop", "hip-hop": "Hip-hop", "rap": "Hip-hop", "r&b": "R&B",
    "soul": "Soul", "folk": "Folk", "country": "Country", "blues": "Blues",
    "electronic": "Electronic", "edm": "Electronic", "house": "Electronic",
    "techno": "Electronic", "synth": "Synth-pop", "pop": "Pop", "punk": "Punk",
    "soundtrack": "Soundtrack", "ost": "Soundtrack", "reggae": "Reggae",
}


def _text(record: Dict[str, Any]) -> str:
    fields = [record.get(key, "") for key in ("title", "video_title", "channelName", "channel", "description", "genre", "tags")]
    return " ".join(str(value) for value in fields if value).lower()


def _truthy(record: Dict[str, Any], keys: Iterable[str]) -> bool:
    for key in keys:
        value = record.get(key)
        if isinstance(value, bool) and value:
            return True
        if isinstance(value, str) and value.strip().lower() in {"yes", "true", "1", "instrumental"}:
            return True
    return False


def classify(record: Dict[str, Any]) -> Tuple[bool, float, str]:
    """Return (is_music, confidence, reason) for a single record."""
    text = _text(record)
    explicit_genre = str(record.get("genre", "")).strip()
    if _truthy(record, ("is_music", "music")):
        return True, 1.0, "explicit music field"
    if any(term in text for term in NON_MUSIC_TERMS):
        return False, 0.9, "non-music keyword"
    hits = sum(1 for term in MUSIC_TERMS if term in text)
    # Artist-like channel/title metadata and an explicit genre are useful signals.
    if explicit_genre:
        hits += 2
    if record.get("artist") or record.get("artist_name"):
        hits += 2
    if hits:
        return True, min(0.55 + hits * 0.1, 0.99), "music keyword or metadata"
    # Keep ambiguous records only when they look like a compact song title rather than prose.
    title = str(record.get("title", record.get("video_title", ""))).strip()
    if title and len(title.split()) <= 8 and len(title) <= 100 and not re.search(r"[.!?]", title):
        return True, 0.51, "ambiguous short title"
    return False, 0.2, "no music signal"


def genre_for(record: Dict[str, Any]) -> str:
    explicit = str(record.get("genre", "")).strip()
    if explicit:
        return explicit
    text = _text(record)
    for term, genre in GENRE_TERMS.items():
        if term in text:
            return genre
    return "Unclassified"


def instrumental_for(record: Dict[str, Any]) -> bool:
    if _truthy(record, ("instrumental", "no_lyrics", "noLyrics", "lyrics_missing")):
        return True
    text = _text(record)
    return any(term in text for term in INSTRUMENTAL_TERMS)
