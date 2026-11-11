#!/usr/bin/env python3
"""Verify the Instagram token works and show the account it posts to.
With REFRESH=1, also refresh the long-lived token and print the new one to the
file new_token.txt (used by the refresh workflow; never printed to the log)."""
import json
import os
import urllib.parse
import urllib.request

tok = os.environ["IG_ACCESS_TOKEN"]
q = urllib.parse.urlencode({"fields": "user_id,username,account_type", "access_token": tok})
with urllib.request.urlopen(f"https://graph.instagram.com/v26.0/me?{q}", timeout=60) as r:
    me = json.loads(r.read().decode())
print(f"Token OK: @{me.get('username')} ({me.get('account_type')}) id={me.get('user_id')}")

if os.environ.get("REFRESH") == "1":
    q = urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": tok})
    with urllib.request.urlopen(f"https://graph.instagram.com/refresh_access_token?{q}", timeout=60) as r:
        res = json.loads(r.read().decode())
    with open("new_token.txt", "w") as fh:
        fh.write(res["access_token"])
    days = int(res.get("expires_in", 0)) // 86400
    print(f"Token refreshed; valid for about {days} more days.")
