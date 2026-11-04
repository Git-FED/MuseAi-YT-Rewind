import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from channel_edit import build_edit
from main import build_rewind, load_records, render_genres, render_original


def test_sample_has_repeat_once_and_separate_versions():
    history = load_records(ROOT / "examples/watch-history-sample.json")
    result = build_rewind(history, years=0)
    assert result["summary"]["repeat_versions"] == 1
    assert result["summary"]["once_only_versions"] == 3
    assert {song["version_id"] for song in result["repeat"]} == {"m83-midnight-official"}
    assert "m83-midnight-live" in {song["version_id"] for song in result["once_only"]}


def test_likes_and_comments_do_not_inflate_play_count():
    history = [{"title": "Song (Official Audio)", "videoId": "song-1", "channelName": "Artist"}]
    likes = [{"title": "Song (Official Audio)", "videoId": "song-1", "channelName": "Artist"}, {"title": "New (Official Audio)", "videoId": "new-1"}]
    result = build_rewind(history, likes, likes, years=0)
    songs = {song["version_id"]: song for song in result["songs"]}
    assert songs["song-1"]["plays"] == 1
    assert songs["new-1"]["plays"] == 0
    assert songs["new-1"]["discovered_via"] == ["comment", "like"]


def test_genre_render_marks_instrumental():
    result = build_rewind([{"title": "Piano instrumental", "videoId": "piano-1", "genre": "Classical"}, {"title": "Piano instrumental", "videoId": "piano-1", "genre": "Classical"}], years=0)
    assert "instrumental/no-lyrics" in render_original(result)
    assert "## Classical" in render_genres(result)


def test_non_music_is_excluded():
    result = build_rewind([{"title": "How to repair a bike", "videoId": "howto-1"}], years=0)
    assert result["songs"] == []


def test_edit_is_dry_run_data_only():
    edit = build_edit("abc123", "[MuseAi] ", " | Rewind")
    assert edit["id"] == "abc123"
    assert edit["snippet"]["title"] == "[MuseAi] abc123 | Rewind"
