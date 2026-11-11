#!/usr/bin/env python3
"""ABAP Code Vault - Instagram post generator.

Usage:
    python3 generate.py week.json OUT_DIR

week.json schema (see README.md):
{
  "week": 1,
  "handle": "@abapcodevault",
  "posts": [
    {"day": "Mon", "type": "carousel" | "post" | "reel", "slug": "alv-basics",
     "slides": [ {"kind": "cover"|"text"|"code"|"compare"|"list"|"cta", ...} ],
     "seconds_per_slide": 3.5,          # reels only: minimum time per frame
     "voice": "hm_omega", "voice_lang": "hi", "voice_speed": 1.0,   # reels only
     # each reel slide may carry "voiceover": "<Hinglish in Devanagari>"; frames then
     # stay on screen as long as their narration and the MP4 gets an audio track
     "caption": "...", "hashtags": ["#sapabap", ...]}
  ]
}
Carousels and posts render 1080x1350 PNGs. Reels render 1080x1920 frames + an MP4
(no audio: add trending audio inside Instagram).
"""
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

# ---------- Brand ----------
BG = (11, 18, 32)
PANEL = (15, 24, 48)
PANEL_TOP = (19, 30, 54)
BORDER = (36, 50, 77)
WHITE = (255, 255, 255)
TEXT = (232, 237, 245)
MUTED = (199, 208, 222)
DIM = (143, 160, 186)
AMBER = (245, 184, 61)
BLUE = (124, 196, 255)
GREEN = (126, 224, 161)
RED = (255, 138, 128)

FONT_DIRS = ["/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/dejavu"]


def _font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def F_HEAD(s):
    return _font(["InterDisplay-Bold.otf", "Inter-Bold.otf", "DejaVuSans-Bold.ttf"], s)


def F_SEMI(s):
    return _font(["Inter-SemiBold.otf", "DejaVuSans-Bold.ttf"], s)


def F_BODY(s):
    return _font(["Inter-Regular.otf", "DejaVuSans.ttf"], s)


def F_MONO(s):
    return _font(["DejaVuSansMono.ttf"], s)


def F_MONO_B(s):
    return _font(["DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf"], s)


ABAP_KW = set("""
DATA TYPES TYPE TABLE OF STANDARD SORTED HASHED WITH KEY EMPTY UNIQUE NON-UNIQUE BEGIN END
SELECT SINGLE FROM WHERE INTO APPENDING UP TO ROWS FOR ALL ENTRIES IN JOIN INNER LEFT OUTER ON AS
ORDER BY GROUP HAVING LOOP AT ENDLOOP ASSIGNING FIELD-SYMBOL READ INDEX IF ELSE ELSEIF ENDIF
CASE WHEN ENDCASE DO ENDDO WHILE ENDWHILE TRY CATCH ENDTRY CLASS DEFINITION IMPLEMENTATION
ENDCLASS METHOD METHODS ENDMETHOD PUBLIC PRIVATE PROTECTED SECTION IMPORTING EXPORTING CHANGING
RETURNING VALUE REF NEW CAST CALL FUNCTION EXCEPTIONS TABLES PERFORM FORM ENDFORM USING
APPEND INSERT MODIFY DELETE CLEAR SORT ADJACENT DUPLICATES COMPARING DESCENDING ASCENDING
PARAMETERS SELECT-OPTIONS OBLIGATORY DEFAULT MESSAGE RAISE EXCEPTION RETURN EXIT CONTINUE CHECK
REPORT START-OF-SELECTION END-OF-SELECTION INITIALIZATION COND SWITCH REDUCE INIT NEXT
CORRESPONDING MAPPING EXCEPT LINES NOT AND OR IS INITIAL BOUND LINE_EXISTS COMMIT WORK ROLLBACK
SET HANDLER EVENT EVENTS FINAL CREATE OBJECT INTERFACES INTERFACE ENDINTERFACE ABSTRACT REDEFINITION
WRITE SKIP ULINE TRANSPORTING NO FIELDS BINARY SEARCH FIELD-SYMBOLS CONSTANTS STATICS
""".split())

TOKEN_RE = re.compile(r"('[^']*'|`[^`]*`|\|[^|]*\||@?[A-Za-z_][A-Za-z0-9_\-]*|\s+|.)")


def wrap(draw, text, font, max_w):
    """Wrap text to max_w pixels. Keeps explicit newlines."""
    out = []
    for para in str(text).split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            test = (line + " " + w).strip() if line else w
            if draw.textlength(test, font=font) <= max_w:
                line = test
            else:
                if line:
                    out.append(line)
                line = w
        out.append(line)
    return out


def draw_lines(draw, xy, lines, font, fill, spacing):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += spacing
    return y


