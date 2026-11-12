# Continuous design & motion improvements

Every daily run ships ONE small, tested improvement to the REELS: animation, motion, cuts/transitions,
kinetic typography, timing, **voiceover** (pronunciation, pacing, pauses, emphasis, audio clarity) or
**translation** (natural Hinglish phrasing, caption accuracy, glossary in `pipeline/HINGLISH.md`).
The goal: every reel looks and sounds a little more polished and natural than the last.

## Rules (must follow)
1. **Every run improves ALL six areas** — one small change per area, in this order:
   **animation → voice → cuts → translation → typography → sound/timing**.
   For each area: do 1-2 web searches for a current technique (short-form editing, motion design, TTS/narration,
   Hinglish writing...), pick ONE idea that fits the clean notebook look and can be built with PIL + ffmpeg + Kokoro
   (or take the top unchecked backlog item in that area), implement it, test it, then keep or revert it ON ITS OWN.
   A failed area never blocks the others or the day's reels. Aim for 6 kept changes; 4+ is a good day.
2. Each change is small and focused (usually 10-80 lines). Translation changes go in `pipeline/HINGLISH.md`, the
   generator's checks, and upcoming UNPUBLISHED day files (never published reels).
3. Never change the fixed brand: palette (cream paper, ink, SAP blue, yellow highlighter), fonts, sizes,
   the notebook grid (text baselines on ruled lines), the JSON schema (old day files must still render),
   voice model (hm_psi), 12-18 s length, the follow end card, captions or hashtag rules. No whoosh/swoosh on cuts.
   Motion must stay readable: no text moving while the viewer needs to read it, nothing faster than ~0.25 s for text.
4. Test EACH change before keeping it: render `pipeline/days/2026-11-12.json` (2 reels) and `pipeline/days/2026-11-21.json`
   (interview_chat) into a temp folder. Look at 8 frames per reel plus a strip of frames 0.1 s apart around one cut;
   confirm video + audio and 12-18 s; no OVERLAP/other WARNING. Voice changes: compare voiceover_script.txt and
   durations before/after and confirm no clipping (ffmpeg volumedetect max_volume < -0.5 dB).
   If broken, overlapping, harder to read/hear, or simply not better: revert just that change (git checkout / git stash it).
5. Commit each kept change separately as `Improve (<area>): <short description>` and add one Log row per change
   (date, area, technique + source URL, what changed, why it is better). Keep backlog boxes ticked.

## Backlog (reels; research-first — carousel/post sections are legacy)

### Reel
- [x] Rotating reel transitions: rise, slide (page push), zoom (2026-11-11)
- [ ] Highlighter "draw-on": yellow marker sweeps left→right behind words on reels instead of appearing at once
- [x] Code typing per character (typewriter) with a blinking cursor (2026-11-11)
- [x] Spotlight the code line being explained (2026-11-11)
- [ ] Hook punch-in: first 0.6 s of the reel zooms from 1.12 → 1.0 for a stronger first frame
- [x] Handwritten circle + arrow + note on the bug line (2026-11-11)
- [ ] Caption pill: bounce on each new chunk, slight tilt like a sticker
- [ ] End card: "Follow" button pulses twice; progress bar fills with a soft glow
- [x] Transitions + pace chosen per format (2026-11-11)
- [ ] Beat-synced cuts: snap scene changes to the nearest sentence pause in the voiceover
- [ ] Interview chat: typing-dots bubble ("...") before each message appears
- [ ] Quiz: options shake slightly during the countdown; wrong options fade when the answer is revealed
- [ ] Story: subtle film-grain/vignette and a ticking-clock SFX on the time kicker
- [ ] Number format: big number flips like a page counter between scenes
- [ ] Table: rows slide in with a pen-underline under the best option
- [ ] Flow: arrows draw step by step synced to the voice
- [ ] Sound polish: a tiny soft "tick" when each code line appears (no whoosh on cuts — user disliked it)

### Reel — ideas from research (2026-11-12)
- [ ] Hook pattern interrupt: frame 1 starts already readable (title fully on screen at t=0) then a 1.08→1.0 punch-in in 0.4 s
- [ ] Anticipation + overshoot: pops dip 3% before growing and settle with a small overshoot (ease_back tuned per element)
- [ ] Follow-through: after a block lands, its highlighter/underline settles 80 ms later (secondary motion)
- [ ] Match cut: the highlighted key word of scene N flies/morphs into the heading position of scene N+1
- [ ] Cut on action: start the next scene's transition while the last element is still moving (overlap 0.12 s)
- [ ] Word-level emphasis synced to voice: the key word pulses (scale 1.06) exactly when it is spoken
- [ ] Parallax: ruled paper drifts 6-10 px slower than content during slide/zoom transitions (depth)
- [ ] Motion blur / smear on fast transitions (blend 2-3 sub-frames) for smoother 30 fps movement
- [ ] Ease library: replace linear moves with easeOutExpo / easeInOutCubic consistently; test curves frame by frame

