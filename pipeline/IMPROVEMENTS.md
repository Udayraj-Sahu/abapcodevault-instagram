# Continuous design & motion improvements

Every daily run ships ONE small, tested improvement to how reels and posts look and move,
then logs it here. The goal: each week's content looks noticeably more polished than the last.

## Rules (must follow)
1. Exactly one improvement per run, small and focused (usually 10-60 lines in `pipeline/generate.py`).
2. Never change the fixed brand: palette (cream paper, ink, SAP blue, yellow highlighter), fonts,
   slide sizes (1080×1350 / 1080×1920), the JSON schema (old day files must still render), captions or hashtag rules.
3. Allowed areas: reel animations, transitions/cuts, timing and easing, kinetic typography, caption pill
   animation, code-typing effects, highlighter effects, sound-effect timing, layout polish, spacing,
   annotations, visual hierarchy on static slides, carousel cover hooks.
4. Test before keeping it: render `pipeline/days/2026-11-12.json` into a temp folder AND today's new day file.
   Look at contact sheets (slides + 8 reel frames). Confirm the reel still has video + audio.
   If anything is broken, cut off, harder to read, or simply not better: `git checkout pipeline/generate.py` and skip.
5. Log it below (date, area, what changed, why it is better) and commit it as its own commit:
   `Improve: <short description>`.

## Backlog (pick the top unchecked item, or a better idea)
- [x] Rotating reel transitions: rise, slide (page push), zoom (2026-11-11)
- [ ] Highlighter "draw-on": yellow marker sweeps left→right behind words on reels instead of appearing at once
- [x] Code typing per character (typewriter) with a blinking cursor (2026-11-11)
- [x] Spotlight the code line being explained (2026-11-11)
- [ ] Hook punch-in: first 0.6 s of the reel zooms from 1.12 → 1.0 for a stronger first frame
- [x] Handwritten circle + arrow + note on the bug line (2026-11-11)
- [ ] Caption pill: bounce on each new chunk, slight tilt like a sticker
- [ ] End card: "Follow" button pulses twice; progress bar fills with a soft glow
- [ ] Sticky-note style for highlight boxes (slight rotation + paper shadow) on static slides
- [ ] Carousel progress dots on every slide; "swipe" arrow nudges on the cover
- [ ] Cover slide: big handwritten number badge for list posts ("10")
- [ ] Subtle paper grain texture and soft shadow under code boxes
- [x] Transitions + pace chosen per format (2026-11-11)
- [ ] Beat-synced cuts: snap scene changes to the nearest sentence pause in the voiceover
- [ ] Sound polish: softer whoosh for slide cuts, a tiny "tick" when each code line appears

- [ ] Interview chat: typing-dots bubble ("...") before each message appears
- [ ] Quiz: options shake slightly during the countdown; wrong options fade when the answer is revealed
- [ ] Story: subtle film-grain/vignette and a ticking-clock SFX on the time kicker
- [ ] Number format: big number flips like a page counter between scenes
- [ ] Table: rows slide in with a pen-underline under the best option
- [ ] Flow: arrows draw step by step synced to the voice
- [ ] New post kind: "mistake card" (red X on wrong code, green tick on right code side by side)

## Log
| Date | Area | Change | Why |
| --- | --- | --- | --- |
| 2026-11-11 | Reel cuts | Transitions rotate between rise, slide (header stays fixed) and zoom | Same fade every cut felt repetitive; variety keeps attention |
| 2026-11-11 | Variety engine | 8 reel formats, 8 carousel formats, 8 post formats; 13 new slide kinds; stamp/typewriter/draw-on/slide anims; circle/arrow/strike/tick/spotlight overlays; whip/flip/wipe transitions; fast/calm pacing; stamp/tick/scratch SFX | Every post feels different while the brand stays fixed |
| 2026-11-11 | Static slides | Light notebook theme, highlighter on key words, handwritten notes, auto-fit lists | Final brand design; lists never overflow |
