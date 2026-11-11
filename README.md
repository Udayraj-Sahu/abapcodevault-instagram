# @abapcodevault — automatic Instagram posting

Every day a GitHub Action posts whatever is due, at 3 fixed times (IST):

| Time (IST) | Post |
| --- | --- |
| 9:00 AM | Single post (cheat sheet) |
| 1:00 PM | Carousel (concept or interview question) |
| 7:30 PM | Reel with voiceover and captions |

Claude generates tomorrow's 3 posts every afternoon and adds them to `queue/`.

`published.json` records every post that went live, so nothing is posted twice.

## One-time setup (about 30 minutes)

### 1. Make your Instagram a professional account
Instagram app → Settings → **Account type and tools** → **Switch to professional account** → choose **Creator** (or Business).

### 2. Create a Meta app and get a token (Unified login)
1. <https://developers.facebook.com> → **My Apps → Create app** → use case **Manage messaging & content on Instagram**.
2. **Customize → API setup with Unified login** → connect a **Business portfolio** (create a free one if needed).
3. **1. Configure your app → Create new configuration**: token type **System-user access token**, expiration **Never**, asset **your Instagram account**, permissions must include **instagram_basic** and **instagram_content_publish**. The redirect URL can stay empty.
4. **2. Generate access tokens** → generate the system-user token for the configuration and copy it.
5. Note the **Instagram account ID** (a long number shown with the account in this setup, or in Business settings → Accounts → Instagram accounts).

### 3. Add two secrets to this repo
Repo → **Settings → Secrets and variables → Actions → New repository secret**
- `IG_ACCESS_TOKEN` = the token
- `IG_USER_ID` = the Instagram account ID

A system-user token never expires, so no refresh setup is needed.

### 4. (Only for 60-day Instagram-login tokens) automatic refresh
If you used a 60-day Instagram-login token instead (no `IG_USER_ID`), add a fine-grained GitHub token with **Secrets: Read and write** on this repo as `GH_PAT`; the token workflow then renews it twice a month.

### 5. Test it
1. **Actions → Check and refresh Instagram token → Run workflow.** The log should say `Token OK ... @abapcodevault`.
2. **Actions → Publish to Instagram → Run workflow**, tick **Dry run**. The log lists what would be posted.
3. To post one item right now, run it again with the folder name in **only** (e.g. `2026-11-17_tue_post_sy-subrc-cheatsheet`).

## Day to day
- To skip or change a post: delete or edit its folder in `queue/` before 7 PM on its date.
- To pause everything: **Actions → Publish to Instagram → ⋯ → Disable workflow**.
- If a run fails, GitHub emails you; the log explains why (most often an expired token).
- Media files are served publicly from this repo through the jsDelivr CDN, which is why the repo is public. Never commit tokens: they live only in repo secrets.

## Files
- `queue/` — posts waiting to go out (`post.json`, `caption.txt`, `slide_XX.jpg` or `reel.mp4` + `cover.jpg`)
- `scripts/publish.py` — posts due items via the Instagram API
- `scripts/check_token.py` — verifies and refreshes the token
- `scripts/queue_week.py` — turns a generated week into dated queue folders
- `pipeline/` — the content generator (slides, reels with voiceover) and topic plan