### Voice (research-first)
- [ ] Pause map: 0.25 s after commas, 0.45 s after full stops, 0.6 s between scenes (instead of one fixed gap)
- [ ] Key-word emphasis: slow the sentence containing the *highlighted* word by 5% and add a 0.15 s pause before it
- [ ] Pronunciation audit: render every SAY entry once, list any that sound wrong, fix spellings (e.g. sy-subrc, SM30, BSEG)
- [ ] Per-sentence speed: hook sentence 1.05x, explanation 0.97x, CTA 1.0x
- [ ] Gentle de-esser + warmer EQ (low-shelf +1.5 dB at 180 Hz) in VOICE_POLISH; keep loudness -14 LUFS
- [ ] Room tone: very quiet noise bed under the voice so gaps don't feel dead (no music, no whoosh)
- [ ] Automatic pronunciation check: if a small offline ASR (pip-installable, no Hugging Face) is available, transcribe the reel and flag words that differ from the script

### Translation (research-first)
- [ ] generate.py check: warn if a `voiceover` contains Latin-script Hindi words (hai, karo, mein) or Devanagari-transliterated English (सेलेक्ट)
- [ ] generate.py check: warn if `spoken` and `voiceover` differ in word count by > 25% (captions out of sync)
- [ ] generate.py check: warn on code symbols (@ = -> #( ) in a voiceover
- [ ] Grow HINGLISH.md glossary with 10 more ABAP terms as developers say them (BAdI, user exit, IDoc, LUW, COMMIT WORK ...)
- [ ] Hook library in HINGLISH.md: 15 proven Hinglish opening lines by format (bug_hunt, quiz, story ...)
- [ ] Caption chunking: break captions at natural phrase boundaries, never between a number and its unit

### Carousel
- [ ] Carousel progress dots on every slide; "swipe" arrow nudges on the cover
- [ ] Cover slide: big handwritten number badge for list posts ("10")
- [ ] Cover: bigger hook — handwritten kicker with a hand-drawn underline + a small arrow to the title
- [ ] "Swipe →" handwritten note on the cover, bottom-right
- [ ] Slide numbers like notebook page numbers ("2/7") in the margin, handwritten
- [ ] Recap slide before CTA: 3 ticked one-liners summarising the carousel
- [ ] Code slides: line numbers in the margin + one key line highlighted with marker
- [ ] Consistent spacing rhythm: same top offset and gaps on every inner slide
- [ ] CTA slide: "Save this for your next interview" with a hand-drawn bookmark icon

### Single post
- [ ] Sticky-note style for highlight boxes (slight rotation + paper shadow) on static slides
- [ ] Subtle paper grain texture and soft shadow under code boxes
- [ ] New post kind: "mistake card" (red X on wrong code, green tick on right code side by side)
- [ ] Cheat-sheet posts: two-column layout with section labels in SAP blue small caps
- [ ] Handwritten margin note pointing at the single most important row
- [ ] Footer strip: "@abapcodevault · save for later" with a small bookmark doodle
- [ ] Code-only posts: soft card shadow + tab label ("ABAP 7.40") on the code box
- [ ] Title block: heavier weight + marker on 1-2 words + thin rule under it
- [ ] Tables: zebra rows on paper tint, header row in SAP blue, check/cross icons drawn by hand

## Log
| Date | Area | Change | Why |
| --- | --- | --- | --- |
| 2026-11-11 | Reel cuts | Transitions rotate between rise, slide (header stays fixed) and zoom | Same fade every cut felt repetitive; variety keeps attention |
| 2026-11-11 | Variety engine | 8 reel formats, 8 carousel formats, 8 post formats; 13 new slide kinds; stamp/typewriter/draw-on/slide anims; circle/arrow/strike/tick/spotlight overlays; whip/flip/wipe transitions; fast/calm pacing; stamp/tick/scratch SFX | Every post feels different while the brand stays fixed |
| 2026-11-11 | Static slides | Light notebook theme, highlighter on key words, handwritten notes, auto-fit lists | Final brand design; lists never overflow |
| 2026-11-12 | All (static + reels) | Notebook grid: every text baseline on a ruled line, fixed line pitches (64/128), header/footer on rules, code & highlight boxes between rules, centring in whole lines, list rows with aligned description column, equal-height choice cards, matched code size in compare slides, footer/caption overflow check | User: text alignment and line height looked uneven against the ruled paper |
