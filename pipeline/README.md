# @abapcodevault — daily Instagram pipeline

**Since 14 Nov: 4 reels a day** (9:00 course, 13:00 additional concepts / Sunday FAQ, 17:00 course, 19:30 course). Course parts go 09:00 -> 17:00 -> 19:30.

Each daily run creates tomorrow's **3 reels** (reels only since 12 Nov 2026).

## Daily rhythm (3 reels every day, all 7 days of the week)
| Time (IST) | Slot `time` | What | Length |
| --- | --- | --- | --- |
| 9:00 AM | `"09:00"` | **Course reel**: next part of the ABAP course (`pipeline/syllabus.json`, in order) | 30-60 s, max 90 s |
| 1:00 PM | `"13:00"` | **Free topic** reel from topics.json (tips, bugs, interview, performance...). Even day-of-month: ABAP Code Vault plug in caption; odd: interview angle + ABAP Interview Pack plug | 30-60 s, max 90 s |
| 5:00 PM | `"17:00"` | **Course reel** (since 14 Nov): the part after the 9 AM one | 30-60 s, max 90 s |
| 7:30 PM | `"19:30"` | **Course reel**: the part after the 9 AM one | 30-60 s, max 90 s |
**Pacing rule (every reel, approved 12 Nov):** the screen must visibly change at least every 3 seconds (new element, highlight, outline, typing, word emphasis, punch-in or cut); keep pauses short. Default pace "snappy" does the audio side and adds punch-ins on highlighted words / every ~2.6 s (not on code, screen, compare, table, bug slides); reels over 20 s get an automatic mid-reel re-hook stamp (override with `"rehook": {"stamp": "Common mistake", "slide": 2}` or turn off with `"rehook": false`; best: make that slide's voiceover start with the same words). The generator warns "STATIC: ..." if the picture is still for more than 3 s — fix it; plan 1 visual beat per 2-3 s when writing slides (e.g. more fields revealed one by one, focus outlines, step lists).
**Live style (default since 12 Nov, user approved, inspired by a reference reel):** segmented progress bar (one
segment per scene); a section chip at top-left per scene (HOOK, INSIDE SE11, CODE, HOW IT WORKS, REMEMBER, COMMON MISTAKE,
NEXT ... — derived from the slide kind/label, override with slide "section"); a mood colour per section (red = hook/mistake,
blue = SE11/code, green = rule/next, orange = tip/quiz; override with slide "mood": red|green|orange|blue) on the chip, its
segment and a soft breathing glow behind the content; an animated heart "+1" and Follow -> Following on the end card; and a
soft generated lo-fi music bed ducked under the voice. Turn off per reel with "style": "classic" or "no_music": true.
**Length rule (every reel, user 14 Nov):** explain the ONE idea well, but keep it watchable to the end: aim for 30-60 s, never over 90 s (the generator warns above 90 s and never speeds up the voice). If an idea needs more, split it into the next part. Never pad, never rush.
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
- **Plan a lesson before starting it:** list every bullet point and split them into parts so that each part teaches ONE
  idea (no time limit since 14 Nov; follow the deep-dive topic map). Write the remaining parts into `pending_parts` with a `title` and a precise `focus`.
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
  "Next: <next part/lesson>" and "Follow the series so you don't miss it." Hashtags as usual (5, topic tag e.g. #ddic).
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
8. **Two improvements per run** (one visual: animation/cuts/typography; one audio/words: voice/script/sound-timing — rotating via `state.json` improve_next) following `pipeline/IMPROVEMENTS.md`: research a technique on the web, implement, test, keep or revert on its own, log. Never let an improvement block or break the day's reels: if in doubt, revert it.

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

## Hashtags (fixed: exactly 5 per post, since 14 Nov)
Instagram caps hashtags at 5 per post/reel (since Dec 2025); tags past the fifth do not count. Always:
`#sap #abap #sapabap` + 1 topic tag (e.g. #ddic #alv #performance #sapinterview #cds) + `#abapcodevault` last.

## Instagram skill checks (since 14 Nov; tools in tools/ig, MIT, from Jakeschincariol/instagram-agent-skill)
Run these on every reel before rendering; fix every FAIL, decide every WARN:
1. **Hook:** write 3 hook options (different formulas from `tools/ig/ig-reel/hooks.json`), score them with
   `python3 tools/ig/ig-reel/hookscore.py hooks.txt`, use the top one (aim 50+). The hook sentence is the FIRST spoken
   sentence, 8 words or fewer; the recap line ("Last time we learned X. Now, Y.") follows it.
2. **Beats:** put the voiceover sentences one per line and run `python3 tools/ig/ig-reel/beats.py script.txt --target <s>`;
   fix any beat over 4 s (split the line or add a reveal on screen). Ignore its "under target" advice (no length limit).
3. **Humanize:** `python3 tools/ig/ig-human/humanize.py script.txt --report` then `detect.py`; rewrite flagged lines by hand
   (keep SAP terms, never say "ABAP"); aim for PASS.
4. **Caption:** Job A (the reel carries the hook): line 1 = the hook (lands whole within 125 chars), the 2 search phrases a
   learner would type (e.g. "SAP domain", "data element") as plain words in the first 2-3 lines, exactly ONE ask
   (e.g. "Comment <comment_word> if ..." or "Save this for your next SE11 task"), no URL, 5 hashtags.
   Run `python3 tools/ig/ig-caption/caption.py caption.txt --keywords "<phrase 1>,<phrase 2>"` and fix every FAIL.

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

## Motion graphics (approved 12 Nov, live from the 13 Nov reels)
**No empty scene (user rule, 13 Nov):** the first content block of a scene (e.g. flow step 1) must be on screen within 0.9 s of the cut, even if its sync word is spoken later; the engine enforces this (`FIRST_CONTENT_MAX` in generate.py). Never weaken it.
Automatic per scene kind, no per-reel work: `screen` = cursor click + typed value in each `focus` field;
`flow` = side rail with a running packet; stamps = short landing shake. Do not add drifting background
symbols (rejected). New effects or variations can come in through the daily visual improvement.

## Reference-reel motion set A-E (approved 12 Nov, live from the 13 Nov reels)
- A: transitions are "soft" by default (old scene shrinks + fades, mood colour shifts, new scene builds on an empty page);
  the section chip switches to the next label ~0.2 s before the cut.
- B: SE11 panels and flow steps "grow" in with a white outline flash; flow steps appear when their first word is spoken
  (automatic). Any block can take `say` to sync to a spoken word.
- C: flow / versus headings build word by word.
- D: slide kind `versus` for wrong-vs-right: `{"kind":"versus","label":"REMEMBER","heading":"...",
  "bad":{"title":"...","sub":"...","say":"<spoken word>"},"good":{"title":"...","sub":"...","say":"<spoken word>"}}`
  -> red card, VS, green card on its word, strike-through + ✗/✓ badges. Use it in course reels where a mistake/fix fits.
- E: every reel sets `"comment_word"` (one short keyword, e.g. "DDIC"): the end card types it into a comment box.
  Do NOT promise anything for commenting in the caption or voice.

## Story rules (approved 12 Nov, live from the 13 Nov reels)
1. **Hook first.** The cover opens on the problem the lesson solves, never a definition
   ("Your program can't see your *new field*?", not "What is the Data Dictionary?"). The syllabus order and the
   lesson content stay the same; the kicker still names it ("ABAP course · DDIC · Lesson 1").
2. **Story arc:** problem -> mistake -> fix -> payoff. Use `versus` for the mistake/fix wherever it fits.
   End on an **open loop** for the next reel via `"next": {..., "vo": "Part 2, tomorrow at 9 AM: how SAP blocks
   wrong values before your code even runs."}` instead of a plain "Next: ...".
3. **Real SAP moments:**
   - `{"kind":"sap_error","label":"THE PROBLEM","heading":"...","tcode":"SE38","title":"ZPROG","code":["..."],
     "bad_line":0,"message":"Field \"ZZ_X\" is unknown.","say":"<spoken word when the error lands>"}`
     -> window grows, code types in, red status-bar error slides in with an error buzz + shake, red squiggle.
   - `{"kind":"output","label":"RESULT","heading":"...","tcode":"ALV","title":"...","columns":[...],"rows":[[...]],
     "highlight":<row>,"verdict":{"text":"5 LINES","good":true}}` -> report output fills row by row + verdict stamp.
     Two output slides (wrong -> fixed) make a before/after.
4. **Signature sounds (4b, automatic):** the same soft two-note pluck on every cut, and a thud + bell on every
   "Remember" stamp. Do not add whooshes.
5. **Rewatch:** about one course reel a day ends on a quiz whose answer is IN the reel:
   `"next": {"title":..., "when":..., "quiz": {"question":"Quiz: what does *Ctrl+F3* do?","options":["Save","Activate","Check"]},
   "vo":"Quiz: what does Control F3 do? The answer is in this reel. Comment it."}` (no comment box on quiz cards).
   Every reel fades back to its empty opening page in the last 0.35 s, so the loop is seamless (automatic).
6. Numbers in the voiceover are written as words ("one two three four"), digits stay in `spoken` (subtitles).

## Deep-dive topic map (user rule, 13 Nov — overrides any shorter lesson plan)
Every course topic (domain, data element, table, view, ...) is taught COMPLETELY, so the viewer never stays confused and
knows every little detail at the end. Before the first reel of a topic, plan it through these 10 questions, in order;
each question gets one or more reels (one idea per reel), as many parts as needed:
1. What is it? (one plain sentence)  2. Why do we need it? (the problem without it)  3. Where is it used? (how it connects)
4. How do you open / create it? (every click)  5. What's inside? (every tab and every field, with a real example value)
6. Special features, and why each exists  7. Key points / rules  8. Common mistakes  9. Interview questions  10. Recap + quiz.
Store the plan in `state.json` -> `course.pending_parts` (title + precise focus per part). The free PDF notes follow the same map.
Example (Domain, 11 parts): what + why · where used (domain -> data element -> table field, Where-Used List) · create step
by step · Definition tab Format block · Output Characteristics · Single values · Intervals · Value table (why) · key points ·
mistakes + interview · recap quiz.

## Teaching rules (approved 13 Nov, live from the 14 Nov reels; inspired by the teaching method of the "SAP ABAP by Rahul Mehta" YouTube channel. Copy the method, never his words, slides or examples)
Goal: every reel explains its one idea so clearly that a fresher understands it on the first watch. These rules sit on top of
the Story rules; one idea per reel, explained fully at a calm pace (no time limit since 14 Nov); never talk faster to fit.
1. **One idea per reel.** A course part teaches ONE concept (one tab, one field group, one statement). If a part has more,
   split it and update `pending_parts`. At most 3-4 fields/terms explained per reel; voiceover ≈ 2.3-2.5 words per second.
2. **Recap first (course reels, from the second part/lesson on).** After the hook, one line in exactly this pattern
   (user rule, 13 Nov): "Last time we learned <last topic>. Now, <this topic>." e.g. "Last time we learned the Definition tab.
   Now, the values it allows." Never the short "Last time: <topic>." form.
3. **Why before how.** Say what problem the thing solves before showing fields or code ("Without a domain, every field
   repeats its own type and length. Change one, miss ten.").
4. **Define every new term the first time it appears**, in one plain sentence ("A check table is the table SAP checks your
   value against."). Track defined terms in `state.json` -> `course.terms` (append new ones); don't redefine them later,
   just use them.
5. **Show every click.** When a reel shows SAP, show the path in order: T-code -> what you type -> which button/tab -> the
   field. Use `screen` with `focus` / cursor, or a `flow` of the steps. Never jump from "open SE11" to a finished object.
6. **Simple analogy only when it is accurate** (e.g. domain = the template, data element = the label + meaning on top of it).
7. **One-sentence takeaway** on the REMEMBER slide: the single line the viewer should keep.
8. **Beginner-clean course.** Course reels (9 AM / 7:30 PM) never go into advanced, cross-topic detail; if it comes up,
   say it in one line and leave it for a 1 PM reel ("We'll do performance in a separate reel.").

## 1 PM slot = "Additional concepts" + Sunday FAQ (approved 13 Nov)
- **Monday-Saturday 1 PM:** advanced / cross-topic reels that need knowledge from several areas (performance, FOR ALL ENTRIES,
  SELECT in LOOP, debugging, interview traps, 7.40+ syntax), taken from topics.json as before. Prefer topics whose basics the
  course has already covered. Kicker like "Additional concepts".
- **Sunday 1 PM: FAQ reel** (`"format": "faq"`, tag "FAQ"). Answer ONE common learner question from topics.json `faq`
  (first one not in `state.json` -> `faq_done`; append it after queueing). Hook = the question itself. Answer in 3-4 clear
  steps. Facts that change over time (trial systems, certification, versions) MUST be checked with WebSearch on the day and
  stated without invented numbers. When the list runs out, write new common questions.

## Free PDF notes per lesson (approved 13 Nov)
- When the run queues the LAST part of a course lesson, also create `notes/<S.L>-<slug>.pdf` (A4, 1-3 pages) with PIL
  (render pages as images with the reel fonts and notebook look, save as one multi-page PDF; `pip install reportlab` is also fine).
- Contents: lesson title, why it matters, every tab/field/statement covered with its meaning, the code example, the common
  mistake, 2-3 interview questions with short answers, terms defined in the lesson, and a footer
  "More snippets & cheat sheets: ABAP Code Vault (link in bio) · @abapcodevault". Same accuracy rules as the reels.
- Commit it to `notes/`, send it to the user with SendUserFile and mention it in the summary message (the user uploads it).
- Only while `state.json` -> `notes_link_live` is true, the caption of that last part adds "Free notes for this lesson: link in bio."
  The user switches that flag on once the notes link is live. A failed PDF never blocks the reels.

## Posting reliability (13 Nov)
Layers, any one of which is enough: (1) **keeper.yml**, a self-restarting GitHub Actions loop that dispatches
publish.yml 3 min before 09:00 / 13:00 / 19:30 IST and re-dispatches anything overdue (restarted by its own
2-hourly cron if the chain ever breaks); (2) Claude scheduled publish tasks at 8:48 / 12:48 / 19:18;
(3) Claude backup checks at 9:05 / 13:05 / 19:35; (4) publish.yml's own crons. publish.yml waits for the slot
when started up to 20 min early (wait_slot.py) and posts at once when catching up. published.json + the
concurrency group prevent double posts.
