# @abapcodevault — daily Instagram pipeline

Each daily run creates tomorrow's **3 reels** (reels only since 12 Nov 2026).

## Daily rhythm (3 reels every day)
| Time (IST) | Slot `time` | Purpose |
| --- | --- | --- |
| 9:00 AM | `"09:00"` | Quick win: cheat-sheet style tip, T-code, syntax trick (fast formats) |
| 1:00 PM | `"13:00"` | Teach: concept / live coding / before-after. Even day-of-month: end with ABAP Code Vault plug in the caption. Odd day-of-month: interview angle + ABAP Interview Pack plug |
| 7:30 PM | `"19:30"` | Story / bug hunt / interview chat / quiz (highest-effort reel of the day) |
All three are 1080×1920 MP4 reels, 12-18 s, Hinglish voiceover (voice hm_psi). Every post in a day file is
`"type": "reel"` with a `"time"` field; `scripts/queue_day.py` reads it. The three reels of a day must use
three DIFFERENT formats and three different topics. Old day files with post/carousel still render.

## Steps for a daily run (makes TOMORROW's reels)
1. DATE = tomorrow (Asia/Kolkata). Read `pipeline/state.json`, `pipeline/topics.json`, `published.json` and list `queue/`.
2. For each slot 09:00 / 13:00 / 19:30: if `queue/` already has an UNPUBLISHED folder starting with `DATE_HHMM_` (not a key in published.json), skip that slot. Otherwise pick the next unused topic (see topics.json how_to_use).
3. Write `pipeline/days/DATE.json` with only the needed reels (each with `"time"`, `"format"`, `"slug"`, `"tag"`, slides, caption, hashtags).
4. `python3 pipeline/generate.py pipeline/days/DATE.json out/DATE`
5. Check 8 frames per reel (ffmpeg) + ffprobe (video+audio, 12-18 s). If the generator printed **OVERLAP WARNING** or wrote LENGTH_WARNING.txt, shorten/restructure and re-render until gone.
6. `python3 scripts/queue_day.py out/DATE DATE`
7. Update `state.json`: `last_queued_date` = DATE, append the topics to `history`, append formats to `recent_formats.reel`. Commit and push.
8. **Improve the reels in ALL six areas** (animation, voice, cuts, translation, typography, sound/timing) following `pipeline/IMPROVEMENTS.md`: per area research a technique on the web, implement, test, keep or revert on its own, log. Never let an improvement block or break the day's reels: if in doubt, revert it.

## Design (fixed)
- Light "notebook" theme: cream ruled paper, ink text, one brand colour **SAP blue**, yellow highlighter, handwritten (Caveat) notes. All built into generate.py; do not change colours per post.
- Wrap 1-3 key words of every title/heading in `*asterisks*` to get the yellow highlighter, e.g. `"A full *ALV report* in 10 lines"`. Use it on every cover title, heading and CTA title; never on more than half the words.
- Cover `kicker` is a short handwritten note (2-5 words), e.g. "No field catalog needed".
- Slide kinds: cover, text, code, compare, list, cta. Slide text English, short. Max ~12 code lines per panel, ~45 characters per code line.
- **Notebook grid (fixed, built into generate.py):** ruled lines every 64 px and every text baseline sits ON a ruled line.
  Body text = 1 line pitch (64 px); headings = 58 px on 1 pitch or 108 px on 2 pitches; header/footer sit on rules;
  code boxes and highlight boxes start/end between rules; content is centred in whole-line steps.
  Never add layout code that places text at arbitrary y: use `snap_base()`, `grid_box()`, `heading_img()`, `text_img()`.
  If text looks "off the lines" or spacing is uneven in a render, that is a bug to fix, not to ship.
- List items ("Label - description") render one per ruled line with descriptions in one aligned column; keep labels short.
- The generator warns (OVERLAP WARNING) if text collides OR content runs into the footer/captions; shorten until it is gone.

