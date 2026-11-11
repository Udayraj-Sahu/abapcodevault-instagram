# @abapcodevault — automatic Instagram posting

Every Sunday, Claude generates next week's 4 posts and adds them to `queue/`.
Every day at **7:00 PM IST**, a GitHub Action posts whatever is due:

| Day | Post |
| --- | --- |
| Mon | Carousel (concept + ABAP Code Vault plug) |
| Tue | Single post (cheat sheet) |
| Thu | Reel with voiceover and captions |
| Sat | Carousel (interview question + Interview Pack plug) |

`published.json` records every post that went live, so nothing is posted twice.

## One-time setup (about 30 minutes)

### 1. Make your Instagram a professional account
Instagram app → Settings → **Account type and tools** → **Switch to professional account** → choose **Creator** (or Business).

### 2. Create a Meta app and get a token
1. Go to <https://developers.facebook.com> → log in → **My Apps** → **Create app**.
2. Use case: **Manage messaging & content on Instagram**. Give it any name, e.g. `abapcodevault-poster`.
3. In the app dashboard open **Instagram → API setup with Instagram login**.
4. Under **Generate access tokens**, click **Add account** and log in with the @abapcodevault Instagram account. Allow the permissions it asks for (it must include **content publishing**).
   - If it says the account needs a role: **App roles → Roles → Add people → Instagram tester**, then in the Instagram app go to Settings → **Website permissions → Apps and websites → Tester invites** and accept.
5. Click **Generate token** next to the account and copy the token. It is valid for 60 days; the token workflow below refreshes it automatically.

The app can stay in **Development mode**: posting to your own account works without Meta app review.

### 3. Add the token to this repo
Repo → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `IG_ACCESS_TOKEN`
- Value: the token from step 2

### 4. (Recommended) Let the token refresh itself
GitHub → your profile → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**
- Repository access: only this repo
- Permissions: **Secrets → Read and write**
- Expiration: the longest allowed

Add it to this repo as a secret named `GH_PAT`. Twice a month the token workflow then renews `IG_ACCESS_TOKEN` before it expires. Without `GH_PAT`, the workflow only checks the token, and you must paste a fresh one every ~55 days.

### 5. Test it
1. **Actions → Check and refresh Instagram token → Run workflow.** The log should say `Token OK: @abapcodevault`.
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
