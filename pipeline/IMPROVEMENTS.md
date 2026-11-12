# Continuous design & motion improvements

Every daily run ships ONE small, tested improvement to how the REELS move: animation, motion, cuts/transitions,
kinetic typography, timing/easing, sound timing. The goal: every reel feels a little more polished and alive than the last.

## Rules (must follow)
1. **Learn first:** run 1-2 web searches each day for a current short-form / motion-design technique
   (e.g. "kinetic typography reels technique", "match cut motion design", "easing anticipation overshoot text",
   "reel hook first frame pattern interrupt"). Pick ONE technique that fits a clean notebook look and can be built
   in PIL + ffmpeg. Note the idea + source URL in the Log row. If nothing fits, take the top unchecked backlog item.
2. Exactly one improvement per run, small and focused (usually 10-80 lines in `pipeline/generate.py`).
   Rotate the focus so it never gets stuck: `improve_next` in `pipeline/state.json` cycles
   **animation → cuts → typography → sound/timing → animation …**; set it to the next one after the run, even if skipped.
3. Never change the fixed brand: palette (cream paper, ink, SAP blue, yellow highlighter), fonts, sizes,
   the notebook grid (text baselines on ruled lines), the JSON schema (old day files must still render),
   voice (hm_psi), 12-18 s length, captions or hashtag rules. No whoosh/swoosh sound on cuts (user disliked it).
   Motion must stay readable: no text moving while the viewer needs to read it, nothing faster than ~0.25 s for text.
4. Test before keeping it: render `pipeline/days/2026-11-12.json` (3 reels: before_after, live_coding + legacy post)
   and `pipeline/days/2026-11-21.json` (interview_chat) into a temp folder AND today's new day file.
   Look at 8 frames per reel plus a 0.1 s frame strip around one cut; confirm video + audio and 12-18 s.
   No OVERLAP WARNING. If anything is broken, overlapping, harder to read, or simply not better: `git checkout pipeline/generate.py` and skip.
5. Log it below (date, area, technique + source, what changed, why it is better) and commit it as its own commit:
   `Improve (<area>): <short description>`.

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
