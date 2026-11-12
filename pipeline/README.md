# @abapcodevault — daily Instagram pipeline

Each daily run creates tomorrow's **3 reels** (reels only since 12 Nov 2026).

## Daily rhythm (3 reels every day)
| Time (IST) | Slot `time` | What | Length |
| --- | --- | --- | --- |
| 9:00 AM | `"09:00"` | **Course reel**: next part of the ABAP course (`pipeline/syllabus.json`, in order) | any length, never > 30 s |
| 1:00 PM | `"13:00"` | **Free topic** reel from topics.json (tips, bugs, interview, performance...). Even day-of-month: ABAP Code Vault plug in caption; odd: interview angle + ABAP Interview Pack plug | any length, never > 30 s |
| 7:30 PM | `"19:30"` | **Course reel**: the part after the 9 AM one | any length, never > 30 s |
**Pacing rule (every reel, approved 12 Nov):** the screen must visibly change at least every 3 seconds (new element, highlight, outline, typing, word emphasis, punch-in or cut); keep pauses short. Default pace "snappy" does the audio side and adds punch-ins on highlighted words / every ~2.6 s (not on code, screen, compare, table, bug slides); reels over 20 s get an automatic mid-reel re-hook stamp (override with `"rehook": {"stamp": "Common mistake", "slide": 2}` or turn off with `"rehook": false`; best: make that slide's voiceover start with the same words). The generator warns "STATIC: ..." if the picture is still for more than 3 s — fix it; plan 1 visual beat per 2-3 s when writing slides (e.g. more fields revealed one by one, focus outlines, step lists).
**Length rule (every reel):** as long as the topic needs, never more than 30 s including the end card. If a topic needs
more, split it into parts (Part 1/2, 2/2 ...) in the following slots.
**"Next" rule (every reel):** set `"next": {"title": "The *Value Range* tab", "when": "tomorrow at 9 AM", "voice": "the Value Range tab"}`
= the NEXT reel in the schedule (9 AM -> 1 PM, 1 PM -> 7:30 PM, 7:30 PM -> tomorrow 9 AM). The generator turns it into the end card
("Next: …" + when + follow button; voice "Next: <voice>, <when>. Follow so you don't miss it.") and replaces any own follow CTA.
The caption also gets a line before its last line: "Next: <title> (<when>)."
When the next reel is a part of a multi-part topic, start its title with the part: "Part 2 · The *Value Range* tab" (voice: "part two, the Value Range tab").
All are 1080×1920 MP4 reels with English voiceover (voice am_michael). Every post in a day file is `"type": "reel"` with a
`"time"` field; `scripts/queue_day.py` reads it. Old day files with post/carousel still render.

## Course reels (9 AM + 7:30 PM) — the ABAP course
- Source: `pipeline/syllabus.json` (from the user's syllabus, `pipeline/syllabus.md`). Teach it **in order**:
  section → lesson → every bullet point. Progress lives in `state.json` → `course`:
  `pending_parts` (planned remaining parts of the current lesson — always do these first, in order) and `next`
  (`{"section": S, "lesson": L}` = the next lesson to start). Section 16 (T-codes) is not a course lesson; use it for 1 PM reels.
- **Plan a lesson before starting it:** list every bullet point and split them into parts so that each part fits ONE reel of
  ≤ 30 s (your frames ≈ 24-27 s + the ~3 s end card ≈ 40-50 words of voiceover, 3-4 frames). Short lessons = 1 part;
  big ones = 2-4 parts. Write the remaining parts into `pending_parts` with a `title` and a precise `focus`.
- **Go deep, not just definitions.** Show what is actually inside: the real SE11/SE80/SE37/... screen, its tabs and field
  names (use the `screen` kind), what each important field does, a real code example, a common mistake, and the interview
  angle. Example: a domain is not "a data type" — it is the Definition tab (data type, length, decimals, output length,
  conversion routine like ALPHA, lowercase) and the Value Range tab (fixed values, intervals, value table).
- JSON per course reel: `"series": "course"`, `"syllabus": "3.2"`, `"part": 1`, `"parts": 3` (omit part/parts for single-part
  lessons), `"format": "course_lesson"`, `"tag": "DDIC · Domain 1/3"`, cover `kicker` like "Domains & data elements · Part 1/3".
  Frame plan: cover → screen / code / flow / table (the meat, 1-2 frames) → answer ("REMEMBER" / common mistake).
- The end card is automatic: parts that continue get "Part N is *next*" + "The next part is coming soon. Follow so you don't miss it.";
  the last part gets the normal follow card.
- Caption: start with "Lesson: <title>" or "<topic>, Part n of N", numbered list of what the reel covered, then
  "Next: <next part/lesson>" and "Follow the series so you don't miss it." Hashtags as usual (topic tag e.g. #ddic).
- Accuracy matters: SE11 field names, tab names and transaction codes must be exactly as in the SAP system. No invented facts.
- After queueing: move the done part out of `pending_parts` (append "S.L part n …" to `course.done`), and when a lesson is
  started advance `next` (next lesson, or lesson 1 of the next section).

`screen` kind (simplified SAP GUI screen):
`{"kind":"screen","heading":"Definition *tab*","tcode":"SE11","object":"Domain ZD_ORDER_NO","tabs":["Properties","Definition","Value Range"],"active":1,"fields":[["Data Type","CHAR"],["No. Characters","10"],["Convers. Routine","ALPHA"]],"focus":[2],"note":"runs on every input & output"}`
— up to 7 fields; `tabs` optional; `focus` rows get a red outline; `note` is a handwritten remark under the screen.

## When reels are made (user rule, 12 Nov)
Reels are made only for the NEXT day, by the daily run at about 9 PM the evening before, so the user can still change
them that evening/morning. Never queue reels further ahead. A day file `pipeline/days/<date>.json` may already exist
as a DRAFT (script only, not queued): reuse and improve it, render it, then queue it at the 9 PM run before that date.
If tomorrow's reels are already queued and unpublished, re-render them with the latest generator (same content)
so they get today's improvements.

## Steps for a daily run (makes TOMORROW's reels)
1. DATE = tomorrow (Asia/Kolkata). Read `pipeline/state.json`, `pipeline/topics.json`, `published.json` and list `queue/`.
2. For each slot 09:00 / 13:00 / 19:30: if `queue/` already has an UNPUBLISHED folder starting with `DATE_HHMM_` (not a key in published.json), skip that slot. 09:00 and 19:30: next course parts (see "Course reels"). 13:00: next unused free topic (see topics.json how_to_use).
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
- **Professional English**, LinkedIn-like tone.
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
Every reel automatically ends with the follow card ("Follow for more *ABAP tricks*" + "Follow @abapcodevault", voice: "Follow for more tips and tricks."),
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

## Reel voiceover (English, every reel — since 12 Nov 2026)
- **Read `pipeline/VOICEOVER.md` first** (style, glossary, natural vs stiff phrases); it improves over time.
- Post sets `"voice": "am_michael", "voice_lang": "en"` and a `"format"`. (Old Hinglish day files with "hi" still render.)
- Every reel slide has `"voiceover"` in clear, conversational **English**, the way a senior developer explains to a friend:
  short sentences (5-14 words), contractions ("it's", "don't"), active voice. Example: "A SELECT inside a loop means one
  database call for every row."
- Acronyms and T-codes are pronounced via the SAY table in generate.py (SAP, ALV, BAPI, SE38, ST22, VBAK, F8 ...).
  Add new ones there if needed. Do not put code lines or symbols like @, =, -> in the voiceover; describe them in words.
  Do not say the word "ABAP" in the voiceover (mispronounced); "ABAP" on screen and in captions is fine.
- Every reel slide also gets `"spoken"`: exactly the same text as "voiceover" (used for the on-screen subtitles).
  Do NOT use the key `subtitle` for this (on a cover slide `subtitle` is the visible sub-heading).
- Hook in the first 2 seconds ("This one line can read your entire table.", "Is your report slow?").
- Check: voiceover_script.txt in the reel folder, and the reel duration (12-18 s) with ffprobe.
- The engine animates automatically: blocks slide/pop in, code types in across the narration, camera push, scene transitions, progress bar, soft pop/stamp/tick SFX (no whoosh on cuts), loudness normalised.
- Setup before rendering: `pip install --break-system-packages kokoro-onnx soundfile`, then download into a `tts` folder next to generate.py (or set ABAP_TTS_DIR):
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
- Check the MP4 has an audio stream (ffprobe) before delivering.
