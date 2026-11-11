#!/usr/bin/env python3
"""Queue one generated day (output of pipeline/generate.py) for a date.

Usage: python3 scripts/queue_day.py OUT_DAY_DIR YYYY-MM-DD [HH:MM]
Times (IST) by type: post 09:00, carousel 13:00, reel 19:30.
Optional HH:MM puts every post of that day at the same time (e.g. a one-off 21:00 launch).
PNG slides become JPEG (the Instagram API only accepts JPEG images).
"""
import glob
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMES = {"post": "09:00", "carousel": "13:00", "reel": "19:30"}


def main(day_dir, date, at=None):
    for src in sorted(glob.glob(os.path.join(day_dir, "*"))):
        if not os.path.isdir(src):
            continue
        m = re.match(r"\d+_\w*_(carousel|post|reel)_(.+)$", os.path.basename(src))
        if not m:
            continue
        kind, slug = m.group(1), m.group(2)
        when = at or TIMES[kind]
        dst = os.path.join(ROOT, "queue", f"{date}_{when.replace(':', '')}_{kind}_{slug}")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        os.makedirs(dst)
        if kind == "reel":
            shutil.copy(os.path.join(src, "reel.mp4"), os.path.join(dst, "reel.mp4"))
            cover = os.path.join(src, "frame_01.png")
            if os.path.exists(cover):
                Image.open(cover).convert("RGB").save(os.path.join(dst, "cover.jpg"), quality=92)
        else:
            for i, png in enumerate(sorted(glob.glob(os.path.join(src, "slide_*.png"))), 1):
                Image.open(png).convert("RGB").save(os.path.join(dst, f"slide_{i:02d}.jpg"), quality=92)
        shutil.copy(os.path.join(src, "caption.txt"), os.path.join(dst, "caption.txt"))
        json.dump({"type": kind, "publish_date": date, "publish_time": when},
                  open(os.path.join(dst, "post.json"), "w"), indent=2)
        print("queued", os.path.basename(dst))


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
