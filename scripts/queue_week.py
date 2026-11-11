#!/usr/bin/env python3
"""Copy one generated week (output of generate.py) into queue/ with publish dates.

Usage: python3 scripts/queue_week.py OUT_WEEK_DIR MONDAY_DATE
  e.g. python3 scripts/queue_week.py ../out/week02 2026-11-23

Day names in the generated folder names (Mon/Tue/Wed/Thu/Fri/Sat/Sun) decide the date.
PNG slides become JPEG (Instagram's API only accepts JPEG images).
"""
import datetime as dt
import glob
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def main(week_dir, monday):
    start = dt.date.fromisoformat(monday)
    if start.weekday() != 0:
        sys.exit(f"{monday} is not a Monday")
    for src in sorted(glob.glob(os.path.join(week_dir, "*"))):
        if not os.path.isdir(src):
            continue
        m = re.match(r"\d+_(\w{3})_(carousel|post|reel)_(.+)$", os.path.basename(src))
        if not m:
            continue
        day, kind, slug = m.group(1).lower(), m.group(2), m.group(3)
        date = start + dt.timedelta(days=DAYS[day])
        dst = os.path.join(ROOT, "queue", f"{date.isoformat()}_{day}_{kind}_{slug}")
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
        json.dump({"type": kind, "publish_date": date.isoformat()},
                  open(os.path.join(dst, "post.json"), "w"), indent=2)
        print("queued", os.path.basename(dst))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
