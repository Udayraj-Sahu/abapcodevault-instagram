#!/usr/bin/env python3
"""Publish due posts from queue/ to Instagram (Instagram API with Instagram Login).

Each folder in queue/ holds:
  post.json    {"type": "carousel" | "post" | "reel", "publish_date": "YYYY-MM-DD",
                "publish_time": "HH:MM" (IST, optional; default by type: post 09:00,
                carousel 13:00, reel 19:30)}
  caption.txt
  slide_01.jpg ...   (carousel/post)   or   reel.mp4 (+ optional cover.jpg)

Env:
  IG_ACCESS_TOKEN   access token (secret). Either a system-user token from Meta's
                    "Unified login" setup (never expires; needs IG_USER_ID) or an
                    Instagram-login user token (60 days; IG_USER_ID not needed)
  IG_USER_ID        Instagram account ID (set it when using a system-user token)
  MEDIA_BASE_URL    public base URL for this repo's files at the current commit
  MEDIA_FALLBACK_URLS  optional, space-separated extra base URLs tried when Instagram
                    cannot fetch the media from MEDIA_BASE_URL (e.g. raw.githubusercontent)
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
DEFAULT_TIME = {"post": "09:00", "carousel": "13:00", "reel": "19:30"}


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


def media_bases():
    bases = [os.environ["MEDIA_BASE_URL"]] + os.environ.get("MEDIA_FALLBACK_URLS", "").split()
    return [b.rstrip("/") for b in bases if b.strip()]


def url_for(folder, name, base=None):
    base = (base or media_bases()[0]).rstrip("/")
    rel = os.path.relpath(os.path.join(folder, name), ROOT).replace(os.sep, "/")
    return f"{base}/{urllib.parse.quote(rel)}"


def check_url(folder, name, base, tries=4):
    """Download the file from the public URL (this also warms the CDN cache) and check it
    matches the local file, so Instagram gets a URL that is known to work right now."""
    url = url_for(folder, name, base)
    want = os.path.getsize(os.path.join(folder, name))
    for i in range(tries):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "abapcodevault-publisher"})
            with urllib.request.urlopen(req, timeout=180) as r:
                got = len(r.read())
                ctype = r.headers.get("Content-Type")
            print(f"  media check {url}: {got} bytes, {ctype}, {time.time() - t0:.1f}s")
            if got == want:
                return True
            print(f"  size mismatch (local {want})")
        except Exception as e:
            print(f"  media check {url}: {e}")
        time.sleep(20 * (i + 1))
    return False


def create_reel(folder, ig_id, caption, rounds=3):
    """Create a ready reel container. Instagram fetches the video itself, and a slow or
    failing CDN shows up as "Media upload has failed with error code 2207076/2207077",
    so check the URL first, then retry with backoff and fall back to other hosts."""
    has_cover = os.path.exists(os.path.join(folder, "cover.jpg"))
    errors = []
    for rnd in range(rounds):
        for base in media_bases():
            if not check_url(folder, "reel.mp4", base):
                errors.append(f"{base}: media URL not reachable")
                continue
            if has_cover:
                check_url(folder, "cover.jpg", base, tries=2)
            params = {"media_type": "REELS", "video_url": url_for(folder, "reel.mp4", base),
                      "caption": caption, "share_to_feed": "true"}
            if has_cover:
                params["cover_url"] = url_for(folder, "cover.jpg", base)
            try:
                cid = call("POST", f"{ig_id}/media", params)["id"]
                wait_ready(cid, 900)
                print(f"  container ready via {base}")
                return cid
            except RuntimeError as e:
                errors.append(f"{base}: {e}")
                print(f"  attempt failed via {base}: {e}")
        if rnd < rounds - 1:
            time.sleep(90 * (rnd + 1))
    raise RuntimeError("all media hosts failed: " + " | ".join(errors[-3:]))


def publish(folder, ig_id):
    meta = json.load(open(os.path.join(folder, "post.json"), encoding="utf-8"))
    caption = open(os.path.join(folder, "caption.txt"), encoding="utf-8").read().strip()[:2200]
    kind = meta["type"]
    images = sorted(os.path.basename(p) for p in glob.glob(os.path.join(folder, "slide_*.jpg")))
    if kind == "reel":
        cid = create_reel(folder, ig_id, caption)
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


def recent_captions(ig_id):
    """Captions of the account's latest posts -> media id. A second guard against double
    posts when published.json is out of date."""
    try:
        data = call("GET", f"{ig_id}/media", {"fields": "id,caption", "limit": "25"}).get("data", [])
        return {(m.get("caption") or "").strip(): m["id"] for m in data if m.get("caption")}
    except RuntimeError as e:
        print("could not read recent posts:", e)
        return {}


def main():
    now = dt.datetime.now(IST)
    now_key = now.strftime("%Y-%m-%d %H:%M")
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
        else:
            slot = f'{meta.get("publish_date", "9999-12-31")} {meta.get("publish_time") or DEFAULT_TIME.get(meta.get("type"), "19:00")}'
            if slot <= now_key:
                due.append(f)
    if not due:
        print(f"Nothing due at {now_key} IST.")
        return
    if os.environ.get("DRY_RUN") == "1":
        for f in due:
            print("WOULD PUBLISH:", os.path.basename(f))
        return
    me, ig_id = detect_api()
    print(f"Publishing as @{me.get('username')} ({ig_id})")
    failed = False
    recent = recent_captions(ig_id)
    for f in due:
        name = os.path.basename(f)
        caption = open(os.path.join(f, "caption.txt"), encoding="utf-8").read().strip()[:2200]
        if caption in recent:
            log[name] = {"media_id": recent[caption], "published_at": "already live (found on Instagram)"}
            print("ALREADY LIVE", name, recent[caption])
            json.dump(log, open(LOG, "w"), indent=2)
            continue
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