def pill(draw, x, y, text, font, fg, bg, pad_x=18, pad_y=10, radius=10):
    w = draw.textlength(text, font=font)
    h = font.size
    draw.rounded_rectangle([x, y, x + w + 2 * pad_x, y + h + 2 * pad_y], radius=radius, fill=bg)
    draw.text((x + pad_x, y + pad_y - 2), text, font=font, fill=fg)
    return x + w + 2 * pad_x


def chrome(img, handle, tag, idx, total, accent, tall):
    """Top bar + footer shared by every slide."""
    d = ImageDraw.Draw(img)
    W, H = img.size
    top = 150 if tall else 64
    pill(d, 72, top, tag.upper(), F_MONO_B(26), BG, accent)
    hx = W - 72 - d.textlength(handle, font=F_MONO(28))
    d.text((hx, top + 10), handle, font=F_MONO(28), fill=DIM)
    bottom = H - (260 if tall else 96)
    d.line([72, bottom - 28, W - 72, bottom - 28], fill=BORDER, width=2)
    if total > 1:
        d.text((72, bottom), f"{idx}/{total}", font=F_MONO(28), fill=DIM)
    if idx < total:
        nxt = "Swipe  →" if not tall else ""
        if nxt:
            d.text((W - 72 - d.textlength(nxt, font=F_SEMI(30)), bottom - 2), nxt, font=F_SEMI(30), fill=accent)
    else:
        sv = "Save for later"
        d.text((W - 72 - d.textlength(sv, font=F_SEMI(30)), bottom - 2), sv, font=F_SEMI(30), fill=accent)
    return top + 90, bottom - 60  # content area y0, y1


def code_panel(img, x, y, w, code, accent, max_h, filename="program.abap"):
    d = ImageDraw.Draw(img)
    lines = code.rstrip("\n").split("\n")
    size = 30
    while size > 20:
        f = F_MONO(size)
        longest = max((d.textlength(l, font=f) for l in lines), default=0)
        h_needed = 70 + len(lines) * int(size * 1.6) + 40
        if longest <= w - 64 and h_needed <= max_h:
            break
        size -= 1
    f = F_MONO(size)
    lh = int(size * 1.6)
    h = 70 + len(lines) * lh + 40
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=PANEL, outline=BORDER, width=2)
    d.rounded_rectangle([x, y, x + w, y + 64], radius=22, fill=PANEL_TOP)
    d.rectangle([x, y + 40, x + w, y + 64], fill=PANEL_TOP)
    d.line([x, y + 64, x + w, y + 64], fill=BORDER, width=2)
    for i in range(3):
        cx = x + 34 + i * 30
        d.ellipse([cx - 8, y + 24, cx + 8, y + 40], fill=(58, 74, 104))
    d.text((x + 130, y + 18), filename, font=F_MONO(24), fill=DIM)
    cy = y + 64 + 26
    for ln in lines:
        cx = x + 32
        stripped = ln.lstrip()
        if stripped.startswith('"') or stripped.startswith("*"):
            d.text((cx, cy), ln, font=f, fill=DIM)
        else:
            in_comment = False
            for tok in TOKEN_RE.findall(ln):
                if in_comment:
                    col = DIM
                elif tok.startswith('"'):
                    in_comment = True
                    col = DIM
                elif tok.startswith("'") or tok.startswith("`") or tok.startswith("|"):
                    col = GREEN
                elif tok.upper() in ABAP_KW and tok.isupper():
                    col = accent
                elif re.fullmatch(r"\d+", tok):
                    col = BLUE
                else:
                    col = (214, 222, 234)
                d.text((cx, cy), tok, font=f, fill=col)
                cx += d.textlength(tok, font=f)
        cy += lh
    return y + h


# ---------- Slide kinds ----------

