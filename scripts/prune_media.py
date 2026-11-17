#!/usr/bin/env python3
"""Delete the media files (reel.mp4, cover.jpg, slide_*.jpg) of queue folders that are
already in published.json. Instagram has its own copy once a post is live, and the files
stay in git history. Keeping the repo small keeps the media CDN (jsDelivr serves the whole
repo at a commit) fast and inside its size limits."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log = json.load(open(os.path.join(ROOT, "published.json")))
removed = 0
for name in log:
    folder = os.path.join(ROOT, "queue", name)
    for pat in ("reel.mp4", "cover.jpg", "slide_*.jpg"):
        for f in glob.glob(os.path.join(folder, pat)):
            os.remove(f)
            removed += 1
print(f"pruned {removed} media files from published folders")
