# @abapcodevault — daily Instagram pipeline

Each daily run creates tomorrow's 3 posts.

## Daily rhythm (3 posts every day)
| Time (IST) | Type | Size | Purpose |
| --- | --- | --- | --- |
| 9:00 AM | post (1 slide) | 1080×1350 | Cheat sheet people save |
| 1:00 PM | carousel (6–7 slides) | 1080×1350 | Even day-of-month: concept, ends with ABAP Code Vault plug. Odd day: interview question, ends with ABAP Interview Pack plug |
| 7:30 PM | reel (5 frames, 30–60 s MP4 with voiceover) | 1080×1920 | Hook + problem + fix |

## Steps for a daily run (makes TOMORROW's posts)
1. DATE = tomorrow (Asia/Kolkata). Read `pipeline/state.json`, `pipeline/topics.json`, `published.json` and list `queue/`.
2. For each type (post, carousel, reel): if `queue/` already has an UNPUBLISHED folder for DATE with that type (folder name starts with DATE and contains `_<type>_`, and it is not a key in published.json), skip that type. Otherwise pick the next unused topic from topics.json (carousel list chosen by day-of-month parity; see topics.json how_to_use).
3. Write `pipeline/days/DATE.json` (same schema as `pipeline/weeks/week01.json`, only the needed posts; set "day" to the weekday short name).
4. `python3 pipeline/generate.py pipeline/days/DATE.json out/DATE`
5. Contact-sheet check (carousel/post PNGs + 6–8 reel frames via ffmpeg); fix overflow and re-render. ffprobe the reel for video+audio.
6. `python3 scripts/queue_day.py out/DATE DATE`
7. Update `state.json`: `last_queued_date` = DATE, append the topics to `history`. Commit and push.

## Design (fixed)
- Light "notebook" theme: cream ruled paper, ink text, one brand colour **SAP blue**, yellow highlighter, handwritten (Caveat) notes. All built into generate.py; do not change colours per post.
- Wrap 1-3 key words of every title/heading in `*asterisks*` to get the yellow highlighter, e.g. `"A full *ALV report* in 10 lines"`. Use it on every cover title, heading and CTA title; never on more than half the words.
- Cover `kicker` is a short handwritten note (2-5 words), e.g. "No field catalog needed".
- Slide kinds: cover, text, code, compare, list, cta. Slide text English, short. Max ~12 code lines per panel, ~45 characters per code line.

## Captions (fixed)
- **Professional English**, LinkedIn-like tone. No Hinglish in captions.
- Structure: hook question or bold statement on line 1 -> blank line -> 2-4 short lines or a numbered list with the substance -> blank line -> one engagement line (question or "Save this for ...") -> product line when the post plugs a product ("... ABAP Code Vault (link in bio)" / "ABAP Interview Pack (160 Q&A): link in bio").
- 60-120 words. At most 1 emoji, or none. No invented statistics.

## Hashtags (fixed: 9-10 per post)
Always these 7: `#sap #abap #coding #sapabap #abapdeveloper #saps4hana #sapfresher`
+ 1-2 topic tags (e.g. #alv #performance #sapinterview #cleancode #tcodes #bapi #smartforms #cds)
+ always `#abapcodevault` last.

## Reel voiceover (every reel)
- Every reel slide gets a `"voiceover"` line; the post sets `"voice": "hm_omega", "voice_lang": "hi", "voice_speed": 1.0`.
- Write voiceover ONLY in Devanagari script, Hinglish style. Spell English/ABAP terms phonetically in Devanagari (फॉर ऑल एंट्रीज़, सेलेक्ट, इंटरनल टेबल, वीबैप). Never use Latin letters: ALL-CAPS words get spelled letter by letter, and Latin words switch to an English accent.
- Every reel slide also gets `"spoken"`: the same line in Roman Hinglish. It becomes the word-by-word on-screen captions (do NOT use the key `subtitle` for this; on a cover slide `subtitle` is the visible sub-heading).
- Sound like a person talking to a friend: short sentences, natural pauses with commas and "...", phrases like "suno", "dekho", "twist ye hai", "bas ek IF". Open with a hook in the first 2 seconds.
- 1–3 short sentences per slide, explaining what is on screen. Total reel 30–60 seconds. Use `"voice_speed": 1.0`.
- The engine animates automatically: blocks slide/pop in, code types in line by line across the narration, camera push, scene transitions, progress bar, whoosh/pop SFX, loudness normalised.
- Setup before rendering: `pip install --break-system-packages kokoro-onnx soundfile`, then download into a `tts` folder next to generate.py (or set ABAP_TTS_DIR):
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  - https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
- Check the MP4 has an audio stream (ffprobe) before delivering.