def s_cover(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (180 if tall else 120)
    if s.get("kicker"):
        d.text((72, y), s["kicker"], font=F_SEMI(38), fill=accent)
        y += 70
    tsize = s.get("title_size", 104 if tall else 96)
    lines = wrap(d, s["title"], F_HEAD(tsize), W - 144)
    while len(lines) > 5 and tsize > 60:
        tsize -= 6
        lines = wrap(d, s["title"], F_HEAD(tsize), W - 144)
    y = draw_lines(d, (72, y), lines, F_HEAD(tsize), WHITE, int(tsize * 1.08)) + 40
    if s.get("subtitle"):
        y = draw_lines(d, (72, y), wrap(d, s["subtitle"], F_BODY(42), W - 144), F_BODY(42), MUTED, 60)
    if s.get("code"):
        code_panel(img, 72, y + 50, W - 144, s["code"], accent, y1 - y - 60)


def s_text(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (120 if tall else 50)
    if s.get("heading"):
        y = draw_lines(d, (72, y), wrap(d, s["heading"], F_HEAD(68), W - 144), F_HEAD(68), WHITE, 78) + 36
    bsize = 44 if tall else 42
    for para in str(s.get("body", "")).split("\n\n"):
        y = draw_lines(d, (72, y), wrap(d, para, F_BODY(bsize), W - 144), F_BODY(bsize), MUTED, int(bsize * 1.45)) + 28
    if s.get("highlight"):
        lines = wrap(d, s["highlight"], F_SEMI(40), W - 144 - 70)
        h = len(lines) * 56 + 56
        d.rounded_rectangle([72, y + 10, W - 72, y + 10 + h], radius=18, fill=PANEL, outline=accent, width=3)
        draw_lines(d, (72 + 36, y + 38), lines, F_SEMI(40), WHITE, 56)


def s_code(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (100 if tall else 40)
    if s.get("heading"):
        y = draw_lines(d, (72, y), wrap(d, s["heading"], F_HEAD(60), W - 144), F_HEAD(60), WHITE, 70) + 30
    note_h = 0
    if s.get("note"):
        note_lines = wrap(d, s["note"], F_BODY(36), W - 144)
        note_h = len(note_lines) * 52 + 40
    end = code_panel(img, 72, y, W - 144, s["code"], accent, y1 - y - note_h, s.get("filename", "program.abap"))
    if s.get("note"):
        draw_lines(d, (72, end + 36), note_lines, F_BODY(36), MUTED, 52)


def s_compare(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (100 if tall else 40)
    if s.get("heading"):
        y = draw_lines(d, (72, y), wrap(d, s["heading"], F_HEAD(60), W - 144), F_HEAD(60), WHITE, 70) + 34
    avail = (y1 - y - 40) // 2
    for title, code, col in ((s.get("left_title", "Old way"), s["left"], RED),
                             (s.get("right_title", "New way"), s["right"], GREEN)):
        pill(d, 72, y, title, F_SEMI(28), BG, col)
        y = code_panel(img, 72, y + 66, W - 144, code, accent, avail - 66, s.get("filename", "program.abap")) + 34


def s_list(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (110 if tall else 40)
    if s.get("heading"):
        y = draw_lines(d, (72, y), wrap(d, s["heading"], F_HEAD(64), W - 144), F_HEAD(64), WHITE, 74) + 40
    items = s.get("items", [])
    size = 40
    for i, it in enumerate(items, 1):
        num = f"{i:02d}"
        d.text((72, y + 2), num, font=F_MONO_B(34), fill=accent)
        title, _, rest = str(it).partition(" - ")
        lines = wrap(d, title, F_SEMI(size), W - 144 - 90)
        y = draw_lines(d, (162, y), lines, F_SEMI(size), WHITE, int(size * 1.35))
        if rest:
            y = draw_lines(d, (162, y + 4), wrap(d, rest, F_BODY(34), W - 144 - 90), F_BODY(34), MUTED, 48)
        y += 34


def s_cta(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (260 if tall else 170)
    y = draw_lines(d, (72, y), wrap(d, s.get("title", "Save this post"), F_HEAD(88), W - 144), F_HEAD(88), WHITE, 96) + 40
    y = draw_lines(d, (72, y), wrap(d, s.get("body", ""), F_BODY(42), W - 144), F_BODY(42), MUTED, 60) + 60
    for a in s.get("actions", ["Save", "Share with a friend", "Follow for daily ABAP"]):
        pill(d, 72, y, a, F_SEMI(34), WHITE, PANEL, pad_x=26, pad_y=16, radius=40)
        d.rounded_rectangle([72, y, 72 + d.textlength(a, font=F_SEMI(34)) + 52, y + 34 + 32], radius=40, outline=BORDER, width=2)
        y += 96


KINDS = {"cover": s_cover, "text": s_text, "code": s_code, "compare": s_compare, "list": s_list, "cta": s_cta}


def render_slide(s, idx, total, handle, tag, accent, tall):
    W, H = (1080, 1920) if tall else (1080, 1350)
    img = Image.new("RGB", (W, H), BG)
    y0, y1 = chrome(img, handle, tag, idx, total, accent, tall)
    # Draw content on its own layer, then centre it vertically in the content area.
    layer = Image.new("RGB", (W, H), BG)
    KINDS[s.get("kind", "text")](layer, s, y0, y1, accent, tall)
    diff = ImageChops.difference(layer, Image.new("RGB", (W, H), BG)).getbbox()
    if diff:
        top, bottom = diff[1], diff[3]
        content_h = bottom - top
        target_top = y0 + max(0, ((y1 - y0) - content_h) // 2)
        if tall:
            target_top -= 60  # keep clear of Instagram's caption overlay
        crop = layer.crop((0, top, W, bottom))
        img.paste(crop, (0, max(y0, target_top)))
    return img


TTS_DIR = os.environ.get("ABAP_TTS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts"))
_KOKORO = None


def tts(text, voice, lang, speed, out_wav):
    """Kokoro TTS (pip install kokoro-onnx soundfile; model files in TTS_DIR). Returns seconds."""
    global _KOKORO
    import soundfile as sf
    if _KOKORO is None:
        from kokoro_onnx import Kokoro
        _KOKORO = Kokoro(os.path.join(TTS_DIR, "kokoro-v1.0.onnx"), os.path.join(TTS_DIR, "voices-v1.0.bin"))
    samples, sr = _KOKORO.create(text, voice=voice, speed=speed, lang=lang)
    sf.write(out_wav, samples, sr)
    return len(samples) / sr


def make_reel(frames, out_mp4, durations, audio=None):
    """Stitch frames into an MP4 with short crossfades. durations[i] = seconds frame i is shown.
    audio: optional path to a narration WAV, already aligned to the frame timings."""
    fade = 0.4
    n = len(frames)
    cmd = ["ffmpeg", "-y"]
    for f, d in zip(frames, durations):
        cmd += ["-loop", "1", "-t", f"{d + fade:.3f}", "-i", f]
    if audio:
        cmd += ["-i", audio]
    if n == 1:
        filt = "[0:v]format=yuv420p[out]"
    else:
        parts = []
        prev = "[0:v]"
        offset = 0.0
        for i in range(1, n):
            offset += durations[i - 1]
            lab = f"[v{i}]"
            parts.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}{lab}")
            prev = lab
        filt = ";".join(parts) + f";{prev}format=yuv420p[out]"
    cmd += ["-filter_complex", filt, "-map", "[out]"]
    if audio:
        cmd += ["-map", f"{n}:a", "-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-movflags", "+faststart", out_mp4]
    subprocess.run(cmd, check=True, capture_output=True)


def build_narration(slides, folder, p, default_secs):
    """Synthesize one clip per slide that has 'voiceover'. Returns (durations, wav path or None)."""
    voice = p.get("voice", "hm_omega")
    lang = p.get("voice_lang", "hi")
    speed = float(p.get("voice_speed", 1.0))
    if not any(s.get("voiceover") for s in slides):
        return [default_secs] * len(slides), None, [(0.2, default_secs - 0.6)] * len(slides)
    import numpy as np
    import soundfile as sf
    pieces, durations, speech, sr = [], [], [], 24000
    lead, tail = 0.35, 0.45  # silence before / after each line
    for i, s in enumerate(slides, 1):
        text = s.get("voiceover", "").strip()
        if text:
            wav = os.path.join(folder, f"vo_{i:02d}.wav")
            secs = tts(text, voice, lang, speed, wav)
            data, sr = sf.read(wav, dtype="float32")
            os.remove(wav)
        else:
            data, secs = np.zeros(0, dtype="float32"), 0.0
        shown = max(default_secs if not text else 0.0, lead + secs + tail)
        clip = np.zeros(int(shown * sr), dtype="float32")
        start = int(lead * sr)
        clip[start:start + len(data)] = data[: len(clip) - start]
        pieces.append(clip)
        durations.append(shown)
        speech.append((lead, secs))
    full = np.concatenate(pieces)
    out = os.path.join(folder, "voiceover.wav")
    sf.write(out, full, sr)
    return durations, out, speech


# =====================================================================
# Motion reel engine: animated blocks, camera push, synced captions, SFX
# =====================================================================
FPS = 30
REEL_W, REEL_H = 1080, 1920
CONTENT_TOP, CONTENT_BOTTOM = 300, 1290   # keep clear of captions + Instagram UI
SUB_Y = 1380


def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_back(p):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def text_img(lines, font, fill, spacing, w=None):
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = w or int(max((d0.textlength(l, font=font) for l in lines), default=1)) + 4
    h = spacing * (len(lines) - 1) + int(font.size * 1.3)
    im = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 0
    for ln in lines:
        d.text((0, y), ln, font=font, fill=fill)
        y += spacing
    return im


class Blocks:
    def __init__(self):
        self.items = []

    def add(self, img, x, y, anim="up", pause=0.22, sfx=None):
        self.items.append({"img": img, "x": x, "y": y, "anim": anim, "pause": pause, "sfx": sfx})
        return y + img.size[1]


def _code_blocks(B, x, y, w, code, accent, max_h, filename):
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = code.rstrip("\n").split("\n")
    size = 32
    while size > 20:
        f = F_MONO(size)
        longest = max((d0.textlength(l, font=f) for l in lines), default=0)
        if longest <= w - 64 and 70 + len(lines) * int(size * 1.6) + 40 <= max_h:
            break
        size -= 1
    f = F_MONO(size)
    lh = int(size * 1.6)
    h = 70 + len(lines) * lh + 40
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=22, fill=PANEL + (255,), outline=BORDER + (255,), width=2)
    d.rounded_rectangle([0, 0, w - 1, 64], radius=22, fill=PANEL_TOP + (255,))
    d.rectangle([0, 40, w - 1, 64], fill=PANEL_TOP + (255,))
    d.line([0, 64, w, 64], fill=BORDER + (255,), width=2)
    for i in range(3):
        cx = 34 + i * 30
        d.ellipse([cx - 8, 24, cx + 8, 40], fill=(58, 74, 104, 255))
    d.text((130, 18), filename, font=F_MONO(24), fill=DIM)
    B.add(frame, x, y, "up", 0.25, "pop")
    cy = y + 64 + 26
    for ln in lines:
        lw = int(d0.textlength(ln, font=f)) + 8
        im = Image.new("RGBA", (max(8, lw), lh), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        cx = 0
        stripped = ln.lstrip()
        if stripped.startswith('"') or stripped.startswith("*"):
            dd.text((0, 0), ln, font=f, fill=DIM)
        else:
            in_c = False
            for tok in TOKEN_RE.findall(ln):
                if in_c or tok.startswith('"'):
                    in_c, col = True, DIM
                elif tok[:1] in "'`|":
                    col = GREEN
                elif tok.upper() in ABAP_KW and tok.isupper():
                    col = accent
                elif re.fullmatch(r"\d+", tok):
                    col = BLUE
                else:
                    col = (214, 222, 234)
                dd.text((cx, 0), tok, font=f, fill=col)
                cx += dd.textlength(tok, font=f)
        if ln.strip():
            B.add(im, x + 32, cy, "type", 0.0)
        cy += lh
    return y + h


def build_blocks(s, accent):
    B = Blocks()
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    W = REEL_W
    x, w = 72, W - 144
    kind = s.get("kind", "text")
    y = 0
    if kind == "cover":
        if s.get("kicker"):
            y = B.add(text_img([s["kicker"]], F_SEMI(42), accent, 50), x, y, "up") + 30
        tsize = s.get("title_size", 108)
        lines = wrap(d0, s["title"], F_HEAD(tsize), w)
        while len(lines) > 5 and tsize > 64:
            tsize -= 6
            lines = wrap(d0, s["title"], F_HEAD(tsize), w)
        for ln in lines:  # each title line pops separately = kinetic typography
            y = B.add(text_img([ln], F_HEAD(tsize), WHITE, int(tsize * 1.08)), x, y, "pop", 0.16, "pop") - int(tsize * 0.22)
        y += 60
        if s.get("subtitle"):
            y = B.add(text_img(wrap(d0, s["subtitle"], F_BODY(44), w), F_BODY(44), MUTED, 62, w), x, y, "up")
        if s.get("code"):
            _code_blocks(B, x, y + 50, w, s["code"], accent, CONTENT_BOTTOM - CONTENT_TOP - y - 60, "program.abap")
    elif kind == "text":
        if s.get("heading"):
            y = B.add(text_img(wrap(d0, s["heading"], F_HEAD(72), w), F_HEAD(72), WHITE, 82, w), x, y, "up") + 40
        for para in str(s.get("body", "")).split("\n\n"):
            y = B.add(text_img(wrap(d0, para, F_BODY(46), w), F_BODY(46), MUTED, 66, w), x, y, "up", 0.35) + 30
        if s.get("highlight"):
            hl = wrap(d0, s["highlight"], F_SEMI(44), w - 72)
            h = len(hl) * 60 + 64
            box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            dd = ImageDraw.Draw(box)
            dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=20, fill=PANEL + (255,), outline=accent + (255,), width=4)
            y_ = 30
            for ln in hl:
                dd.text((36, y_), ln, font=F_SEMI(44), fill=WHITE)
                y_ += 60
            y = B.add(box, x, y + 16, "pop", 0.3, "pop")
    elif kind == "code":
        if s.get("heading"):
            y = B.add(text_img(wrap(d0, s["heading"], F_HEAD(64), w), F_HEAD(64), WHITE, 74, w), x, y, "up") + 34
        note_h = 0
        if s.get("note"):
            note_lines = wrap(d0, s["note"], F_BODY(40), w)
            note_h = len(note_lines) * 56 + 40
        y = _code_blocks(B, x, y, w, s["code"], accent, CONTENT_BOTTOM - CONTENT_TOP - y - note_h, s.get("filename", "program.abap"))
        if s.get("note"):
            B.add(text_img(note_lines, F_BODY(40), MUTED, 56, w), x, y + 36, "up", 0.3)
    elif kind == "compare":
        if s.get("heading"):
            y = B.add(text_img(wrap(d0, s["heading"], F_HEAD(64), w), F_HEAD(64), WHITE, 74, w), x, y, "up") + 34
        avail = (CONTENT_BOTTOM - CONTENT_TOP - y - 40) // 2
        for title, code, col in ((s.get("left_title", "Old way"), s["left"], RED),
                                 (s.get("right_title", "New way"), s["right"], GREEN)):
            tw = int(d0.textlength(title, font=F_SEMI(30))) + 40
            p = Image.new("RGBA", (tw, 52), (0, 0, 0, 0))
            ImageDraw.Draw(p).rounded_rectangle([0, 0, tw - 1, 51], radius=10, fill=col + (255,))
            ImageDraw.Draw(p).text((20, 9), title, font=F_SEMI(30), fill=BG)
            B.add(p, x, y, "pop", 0.2, "pop")
            y = _code_blocks(B, x, y + 66, w, code, accent, avail - 66, s.get("filename", "program.abap")) + 34
    elif kind == "list":
        if s.get("heading"):
            y = B.add(text_img(wrap(d0, s["heading"], F_HEAD(66), w), F_HEAD(66), WHITE, 76, w), x, y, "up") + 40
        for i, it in enumerate(s.get("items", []), 1):
            title, _, rest = str(it).partition(" - ")
            tl = wrap(d0, title, F_SEMI(42), w - 90)
            rl = wrap(d0, rest, F_BODY(36), w - 90) if rest else []
            h = len(tl) * 56 + (len(rl) * 50 + 6 if rl else 0) + 10
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            dd = ImageDraw.Draw(im)
            dd.text((0, 2), f"{i:02d}", font=F_MONO_B(36), fill=accent)
            yy = 0
            for ln in tl:
                dd.text((90, yy), ln, font=F_SEMI(42), fill=WHITE)
                yy += 56
            for ln in rl:
                dd.text((90, yy + 6), ln, font=F_BODY(36), fill=MUTED)
                yy += 50
            y = B.add(im, x, y, "up", 0.45) + 34
    elif kind == "cta":
        y = B.add(text_img(wrap(d0, s.get("title", "Save this post"), F_HEAD(92), w), F_HEAD(92), WHITE, 100, w), x, y, "pop", 0.3, "pop") + 40
        y = B.add(text_img(wrap(d0, s.get("body", ""), F_BODY(44), w), F_BODY(44), MUTED, 62, w), x, y, "up") + 60
        for a in s.get("actions", ["Save", "Share", "Follow"]):
            tw = int(d0.textlength(a, font=F_SEMI(38))) + 64
            pimg = Image.new("RGBA", (tw, 80), (0, 0, 0, 0))
            dd = ImageDraw.Draw(pimg)
            dd.rounded_rectangle([0, 0, tw - 1, 79], radius=40, fill=PANEL + (255,), outline=accent + (255,), width=3)
            dd.text((32, 17), a, font=F_SEMI(38), fill=WHITE)
            y = B.add(pimg, x, y, "pop", 0.28, "pop") + 24
    # centre vertically inside the content zone
    top = min(b["y"] for b in B.items)
    bottom = max(b["y"] + b["img"].size[1] for b in B.items)
    off = CONTENT_TOP + max(0, ((CONTENT_BOTTOM - CONTENT_TOP) - (bottom - top)) // 2) - top
    for b in B.items:
        b["y"] += off
    return B.items


def schedule_blocks(blocks, speech_start, speech_len):
    """Give every block an appear time. Code lines type in across the narration."""
    t = 0.12
    n_type = sum(1 for b in blocks if b["anim"] == "type")
    type_step = 0.1
    if n_type:
        type_step = min(0.45, max(0.09, (speech_len * 0.6) / n_type))
    for b in blocks:
        b["t"] = t
        t += type_step if b["anim"] == "type" else b["pause"]
    return blocks


def reel_chrome(handle, tag, accent):
    img = Image.new("RGB", (REEL_W, REEL_H), BG)
    d = ImageDraw.Draw(img)
    # soft vignette glow behind content
    glow = Image.new("L", (REEL_W, REEL_H), 0)
    ImageDraw.Draw(glow).ellipse([-200, 300, REEL_W + 200, 1500], fill=26)
    from PIL import ImageFilter
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(Image.new("RGB", img.size, (20, 34, 60)), img, glow)
    d = ImageDraw.Draw(img)
    pill(d, 72, 150, tag.upper(), F_MONO_B(28), BG, accent)
    hx = REEL_W - 72 - d.textlength(handle, font=F_MONO(30))
    d.text((hx, 160), handle, font=F_MONO(30), fill=DIM)
    return img


def chunk_words(text, max_words=4, max_chars=24):
    words = text.split()
    chunks, cur = [], []
    for w_ in words:
        if cur and (len(cur) >= max_words or len(" ".join(cur + [w_])) > max_chars):
            chunks.append(cur)
            cur = []
        cur.append(w_)
        if w_[-1:] in ".?!," and len(cur) >= 2:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def word_timeline(text, start, length):
    """[(chunk_words, [(word, t0, t1), ...])] with times proportional to word length."""
    chunks = chunk_words(text)
    weights = [len(w_) + 2.5 for c in chunks for w_ in c]
    total = sum(weights) or 1
    t = start
    out = []
    k = 0
    for c in chunks:
        wt = []
        for w_ in c:
            dur = length * weights[k] / total
            wt.append((w_, t, t + dur))
            t += dur
            k += 1
        out.append(wt)
    return out


def draw_subtitle(img, timeline, tau, accent):
    if not timeline:
        return
    cur = None
    for wt in timeline:
        if wt[0][1] - 0.05 <= tau:
            cur = wt
    if cur is None:
        return
    if tau > cur[-1][2] + 1.2 and cur is timeline[-1]:
        return
    d = ImageDraw.Draw(img, "RGBA")
    f = F_HEAD(62)
    words = [w_ for w_, _, _ in cur]
    gap = d.textlength(" ", font=f)
    widths = [d.textlength(w_, font=f) for w_ in words]
    total = sum(widths) + gap * (len(words) - 1)
    x = (REEL_W - total) / 2
    pad = 28
    # pop-in for the chunk
    p = min(1.0, max(0.0, (tau - cur[0][1] + 0.05) / 0.18))
    sc = 0.85 + 0.15 * ease_back(p)
    bh = 96 * sc
    d.rounded_rectangle([x - pad, SUB_Y - bh / 2, x + total + pad, SUB_Y + bh / 2], radius=24,
                        fill=(0, 0, 0, int(150 * p)))
    for (w_, t0, t1), ww in zip(cur, widths):
        active = t0 <= tau < t1 + 0.05
        col = accent if active else WHITE
        if tau < t0:
            col = (200, 208, 222)
        d.text((x, SUB_Y - 38), w_, font=f, fill=col)
        x += ww + gap


def render_scene(base, blocks, tau, dur, sub_tl, accent):
    content = Image.new("RGBA", (REEL_W, REEL_H), (0, 0, 0, 0))
    for b in blocks:
        p = (tau - b["t"]) / (0.18 if b["anim"] == "type" else 0.5)
        if p <= 0:
            continue
        p = min(1.0, p)
        im = b["img"]
        x, y = b["x"], b["y"]
        if b["anim"] == "type":
            e = ease_out(p)
            if p < 1:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda v, e=e: int(v * e)))
            x = int(x - (1 - e) * 24)
        elif b["anim"] == "pop":
            e = ease_back(p)
            sc = 0.86 + 0.14 * e
            if p < 1:
                w0, h0 = im.size
                im = im.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.BILINEAR)
                a = min(1.0, p * 2.2)
                im.putalpha(im.getchannel("A").point(lambda v, a=a: int(v * a)))
                x = int(x + (w0 - im.size[0]) / 2 * 0.0)
                y = int(y + (h0 - im.size[1]) / 2)
        else:
            e = ease_out(p)
            if p < 1:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda v, e=e: int(v * e)))
            y = int(y + (1 - e) * 46)
        content.alpha_composite(im, (int(x), int(y)))
    # slow camera push on the content
    z = 1.0 + 0.04 * ease_out(min(1.0, tau / max(dur, 0.1)))
    if z > 1.001:
        zw, zh = int(REEL_W * z), int(REEL_H * z)
        content = content.resize((zw, zh), Image.BILINEAR)
        cx, cy = (zw - REEL_W) // 2, int((zh - REEL_H) * 0.42)
        content = content.crop((cx, cy, cx + REEL_W, cy + REEL_H))
    frame = base.copy()
    frame.paste(content, (0, 0), content)
    draw_subtitle(frame, sub_tl, tau, accent)
    return frame


