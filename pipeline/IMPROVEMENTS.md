# Continuous design & motion improvements

Every daily run ships ONE small, tested improvement to how reels and posts look and move,
then logs it here. The goal: each week's content looks noticeably more polished than the last.

## Rules (must follow)
1. Exactly one improvement per run, small and focused (usually 10-60 lines in `pipeline/generate.py`).
   **Rotate the area every day: reel → carousel → single post → reel …** The area for today is
   `improve_next` in `pipeline/state.json`; pick the top unchecked item from THAT section of the backlog
   (or a clearly better idea for that area). After the run, set `improve_next` to the next area —
   even if the improvement was skipped. A carousel/post improvement must show on the static PNGs
   (layout, hierarchy, cover hook, code boxes, annotations, spacing), not only in reels.
2. Never change the fixed brand: palette (cream paper, ink, SAP blue, yellow highlighter), fonts,
   slide sizes (1080×1350 / 1080×1920), the JSON schema (old day files must still render), captions or hashtag rules.
3. Allowed areas: reel animations, transitions/cuts, timing and easing, kinetic typography, caption pill
   animation, code-typing effects, highlighter effects, sound-effect timing, layout polish, spacing,
   annotations, visual hierarchy on static slides, carousel cover hooks.
4. Test before keeping it: render `pipeline/days/2026-11-12.json` (it has a post, a carousel and a reel) into a temp folder AND today's new day file.
   Look at contact sheets (slides + 8 reel frames). Confirm the reel still has video + audio.
   No OVERLAP WARNING allowed. If anything is broken, overlapping, cut off, harder to read, or simply not better: `git checkout pipeline/generate.py` and skip.
5. Log it below (date, area, what changed, why it is better) and commit it as its own commit:
   `Improve: <short description>`.

## Backlog (by area — pick the top unchecked item in today's area, or a better idea)

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
