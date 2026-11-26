#!/usr/bin/env python3
"""Write playlist.json from the public YouTube playlist feed."""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

PLAYLIST_ID = "PLG8B4zAouMmc"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?playlist_id={PLAYLIST_ID}"
ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"


def tracks_from_feed(payload):
    root = ET.fromstring(payload)
    tracks = []
    seen = set()
    for entry in root.findall(f"{ATOM}entry"):
        video_id = (entry.findtext(f"{YT}videoId") or "").strip()
        title = (entry.findtext(f"{ATOM}title") or "").strip()
        if not video_id or not title or video_id in seen:
            continue
        seen.add(video_id)
        tracks.append({"id": video_id, "title": title})
    return tracks


def main():
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "playlist.json")
    request = urllib.request.Request(
        FEED_URL,
        headers={"User-Agent": "research-site-playlist"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
    tracks = tracks_from_feed(payload)
    if not tracks:
        sys.exit("playlist feed contained no tracks")
    document = {
        "playlistId": PLAYLIST_ID,
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tracks": tracks,
    }
    destination.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(tracks)} tracks to {destination}")


if __name__ == "__main__":
    main()
