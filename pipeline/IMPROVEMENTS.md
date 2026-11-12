# Continuous design & motion improvements

Every daily run ships ONE small, tested improvement to the REELS: animation, motion, cuts/transitions,
kinetic typography, timing, **voiceover** (pronunciation, pacing, pauses, emphasis, audio clarity) or
**script** (clear natural English wording, subtitle accuracy, glossary in `pipeline/VOICEOVER.md`).
The goal: every reel looks and sounds a little more polished and natural than the last.

## Pacing standard (approved by the user, 12 Nov 2026 — must hold in every reel)
Based on research (short-form retention guides + learning studies, see Log 2026-11-12):
- **The screen must visibly change at least every 3 seconds**: a new element appearing, a highlight/outline/arrow,
  a word emphasis, a code line typing, a punch-in zoom, or a cut. A static hold longer than 3 s is a bug.
  Code panels and SAP screen slides may hold the layout 3-4 s, but something inside them must still move
  (typing, outline, highlighter) so the viewer can read without the frame feeling frozen.
- Long pauses (> 0.25 s) at most ~5-8% of the reel; speaking rate ~155-170 wpm overall (default pace "snappy":
  voice +3%, tightened pauses, "beat" punch-in every ~2.6 s on longer scenes).
- Every improvement must keep or improve this; animation/cuts/typography work should add MORE meaningful
  motion every 2-3 s (word-synced emphasis, step reveals, outlines), never motion that makes text hard to read.

## Rules (must follow)
1. **Every run ships TWO improvements (user decision, 12 Nov):** one VISUAL + one AUDIO/WORDS.
   - Visual rotates: animation → cuts → typography → animation … (`state.json` → `improve_next.visual`)
   - Audio/words rotates: voice → script → sound/timing → voice … (`state.json` → `improve_next.audio`)
   For each: do 1-2 web searches for a current technique, pick ONE idea that fits the clean notebook look and can be
   built with PIL + ffmpeg + Kokoro (or the top unchecked backlog item in that area), implement, test, keep or revert
   it ON ITS OWN. After the run advance both pointers, even if a change was skipped. A failed improvement never
   blocks the other one or tomorrow's reels.
2. Each change is small and focused (usually 10-80 lines). Script changes go in `pipeline/VOICEOVER.md`, the
   generator's checks, and upcoming UNPUBLISHED day files (never published reels).
3. Never change the fixed brand: palette (cream paper, ink, SAP blue, yellow highlighter), fonts, sizes,
   the notebook grid (text baselines on ruled lines), the JSON schema (old day files must still render),
   voice model (am_michael), 12-18 s length, the follow end card, captions or hashtag rules. No whoosh/swoosh on cuts.
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
- [x] Automatic "static hold" check in generate.py: samples frames every 0.5 s, warns "STATIC: ..." if the picture
      barely changes for more than 3 s (12 Nov)
- [x] Keyword beats: punch-in exactly when a *highlighted* title/heading word is spoken, plus fill beats every ~2.6 s;
      no beats on code/screen/compare/table/bug scenes (reading time 3-4 s, motion comes from typing/outlines) (12 Nov)
- [x] Mid-reel re-hook: reels > 20 s get a stamp ("Remember this" for course, "Watch this" otherwise, or
      post "rehook": {"stamp": "Common mistake", "slide": 2}) + stamp sound near 45% of the reel (12 Nov)
- [ ] Re-hook stamp text from the content: write a matching voice line on that slide ("Common mistake: ...")
- [ ] SE11 screen: move the outline to each field exactly when the voice names it (word-timed focus)
- [x] Snappy pace as default: tighter pauses, voice +3%, beat punch-ins every ~2.6 s (user approved 12 Nov)
- [ ] Hook pattern interrupt: frame 1 starts already readable (title fully on screen at t=0) then a 1.08→1.0 punch-in in 0.4 s
- [ ] Anticipation + overshoot: pops dip 3% before growing and settle with a small overshoot (ease_back tuned per element)
- [x] Follow-through: rising text overshoots ~4.6 px once and settles (ease_back on position) (12 Nov)
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
- [x] De-esser after the compressor in VOICE_POLISH (deesser i=0.5): 5-9 kHz band ~5 dB lower vs. overall, no clipping (12 Nov)
- [ ] Warmer EQ (low-shelf +1.5 dB at 180 Hz) in VOICE_POLISH; keep loudness -14 LUFS
- [ ] Room tone: very quiet noise bed under the voice so gaps don't feel dead (no music, no whoosh)
- [ ] Automatic pronunciation check: if a small offline ASR (pip-installable, no Hugging Face) is available, transcribe the reel and flag words that differ from the script

### Script (research-first; was "Translation" while voiceovers were Hinglish)
- [ ] generate.py check: warn if a `voiceover` sentence is longer than 16 words or uses passive voice heavily
- [ ] generate.py check: warn if `spoken` and `voiceover` differ in word count by > 25% (captions out of sync)
- [ ] generate.py check: warn on code symbols (@ = -> #( ) in a voiceover
- [ ] Grow VOICEOVER.md glossary with 10 more ABAP terms as developers say them (BAdI, user exit, IDoc, LUW, COMMIT WORK ...)
- [ ] Hook library in VOICEOVER.md: 15 proven English opening lines by format (bug_hunt, quiz, story ...)
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
| 2026-11-12 | pace (all) | Research: 140-160+ wpm for short-form, visual change every 2-3 s (3-4 s for educational), cut pauses (FlowShorts, Noiz, Kwebby, Lilach Bullock, SocialGrow; Tes/UCLA: comprehension intact up to 1.5x). Measured our reels: 14-18% silence, 6-7 s static scenes. New default pace "snappy": pauses tightened (silence 14% -> 5%), voice +3%, punch-in beat every 2.6 s. Announcement test 24.9 s -> 22.5 s | User compared and approved |
| 2026-11-12 | animation/cuts | Keyword-synced punch-ins + fill beats (change every 2-3 s), reading scenes exempt; mid-reel re-hook stamp for reels > 20 s; automatic STATIC check (> 3 s without visible change) | User request from research findings |
| 2026-11-12 | animation | Follow-through/settle: "up" blocks overshoot ~4.6 px and settle once (restrained bounce, 2-8 px, one rebound) — https://cursa.app/en/page/polish-pass-overlap-secondary-motion-and-subtle-texture | Motion feels considered, not mechanical; still readable |
| 2026-11-12 | voice | De-esser after compression (deesser i=0.5 m=0.5 f=0.45); sibilance band vs. overall -13.3 dB -> -18.2 dB, peak -1.4 dB — https://www.finchley.co.uk/finchley-learning/visual-podcast/audio-engineering-in-a-professional-podcast-post-production-concepts-and-practices-mixing-domains-and-objectives | Softer harsh s/t sounds on phone speakers and earbuds |