## Captions (fixed)
- **Professional English**, LinkedIn-like tone. No Hinglish in captions.
- Structure: hook question or bold statement on line 1 -> blank line -> 2-4 short lines or a numbered list with the substance -> blank line -> one engagement line (question or "Save this for ...") -> product line when the post plugs a product ("... ABAP Code Vault (link in bio)" / "ABAP Interview Pack (160 Q&A): link in bio").
- 60-120 words. At most 1 emoji, or none. No invented statistics.

## Hashtags (fixed: 9-10 per post)
Always these 7: `#sap #abap #coding #sapabap #abapdeveloper #saps4hana #sapfresher`
+ 1-2 topic tags (e.g. #alv #performance #sapinterview #cleancode #tcodes #bapi #smartforms #cds)
+ always `#abapcodevault` last.

## Formats & recipes (variety engine)
Every post gets a **format**. Never reuse a format that appears in the last 5 entries of `state.json -> recent_formats[<type>]`
(for covers: last 3). Pick the format that fits the topic best among the allowed ones, then append it to that list.
Set `"format": "<name>"` on every post (reels use it for pace + transitions automatically).

### Reel formats (12-18 seconds, 3-4 frames)
Every reel must be **12-18 s**. Write ~30-45 words of voiceover in total (about 8-14 words per frame).
The generator speeds the voice up to 15% if slightly long, holds the last frame if short, and writes
LENGTH_WARNING.txt if still too long: then shorten the script and re-render.
| Format | Pace | Frame plan (kinds) |
| --- | --- | --- |
| `bug_hunt` | fast | cover style=bug → bug (circle + note) → code typewriter (fix) → [cta] |
| `before_after` | fast | cover style=question → compare (slow/fast) → fact ("*X* became *Y*") |
| `quiz` | fast | quiz (question + 3 options, countdown, reveal) → answer → [cta] |
| `three_things` | fast | cover style=number ("3 …") → number 1 → number 2 → number 3 |
| `myth_fact` | fast | myth → answer or code (proof) → [cta] |
| `live_coding` | calm | cover → code typewriter (≤ 6 lines, spotlight the key line) → answer (recap) |
| `interview_chat` | calm | chat (question + answer) → answer (key point) → [cta] |
| `story` | calm | story (time, place, 2 short lines) → bug or code → answer (lesson) |
Every reel automatically ends with the follow card ("Follow for more *ABAP tricks*" + "Follow @abapcodevault", voice: "ऐसी और ABAP tricks के लिए, follow करो।"),
unless its last slide is already a CTA that mentions follow. Budget ~2 s for it: keep your own frames to ~10-15 s.
[cta] = optional 2-second end card with a 4-6 word voice line. Pace comes from the format; never set voice_speed.

### Carousel formats (6-7 slides) — legacy, not used since reels-only
| Format | Slide plan |
| --- | --- |
| `step_by_step` | cover → code/text steps → cta (Code Vault plug) |
| `mistake_fix` | cover style=bug → bug → compare → checklist → cta |
| `myth_fact` | cover style=question → myth ×2-3 → tip → cta |
| `quiz` | cover style=question → quiz (reveal:false, countdown:false) → answer → quiz → answer → cta |
| `cheat_table` | cover style=number → table → table → fact → cta |
| `flowchart` | cover → flow → text/code per step → cta |
| `bug_story` | cover → story → bug → code fix → answer (lesson) → cta |
| `interview_qa` | cover style=question → chat → answer → chat → answer → cta (Interview Pack plug) |
Even day-of-month: a teaching format (step_by_step, mistake_fix, myth_fact, cheat_table, flowchart, bug_story) + Code Vault plug.
Odd day-of-month: an interview format (quiz, interview_qa, myth_fact) + Interview Pack plug.
Rotate cover styles too: default, number, question, checklist, bug.

### Single post formats (1 slide) — legacy, not used since reels-only
`list` (cheat sheet) · `table` · `tip` (quote card) · `fact` ("Did you know?") · `code` (snippet card) · `choice` (this or that) · `flow` · `checklist`

### Slide kinds reference (JSON)
- cover: `{"kind":"cover","kicker":"...","title":"... *key* ...","subtitle":"..."}`; styles:
  `"style":"number","number":"7"` · `"style":"question"` · `"style":"checklist","items":[...]` · `"style":"bug","code":"...","bug_line":1`
- quiz: `{"kind":"quiz","question":"...","options":["A","B","C"],"answer":2,"countdown":true,"reveal":true}`
- answer: `{"kind":"answer","label":"ANSWER","heading":"*HASHED* table","body":"...","highlight":"..."}`
- chat: `{"kind":"chat","heading":"...","messages":[{"from":"Interviewer","text":"..."},{"from":"You","text":"..."}]}`
- myth: `{"kind":"myth","myth":"...","fact":"...","detail":"..."}`
- number: `{"kind":"number","number":"1","title":"...","body":"...","code":"optional"}`
- story: `{"kind":"story","time":"2:07 AM","place":"Production","heading":"...","lines":["...","..."],"lesson":"..."}`
- bug: `{"kind":"bug","heading":"...","code":"...","bug_line":1,"note":"short handwritten note","typewriter":false}`
- table: `{"kind":"table","heading":"...","columns":["A","B","C"],"rows":[["...","...","..."]]}` (max 8 rows)
- flow: `{"kind":"flow","heading":"...","steps":["...","..."]}` (max 5 steps)
- tip: `{"kind":"tip","kicker":"...","quote":"... *key* ...","by":"..."}`
- fact: `{"kind":"fact","title":"Did you know?","text":"... *key* ...","detail":"..."}`
- choice: `{"kind":"choice","question":"...","a":{"label":"...","sub":"..."},"b":{...},"answer":"b","explain":"..."}`
- checklist: `{"kind":"checklist","heading":"...","items":["Title - detail", ...]}`
- code (extras): `"typewriter": true` (character typing + cursor, ≤ 8 lines), `"spotlight": 2` (dim other lines)
- existing: text, code, compare, list, cta

## Reel voiceover (Hinglish, every reel)
- **Read `pipeline/HINGLISH.md` first** (style, caption spellings, glossary, natural vs stiff phrases); it improves over time.
- Post sets `"voice": "hm_psi", "voice_lang": "hi"` and a `"format"`.
- Every reel slide has `"voiceover"` written the way an Indian developer actually talks (Hinglish):
  **Hindi words in Devanagari, English and technical words in Latin script**, exactly as people say them.
  Example: `"Loop के अंदर SELECT SINGLE. हर row के लिए एक database call."`
  The engine speaks Devanagari with Hindi pronunciation and Latin words with English pronunciation, in the same voice.
- Never transliterate English terms into Devanagari (no सेलेक्ट) and never write Hindi words in Latin inside "voiceover".
- Acronyms and T-codes are pronounced via the SAY table in generate.py (SAP, ALV, BAPI, SE38, ST22, VBAK, F8 ...).
  Add new ones there if needed. Do not put code lines or symbols like @, =, -> in the voiceover; describe them in words.
- Every reel slide also gets `"spoken"`: the same line fully in Roman Hinglish (for on-screen captions).
  Do NOT use the key `subtitle` for this (on a cover slide `subtitle` is the visible sub-heading).
- Sound like a person talking to a friend: short sentences, a hook in the first 2 seconds ("Is code mein bug hai.",
  "Aapki report slow hai?"), natural phrases ("dekho", "bas", "save kar lo").
- Check: voiceover_script.txt in the reel folder, and the reel duration (12-18 s) with ffprobe.
- The engine animates automatically: blocks slide/pop in, code types in across the narration, camera push, scene transitions, progress bar, soft pop/stamp/tick SFX (no whoosh on cuts), loudness normalised.
- Setup before rendering: `pip install --break-system-packages kokoro-onnx soundfile`, then download into a `tts` folder next to generate.py (or set ABAP_TTS_DIR):
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
- Check the MP4 has an audio stream (ffprobe) before delivering.