def synth_sfx(kind, sr=24000):
    import numpy as np
    if kind == "whoosh":
        n = int(0.42 * sr)
        noise = np.random.default_rng(7).standard_normal(n).astype("float32")
        # crude band-pass: smooth then difference
        k = 18
        smooth = np.convolve(noise, np.ones(k) / k, mode="same")
        band = smooth - np.convolve(smooth, np.ones(120) / 120, mode="same")
        env = np.sin(np.linspace(0, np.pi, n)) ** 2
        return (band * env * 0.55).astype("float32")
    n = int(0.09 * sr)
    t = np.arange(n) / sr
    freq = 900 * np.exp(-t * 28) + 260
    phase = 2 * np.pi * np.cumsum(freq) / sr
    return (np.sin(phase) * np.exp(-t * 55) * 0.16).astype("float32")


def make_motion_reel(p, slides, folder, handle, accent):
    import numpy as np
    import soundfile as sf
    default = float(p.get("seconds_per_slide", 3.5))
    has_vo = any(s.get("voiceover") for s in slides)
    if has_vo:
        durations, vo_wav, speech = build_narration(slides, folder, p, default)
        voice, sr = sf.read(vo_wav, dtype="float32")
    else:
        durations, speech, sr = [default] * len(slides), [(0.2, default - 0.6)] * len(slides), 24000
        voice = np.zeros(int(sum(durations) * sr), dtype="float32")
    base = reel_chrome(handle, p.get("tag", "SAP ABAP"), accent)
    scenes = []
    for s, dur, (st, ln) in zip(slides, durations, speech):
        blocks = schedule_blocks(build_blocks(s, accent), st, ln)
        sub = s.get("spoken") or ""
        tl = word_timeline(sub, st, ln) if (sub and ln > 0) else []
        scenes.append((blocks, dur, tl))
    starts = [sum(durations[:i]) for i in range(len(durations))]
    total = sum(durations)

    # ---- audio: voice + sfx, loudness-normalised later by ffmpeg
    mix = np.zeros(int(total * sr) + sr, dtype="float32")
    mix[: len(voice)] += voice
    whoosh, popf = synth_sfx("whoosh", sr), synth_sfx("pop", sr)
    for i, st0 in enumerate(starts):
        if i > 0:
            a = max(0, int((st0 - 0.2) * sr))
            mix[a:a + len(whoosh)] += whoosh[: len(mix) - a]
        for b in scenes[i][0]:
            if b.get("sfx") == "pop":
                a = int((st0 + b["t"]) * sr)
                mix[a:a + len(popf)] += popf[: len(mix) - a]
    mix = np.clip(mix, -1, 1)
    mix_wav = os.path.join(folder, "_mix.wav")
    sf.write(mix_wav, mix, sr)

    # ---- video: pipe frames to ffmpeg
    out_mp4 = os.path.join(folder, "reel.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{REEL_W}x{REEL_H}", "-r", str(FPS), "-i", "-", "-i", mix_wav,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", out_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    trans = 0.35
    n_frames = int(total * FPS)
    for fi in range(n_frames):
        t = fi / FPS
        i = max(k for k, st0 in enumerate(starts) if st0 <= t + 1e-9)
        tau = t - starts[i]
        blocks, dur, tl = scenes[i]
        frame = render_scene(base, blocks, tau, dur, tl, accent)
        if i > 0 and tau < trans:
            pb, pd, ptl = scenes[i - 1]
            prev = render_scene(base, pb, pd + tau, pd, ptl, accent)
            # outgoing scene drifts up while fading
            e = ease_out(tau / trans)
            prev = prev.transform(prev.size, Image.AFFINE, (1, 0, 0, 0, 1, int(60 * e)), fillcolor=BG)
            frame = Image.blend(prev, frame, e)
        # progress bar
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([72, 100, REEL_W - 72, 106], radius=3, fill=BORDER)
        d.rounded_rectangle([72, 100, 72 + int((REEL_W - 144) * (t / total)), 106], radius=3, fill=accent)
        proc.stdin.write(frame.tobytes())
        if fi == int((starts[i] + dur * 0.9) * FPS):
            frame.save(os.path.join(folder, f"frame_{i + 1:02d}.png"), optimize=True)
    proc.stdin.close()
    proc.wait()
    for f_ in (mix_wav, os.path.join(folder, "voiceover.wav")):
        if os.path.exists(f_):
            os.remove(f_)
    return out_mp4


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    handle = spec.get("handle", "@abapcodevault")
    captions = []
    accents = {"carousel": AMBER, "post": BLUE, "reel": GREEN}
    for n, p in enumerate(spec["posts"], 1):
        ptype = p["type"]
        tall = ptype == "reel"
        accent = tuple(p["accent"]) if p.get("accent") else accents.get(ptype, AMBER)
        folder = os.path.join(out, f"{n:02d}_{p.get('day', '')}_{ptype}_{p.get('slug', 'post')}")
        os.makedirs(folder, exist_ok=True)
        slides = p["slides"]
        if not tall:
            for i, s in enumerate(slides, 1):
                img = render_slide(s, i, len(slides) if ptype != "post" else 1, handle,
                                   p.get("tag", "SAP ABAP"), accent, tall)
                img.save(os.path.join(folder, f"slide_{i:02d}.png"), optimize=True)
        else:
            make_motion_reel(p, slides, folder, handle, accent)
            script = [s.get("voiceover", "") for s in slides if s.get("voiceover")]
            if script:
                with open(os.path.join(folder, "voiceover_script.txt"), "w", encoding="utf-8") as fh:
                    fh.write("\n\n".join(script) + "\n")
        cap = p.get("caption", "").strip() + "\n\n" + " ".join(p.get("hashtags", []))
        with open(os.path.join(folder, "caption.txt"), "w", encoding="utf-8") as fh:
            fh.write(cap.strip() + "\n")
        captions.append(f"=== {n:02d} | {p.get('day', '')} | {ptype.upper()} | {p.get('slug', '')} ===\n{cap.strip()}\n")
        print("rendered", folder)
    with open(os.path.join(out, "ALL_CAPTIONS.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(captions))


if __name__ == "__main__":
    main()
