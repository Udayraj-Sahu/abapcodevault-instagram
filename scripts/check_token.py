#!/usr/bin/env python3
"""Verify the token works and show the Instagram account it posts to.
System-user token (IG_USER_ID set): checks graph.facebook.com; never expires, no refresh.
Instagram-login token: checks graph.instagram.com; with REFRESH=1 also refreshes it and
writes the new token to new_token.txt (never printed to the log)."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

tok = os.environ["IG_ACCESS_TOKEN"]
ig_id = os.environ.get("IG_USER_ID", "").strip()


def get(url, params, fatal=True):
    params["access_token"] = tok
    try:
        with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        msg = f"{e.code} {e.read().decode(errors='replace')}"
        if fatal:
            raise SystemExit(f"Token check FAILED: {msg}")
        print(f"(system-user check failed: {msg}; trying Instagram-login token)")
        return None


me = get(f"https://graph.facebook.com/v26.0/{ig_id}", {"fields": "username,name"}, fatal=False) if ig_id else None
if me:
    print(f"Token OK (system-user token): @{me.get('username')} id={ig_id}. Never expires; no refresh needed.")
else:
    me = get("https://graph.instagram.com/v26.0/me", {"fields": "user_id,username,account_type"})
    print(f"Token OK: @{me.get('username')} ({me.get('account_type')}) id={me.get('user_id')}")
    if os.environ.get("REFRESH") == "1":
        res = get("https://graph.instagram.com/refresh_access_token", {"grant_type": "ig_refresh_token"})
        with open("new_token.txt", "w") as fh:
            fh.write(res["access_token"])
        print(f"Token refreshed; valid for about {int(res.get('expires_in', 0)) // 86400} more days.")
