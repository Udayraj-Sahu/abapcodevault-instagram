# @abapcodevault — weekly Instagram pipeline

Each Sunday run creates the next week's 4 posts.

## Weekly rhythm
| Day | Type | Size | Purpose |
| --- | --- | --- | --- |
| Mon | carousel (6–7 slides) | 1080×1350 | Teach a concept, end with plug for ABAP Code Vault |
| Tue | post (1 slide) | 1080×1350 | Cheat sheet people save |
| Thu | reel (5 frames, ~18 s MP4) | 1080×1920 | Hook + problem + fix; user adds trending audio |
| Sat | carousel (6 slides) | 1080×1350 | Interview question, end with plug for ABAP Interview Pack |

## Steps for a run
1. Read `pipeline/state.json` → `next_week`. Read `pipeline/topics.json` for that week's 4 topics (after week 12, invent new ones, never repeating `history`).
2. Write `weekNN.json` following the schema in `generate.py` and the example `pipeline/weeks/week01.json`.
3. `python3 generate.py weekNN.json out/weekNN` (needs Pillow + ffmpeg).
4. Make a contact sheet of the PNGs, look at it, and fix overflow (shorten text or code) before delivering.
5. Zip `out/weekNN`, send it plus `ALL_CAPTIONS.txt` to the user.
6. Update `state.json`: increment `next_week`, append the 4 topics to `history`.

## Content rules
- Slide text: English, short. Max ~12 code lines per panel, max ~45 characters per code line.
- Captions: Hinglish (Hindi in Roman script mixed with English), friendly, 60–120 words, hook in line 1, ends with a question or "Save karo" and "link in bio" when plugging a product.
- 8–10 hashtags, always include #sapabap #abap #sap #abapcodevault.
- Code must be correct ABAP 7.40+. No company or client names. No invented statistics.
- Slide kinds: cover, text, code, compare, list, cta.

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
