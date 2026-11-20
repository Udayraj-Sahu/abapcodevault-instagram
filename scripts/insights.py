"""Nightly Instagram insights for every published reel -> insights/ (run by .github/workflows/insights.yml).

Writes:
  insights/latest.json   all metrics per reel (latest snapshot)
  insights/history.csv   one row per reel per day (to see growth over time)
  insights/REPORT.md     human-readable table + averages, read by the nightly content run
Never prints the token; API errors are reported by metric name only.
"""
import csv, datetime as dt, json, os, sys, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import publish as P   # reuse call() / detect_api() (same token, same host detection)

ERRORS = {}
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
METRICS = ["reach", "views", "likes", "comments", "shares", "saved", "total_interactions",
           "ig_reels_avg_watch_time", "ig_reels_video_view_total_time", "reels_skip_rate", "follows", "profile_visits"]


def safe(fn, *a):
    try:
        return fn(*a), None
    except RuntimeError as e:
        msg = str(e)
        return None, msg[msg.find("failed:"):][:160] if "failed:" in msg else "error"


def media_metrics(mid):
    out, bad = {}, []
    res, err = safe(P.call, "GET", f"{mid}/insights", {"metric": ",".join(METRICS)})
    if res is None:                      # one unsupported metric fails the whole call: ask one by one
        for m in METRICS:
            r, e = safe(P.call, "GET", f"{mid}/insights", {"metric": m})
            if r is None:
                bad.append(m)
                ERRORS.setdefault(m, e)
                continue
            for it in r.get("data", []):
                out[it["name"]] = (it.get("values") or [{}])[0].get("value", it.get("total_value", {}).get("value"))
    else:
        for it in res.get("data", []):
            out[it["name"]] = (it.get("values") or [{}])[0].get("value", it.get("total_value", {}).get("value"))
    f, _ = safe(P.call, "GET", mid, {"fields": "permalink,timestamp,like_count,comments_count,media_product_type"})
    if f:
        out["permalink"] = f.get("permalink")
    return out, bad


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pub = json.load(open(os.path.join(root, "published.json")))
    profile, ig_id = P.detect_api()
    acct, _ = safe(P.call, "GET", ig_id, {"fields": "followers_count,media_count"})
    rows, unsupported = [], set()
    for folder, v in sorted(pub.items()):
        mid = v.get("media_id")
        if not mid or "_reel_" not in folder:
            continue
        m, bad = media_metrics(mid)
        unsupported.update(bad)
        rows.append({"folder": folder, "published_at": v.get("published_at"), **m})
    os.makedirs(os.path.join(root, "insights"), exist_ok=True)
    now = dt.datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
    json.dump({"updated": now, "account": acct or {}, "unsupported_metrics": sorted(unsupported), "errors": ERRORS, "reels": rows},
              open(os.path.join(root, "insights", "latest.json"), "w"), indent=1)
    hist = os.path.join(root, "insights", "history.csv")
    cols = ["date", "folder"] + METRICS
    new = not os.path.exists(hist)
    with open(hist, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({"date": now[:10], **r})

    def g(r, k):
        x = r.get(k)
        return x if isinstance(x, (int, float)) else None
    lines = [f"# Reel insights (updated {now})", "",
             f"Followers: {(acct or {}).get('followers_count', '?')}  ·  reels tracked: {len(rows)}", "",
             "| Reel | Views | Reach | Avg watch (s) | Skip rate | Likes | Shares (sends) | Saves | Follows |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["folder"], reverse=True):
        aw = g(r, "ig_reels_avg_watch_time")
        lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            r["folder"].replace("_reel_", " "), g(r, "views") or "", g(r, "reach") or "",
            f"{aw/1000:.1f}" if aw else "", f"{g(r,'reels_skip_rate'):.0f}%" if g(r, "reels_skip_rate") is not None else "",
            g(r, "likes") or 0, g(r, "shares") or 0, g(r, "saved") or 0, g(r, "follows") or ""))
    def avg(k):
        xs = [g(r, k) for r in rows if g(r, k) is not None]
        return sum(xs) / len(xs) if xs else None
    lines += ["", "## Averages",
              f"- Views per reel: {avg('views') or 0:.0f}",
              f"- Average watch time: {(avg('ig_reels_avg_watch_time') or 0)/1000:.1f} s",
              f"- Shares (sends) per reel: {avg('shares') or 0:.2f} · saves per reel: {avg('saved') or 0:.2f}"]
    if unsupported:
        lines += ["", f"_Metrics the API did not return for some reels: {', '.join(sorted(unsupported))}_"]
    open(os.path.join(root, "insights", "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print(f"insights saved for {len(rows)} reels; unsupported: {sorted(unsupported)}")
    for m, e in list(ERRORS.items())[:3]:
        print(f"  {m}: {e}")


if __name__ == "__main__":
    main()
