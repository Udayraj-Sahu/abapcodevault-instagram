#!/usr/bin/env python3
"""Publish due posts from queue/ to Instagram (Instagram API with Instagram Login).

Each folder in queue/ holds:
  post.json    {"type": "carousel" | "post" | "reel", "publish_date": "YYYY-MM-DD"}
  caption.txt
  slide_01.jpg ...   (carousel/post)   or   reel.mp4 (+ optional cover.jpg)

Env:
  IG_ACCESS_TOKEN   access token (secret). Either a system-user token from Meta's
                    "Unified login" setup (never expires; needs IG_USER_ID) or an
                    Instagram-login user token (60 days; IG_USER_ID not needed)
  IG_USER_ID        Instagram account ID (set it when using a system-user token)
  MEDIA_BASE_URL    public base URL for this repo's files at the current commit
  DRY_RUN=1         print what would be published, publish nothing
  ONLY=<folder>     publish just this folder (manual run), ignoring its date
"""
import datetime as dt
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()
# System-user tokens work on graph.facebook.com; Instagram-login tokens on graph.instagram.com.
# detect_api() picks whichever host accepts the token.
API = "https://graph.facebook.com/v26.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "queue")
LOG = os.path.join(ROOT, "published.json")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def call(method, path, params=None):
    params = dict(params or {})
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path} failed: {e.code} {body}") from None


def detect_api():
    """Return (profile, ig_id) and set API to the host that accepts this token."""
    global API
    errors = []
    if IG_USER_ID:
        API = "https://graph.facebook.com/v26.0"
        try:
            return call("GET", IG_USER_ID, {"fields": "username"}), IG_USER_ID
        except RuntimeError as e:
            errors.append(str(e))
    API = "https://graph.instagram.com/v26.0"
    try:
        me = call("GET", "me", {"fields": "user_id,username"})
        return me, (me.get("user_id") or me.get("id"))
    except RuntimeError as e:
        errors.append(str(e))
    raise RuntimeError("Token not accepted by either Instagram API host:\n" + "\n".join(errors))


def wait_ready(container_id, limit_s=600):
    t0 = time.time()
    while True:
        st = call("GET", container_id, {"fields": "status_code,status"})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {container_id} {code}: {st.get('status')}")
        if time.time() - t0 > limit_s:
            raise RuntimeError(f"container {container_id} not ready after {limit_s}s ({code})")
        time.sleep(10)


def url_for(folder, name):
    base = os.environ["MEDIA_BASE_URL"].rstrip("/")
    rel = os.path.relpath(os.path.join(folder, name), ROOT).replace(os.sep, "/")
    return f"{base}/{urllib.parse.quote(rel)}"


def publish(folder, ig_id):
    meta = json.load(open(os.path.join(folder, "post.json"), encoding="utf-8"))
    caption = open(os.path.join(folder, "caption.txt"), encoding="utf-8").read().strip()[:2200]
    kind = meta["type"]
    images = sorted(os.path.basename(p) for p in glob.glob(os.path.join(folder, "slide_*.jpg")))
    if kind == "reel":
        params = {"media_type": "REELS", "video_url": url_for(folder, "reel.mp4"),
                  "caption": caption, "share_to_feed": "true"}
        if os.path.exists(os.path.join(folder, "cover.jpg")):
            params["cover_url"] = url_for(folder, "cover.jpg")
        cid = call("POST", f"{ig_id}/media", params)["id"]
        wait_ready(cid, 900)
    elif kind == "carousel" and len(images) > 1:
        children = []
        for name in images[:10]:
            c = call("POST", f"{ig_id}/media", {"image_url": url_for(folder, name), "is_carousel_item": "true"})["id"]
            children.append(c)
        for c in children:
            wait_ready(c, 300)
        cid = call("POST", f"{ig_id}/media", {"media_type": "CAROUSEL", "children": ",".join(children),
                                               "caption": caption})["id"]
        wait_ready(cid, 300)
    else:
        cid = call("POST", f"{ig_id}/media", {"image_url": url_for(folder, images[0]), "caption": caption})["id"]
        wait_ready(cid, 300)
    media = call("POST", f"{ig_id}/media_publish", {"creation_id": cid})
    return media["id"]


def main():
    today = dt.datetime.now(IST).date().isoformat()
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    only = os.environ.get("ONLY", "").strip()
    folders = sorted(d for d in glob.glob(os.path.join(QUEUE, "*")) if os.path.isdir(d))
    due = []
    for f in folders:
        name = os.path.basename(f)
        if name in log:
            continue
        meta = json.load(open(os.path.join(f, "post.json"), encoding="utf-8"))
        if only:
            if name == only:
                due.append(f)
        elif meta.get("publish_date", "9999") <= today:
            due.append(f)
    if not due:
        print(f"Nothing due on {today}.")
        return
    if os.environ.get("DRY_RUN") == "1":
        for f in due:
            print("WOULD PUBLISH:", os.path.basename(f))
        return
    me, ig_id = detect_api()
    print(f"Publishing as @{me.get('username')} ({ig_id})")
    failed = False
    for f in due:
        name = os.path.basename(f)
        try:
            mid = publish(f, ig_id)
            log[name] = {"media_id": mid, "published_at": dt.datetime.now(IST).isoformat(timespec="seconds")}
            print("PUBLISHED", name, mid)
        except Exception as e:  # keep going, report at the end
            failed = True
            print("FAILED", name, e, file=sys.stderr)
        json.dump(log, open(LOG, "w"), indent=2)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
