"""Small standard-library YouTube Data API client for optional channel tooling."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional

BASE_URL = "https://www.googleapis.com/youtube/v3/"


class YouTubeAPIError(RuntimeError):
    pass


class YouTubeClient:
    def __init__(self, api_key: Optional[str] = None, oauth_token: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.oauth_token = oauth_token or os.getenv("YOUTUBE_OAUTH_TOKEN")

    def _request(self, method: str, resource: str, params: Dict[str, Any], body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = dict(params)
        if self.api_key:
            query["key"] = self.api_key
        url = BASE_URL + resource + "?" + urllib.parse.urlencode(query, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
        if self.oauth_token:
            request.add_header("Authorization", f"Bearer {self.oauth_token}")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise YouTubeAPIError(f"YouTube API request failed: {exc}") from exc

    def channel(self, channel_id: str) -> Dict[str, Any]:
        if not self.api_key:
            raise YouTubeAPIError("YOUTUBE_API_KEY is required for channel scans")
        data = self._request("GET", "channels", {"part": "snippet,statistics,contentDetails", "id": channel_id})
        if not data.get("items"):
            raise YouTubeAPIError(f"Channel not found: {channel_id}")
        return data["items"][0]

    def uploads(self, playlist_id: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        token = None
        while True:
            params = {"part": "snippet,contentDetails", "playlistId": playlist_id, "maxResults": 50}
            if token:
                params["pageToken"] = token
            data = self._request("GET", "playlistItems", params)
            items.extend(data.get("items", []))
            token = data.get("nextPageToken")
            if not token:
                return items

    def videos(self, video_ids: Iterable[str]) -> List[Dict[str, Any]]:
        ids = list(video_ids)
        result = []
        for start in range(0, len(ids), 50):
            result.extend(self._request("GET", "videos", {"part": "snippet,statistics,contentDetails", "id": ",".join(ids[start:start + 50])}).get("items", []))
        return result

    def update_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        if not self.oauth_token:
            raise YouTubeAPIError("YOUTUBE_OAUTH_TOKEN is required for edits")
        return self._request("PUT", "videos", {"part": "snippet,status", "id": video["id"]}, video)
