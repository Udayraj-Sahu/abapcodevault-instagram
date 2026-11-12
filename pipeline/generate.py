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
# Light "notebook" theme with SAP blue accent
BG = (251, 248, 241)        # cream paper
RULE = (232, 227, 214)      # ruled lines
MARGIN = (242, 196, 196)    # notebook margin line
PANEL = (243, 240, 233)     # code box
PANEL_TOP = (234, 230, 220)
BORDER = (219, 212, 198)
WHITE = (27, 31, 42)        # INK: used for headings (name kept for compatibility)
INK = WHITE
TEXT = INK
MUTED = (72, 80, 96)
DIM = (125, 131, 145)
SAP_BLUE = (10, 110, 209)
AMBER = SAP_BLUE
BLUE = SAP_BLUE
GREEN = (46, 125, 50)       # strings in code / "new way" pill
RED = (200, 62, 62)         # "old way" pill
NUM = (176, 96, 20)         # numbers in code
MARKER = (255, 226, 110)    # yellow highlighter
CODE_INK = (38, 44, 58)

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


def F_HAND(s):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Caveat-Bold.woff")
    if os.path.exists(p):
        return ImageFont.truetype(p, s)
    return F_SEMI(s)


def F_MONO(s):
    return _font(["DejaVuSansMono.ttf"], s)


def F_MONO_B(s):
    return _font(["DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf"], s)


# ---------- Notebook grid: every text baseline sits on a ruled line ----------
G = 64          # ruled-line spacing (lines at y = 64, 128, ...)


def asc(font):
    return font.getmetrics()[0]


def snap_base(y, base):
    """Smallest y' >= y so that y' + base lands exactly on a ruled line."""
    return y + ((-(int(y) + int(base))) % G)


def grid_box(y, h, pad=16):
    """Top/height of a box that starts `pad` px below a rule and ends `pad` px above one."""
    top = int(y) + ((pad - int(y)) % G)
    hh = -(-(h + 2 * pad) // G) * G - 2 * pad
    return top, hh


def code_size_for(codes, w, y, ylimit):
    """Largest mono size (30 -> 20) at which the label + code-box pairs, laid out exactly as
    s_compare/_code_blocks do (grid-snapped), end above `ylimit`."""
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for size in range(30, 19, -1):
        f = F_MONO(size)
        if any(max(d0.textlength(l, font=f) for l in c.rstrip("\n").split("\n")) > w - 64 for c in codes):
            continue
        yy = y
        for c in codes:
            top, _ = grid_box(yy + 66, 10)
            _, h = grid_box(top, 70 + len(c.rstrip("\n").split("\n")) * int(size * 1.6) + 40)
            yy = top + h + 34
        if yy - 34 <= ylimit:
            return size
    return 20


def head_font(size):
    """Heading sizes map to two grid-friendly styles: 58 px on 1 line pitch, 108 px on 2."""
    return (F_HEAD(108), 2 * G) if size >= 88 else (F_HEAD(58), G)


def grid_spacing(spacing):
    return G if 44 <= spacing <= 96 else spacing


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


def draw_lines(draw, xy, lines, font, fill, spacing, snap=True):
    x, y = xy
    if snap:
        spacing = grid_spacing(spacing)
        if spacing == G:
            y = snap_base(y, asc(font))
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


def paper(img):
    """Cream notebook paper: faint ruled lines + margin line."""
    d = ImageDraw.Draw(img)
    W, H = img.size
    for y in range(64, H, 64):
        d.line([0, y, W, y], fill=RULE, width=2)
    d.line([40, 0, 40, H], fill=MARGIN, width=3)


def marked_tokens(text):
    """'Plain *highlighted words* plain' -> [(word, marked), ...]"""
    out = []
    prev = ""
    for i, seg in enumerate(str(text).split("*")):
        words = seg.split()
        glued = prev and not prev[-1:].isspace() and seg and not seg[:1].isspace()
        prev = seg
        if words and out and glued:
            # punctuation right after a closing/opening marker sticks to the previous word
            pw, pm = out[-1]
            out[-1] = (pw + words[0], pm)
            words = words[1:]
        for w in words:
            out.append((w, i % 2 == 1))
    return out


def wrap_marked(tokens, font, maxw):
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines, cur = [], []
    for t in tokens:
        test = " ".join(w for w, _ in cur + [t])
        if cur and d0.textlength(test, font=font) > maxw:
            lines.append(cur)
            cur = []
        cur.append(t)
    if cur:
        lines.append(cur)
    return lines


def line_img(tokens, font, fill=None, w=None):
    """One line of words; marked words get a yellow highlighter stroke behind them."""
    fill = fill or INK
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    gap = d0.textlength(" ", font=font)
    widths = [d0.textlength(t, font=font) for t, _ in tokens]
    total = int(sum(widths) + gap * max(0, len(tokens) - 1)) + 24
    h = int(font.size * 1.3)
    a = asc(font)
    im = Image.new("RGBA", (max(w or 0, total), h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 6
    for i, ((t, mk), ww) in enumerate(zip(tokens, widths)):
        if mk:
            nxt = i + 1 < len(tokens) and tokens[i + 1][1]
            x1 = x + ww + (gap if nxt else 0) + 6
            # marker band: from about x-height to just under the baseline
            d.rounded_rectangle([x - 6, a - int(font.size * 0.56), x1, a + int(font.size * 0.12)],
                                radius=6, fill=MARKER + (255,))
        x += ww + gap
    x = 6
    for (t, _), ww in zip(tokens, widths):
        d.text((x, 0), t, font=font, fill=fill)
        x += ww + gap
    im.info["base"] = a
    return im


def heading_img(text, font, maxw, fill=None, lh=None):
    """Multi-line heading with *marker* support, as one RGBA image."""
    font, lh = head_font(font.size)
    lines = wrap_marked(marked_tokens(text), font, maxw)
    imgs = [line_img(l, font, fill) for l in lines]
    h = lh * (len(imgs) - 1) + (imgs[-1].size[1] if imgs else 1)
    out = Image.new("RGBA", (maxw + 40, max(1, h)), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        out.alpha_composite(im, (0, i * lh))
    out.info["base"] = asc(font)
    return out


def paste_heading(img, x, y, text, font, maxw, fill=None, lh=None):
    im = heading_img(text, font, maxw, fill, lh)
    y = snap_base(y, im.info["base"])
    img.paste(im, (x - 6, y), im)
    return y + im.size[1]


def chrome(img, handle, tag, idx, total, accent, tall):
    """Top bar + footer shared by every slide."""
    paper(img)
    d = ImageDraw.Draw(img)
    W, H = img.size
    if tall:
        top = 150
        pill(d, 72, top, tag.upper(), F_MONO_B(26), (255, 255, 255), accent)
        hx = W - 72 - d.textlength(handle, font=F_MONO(28))
        d.text((hx, top + 10), handle, font=F_MONO(28), fill=DIM)
        bottom = H - 260
        d.line([72, bottom - 28, W - 72, bottom - 28], fill=BORDER, width=2)
        if total > 1:
            d.text((72, bottom), f"{idx}/{total}", font=F_MONO(28), fill=DIM)
        if idx >= total:
            sv = "save this for later!"
            d.text((W - 72 - d.textlength(sv, font=F_HAND(46)), bottom - 14), sv, font=F_HAND(46), fill=accent)
        return top + 90, bottom - 60
    # feed slides: header text sits on rule 2 (y=128), footer on the last full rule, divider on a rule
    hb, fb = 2 * G, (H // G - 1) * G            # 128, 1280 for 1350
    div = fb - G                                 # 1216
    tf = F_MONO_B(26)
    pill(d, 72, hb - asc(tf) - 10 + 2, tag.upper(), tf, (255, 255, 255), accent)
    hf = F_MONO(28)
    d.text((W - 72 - d.textlength(handle, font=hf), hb - asc(hf)), handle, font=hf, fill=DIM)
    d.line([72, div, W - 72, div], fill=BORDER, width=2)
    if total > 1:
        d.text((72, fb - asc(hf)), f"{idx}/{total}", font=hf, fill=DIM)
    fh = F_HAND(46)
    if idx < total:
        arrow, word = "→", "swipe "
        af = F_SEMI(36)
        aw = d.textlength(arrow, font=af)
        ww = d.textlength(word, font=fh)
        d.text((W - 72 - aw - ww, fb - asc(fh)), word, font=fh, fill=accent)
        d.text((W - 72 - aw, fb - asc(af)), arrow, font=af, fill=accent)
    else:
        sv = "save this for later!"
        d.text((W - 72 - d.textlength(sv, font=fh), fb - asc(fh)), sv, font=fh, fill=accent)
    return hb + 40, div - 40  # content area y0, y1


def code_panel(img, x, y, w, code, accent, max_h, filename="program.abap", size=None):
    d = ImageDraw.Draw(img)
    lines = code.rstrip("\n").split("\n")
    fixed = size
    size = fixed or 30
    while size > 20 and not fixed:
        f = F_MONO(size)
        longest = max((d.textlength(l, font=f) for l in lines), default=0)
        h_needed = grid_box(0, 70 + len(lines) * int(size * 1.6) + 40)[1] + 16
        if longest <= w - 64 and h_needed <= max_h:
            break
        size -= 1
    f = F_MONO(size)
    lh = int(size * 1.6)
    h0 = 70 + len(lines) * lh + 40
    y, h = grid_box(y, h0)
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=PANEL, outline=BORDER, width=2)
    d.rounded_rectangle([x, y, x + w, y + 64], radius=22, fill=PANEL_TOP)
    d.rectangle([x, y + 40, x + w, y + 64], fill=PANEL_TOP)
    d.line([x, y + 64, x + w, y + 64], fill=BORDER, width=2)
    for i in range(3):
        cx = x + 34 + i * 30
        d.ellipse([cx - 8, y + 24, cx + 8, y + 40], fill=(205, 197, 182))
    d.text((x + 130, y + 18), filename, font=F_MONO(24), fill=DIM)
    cy = y + 64 + 26 + (h - h0) // 2
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
                    col = NUM
                else:
                    col = CODE_INK
                d.text((cx, cy), tok, font=f, fill=col)
                cx += d.textlength(tok, font=f)
        cy += lh
    return y + h


def list_row_img(i, item, w, accent, lsize=40, dsize=34, col=None):
    """'Label - description' as a notebook row: number, bold label and muted description share one
    baseline; a long description continues on the next ruled line."""
    lf, df, nf = F_SEMI(lsize), F_BODY(dsize), F_MONO_B(int(lsize * 0.78))
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    label, _, desc = str(item).partition(" - ")
    ind = 84
    a = asc(lf)
    lab_lines = wrap(d0, label, lf, w - ind)
    lw = d0.textlength(lab_lines[-1], font=lf)
    rows = [(0, ind, l, lf, WHITE) for l in lab_lines]
    r = len(lab_lines) - 1
    if desc:
        sep = 26
        dx = max(col, lw + sep) if col else lw + sep
        if dx + d0.textlength(desc, font=df) <= w - ind:
            rows.append((r, ind + dx, desc, df, MUTED))
        else:
            for dl in wrap(d0, desc, df, w - ind):
                r += 1
                rows.append((r, ind, dl, df, MUTED))
    nrows = max(rr for rr, *_ in rows) + 1 if rows else 1
    h = (nrows - 1) * G + a + lf.getmetrics()[1] + 4
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((0, a - asc(nf)), f"{i:02d}", font=nf, fill=accent)
    k = 0
    for rr, xx, t, f, col in rows:
        if f is lf:
            rr = k
            k += 1
        d.text((xx, a + rr * G - asc(f)), t, font=f, fill=col)
    im.info["base"] = a
    im.info["rows"] = nrows
    return im


def list_col(items, w, lsize, dsize):
    """Shared x for descriptions so they line up in one column (None if a description wouldn't fit)."""
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    parts = [str(it).partition(" - ") for it in items]
    if not parts or any(len(wrap(d0, l, F_SEMI(lsize), w - 84)) > 1 for l, _, _ in parts):
        return None
    col = max(d0.textlength(l, font=F_SEMI(lsize)) for l, _, _ in parts) + 30
    if all(col + d0.textlength(dd, font=F_BODY(dsize)) <= w - 84 for _, _, dd in parts):
        return col
    return None


# ---------- Slide kinds ----------

def s_cover(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (180 if tall else 120)
    if s.get("kicker"):
        kf = F_HAND(58)
        y = snap_base(y, asc(kf))
        d.text((72, y), s["kicker"], font=kf, fill=accent)
        y += asc(kf) + 24
    tsize = s.get("title_size", 104 if tall else 96)
    if len(wrap_marked(marked_tokens(s["title"]), head_font(tsize)[0], W - 144)) > 4:
        tsize = 64
    y = paste_heading(img, 72, y, s["title"], F_HEAD(tsize), W - 144) + 24
    if s.get("subtitle"):
        y = draw_lines(d, (72, y), wrap(d, s["subtitle"], F_BODY(42), W - 144), F_BODY(42), MUTED, 60)
    if s.get("code"):
        code_panel(img, 72, y + 50, W - 144, s["code"], accent, y1 - y - 60)


def s_text(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (120 if tall else 0)
    if s.get("heading"):
        y = paste_heading(img, 72, y, s["heading"], F_HEAD(68), W - 144, lh=78) + 36
    bsize = 44 if tall else 42
    for para in str(s.get("body", "")).split("\n\n"):
        y = draw_lines(d, (72, y), wrap(d, para, F_BODY(bsize), W - 144), F_BODY(bsize), MUTED, int(bsize * 1.45)) + 28
    if s.get("highlight"):
        f = F_SEMI(40)
        lines = wrap(d, s["highlight"], f, W - 144 - 70)
        b1 = snap_base(y + 58, 0)                       # first baseline on a rule
        top, h = b1 - 50, (len(lines) - 1) * G + 80     # box hugs the text, edges between rules
        d.rounded_rectangle([72, top, W - 72, top + h], radius=10, fill=MARKER)
        d.rectangle([72, top, 80, top + h], fill=accent)
        for i, ln in enumerate(lines):
            d.text((72 + 36, b1 + i * G - asc(f)), ln, font=f, fill=INK)


def s_code(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (100 if tall else 0)
    if s.get("heading"):
        y = paste_heading(img, 72, y, s["heading"], F_HEAD(60), W - 144, lh=70) + 30
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
    y = y0 + (100 if tall else 0)
    if s.get("heading"):
        y = paste_heading(img, 72, y, s["heading"], F_HEAD(60), W - 144, lh=70) + 34
    pairs = ((s.get("left_title", "Old way"), s["left"], RED), (s.get("right_title", "New way"), s["right"], GREEN))
    cs = code_size_for([c for _, c, _ in pairs], W - 144, y, y1)
    for title, code, col in pairs:
        top, _ = grid_box(y + 66, 10)            # code box on the grid; label always 14 px above it
        pill(d, 72, top - 62, title, F_SEMI(28), (255, 255, 255), col)
        y = code_panel(img, 72, top, W - 144, code, accent, 9999, s.get("filename", "program.abap"), size=cs) + 34


def s_list(img, s, y0, y1, accent, tall):
    W = img.size[0]
    items = s.get("items", [])
    w = W - 144
    rows = [list_row_img(i, it, w, accent, col=list_col(items, w, 40, 34)) for i, it in enumerate(items, 1)]
    y = y0 + (110 if tall else 0)
    hy = y
    if s.get("heading"):
        him = heading_img(s["heading"], F_HEAD(64), w)
        hy = snap_base(y, him.info["base"])
        y = hy + him.size[1] + 24
    first = snap_base(y, rows[0].info["base"]) if rows else y
    need = sum(r.info["rows"] for r in rows)
    gap = 1 if need + len(rows) - 1 <= (y1 - first) // G else 0
    if first + (need + gap * (len(rows) - 1) - 1) * G > y1:
        return s_list_fit(img, s, y0, y1, accent, tall)
    if s.get("heading"):
        img.paste(him, (66, hy), him)
    yb = first
    for r in rows:
        img.paste(r, (72, yb), r)
        yb += (r.info["rows"] + gap) * G


def s_list_fit(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    items = s.get("items", [])

    def layout(k, draw):
        y = y0 + (110 if tall else 40)
        hs, ts, rs = int(64 * k), int(40 * k), int(34 * k)
        if s.get("heading"):
            n = len(wrap_marked(marked_tokens(s["heading"]), F_HEAD(hs), W - 144))
            if draw:
                hi = heading_img(s["heading"], F_HEAD(hs), W - 144)
                img.paste(hi, (66, y), hi)
            n = len(wrap_marked(marked_tokens(s["heading"]), head_font(hs)[0], W - 144))
            hs_lh = head_font(hs)[1]
            y += n * hs_lh + int(40 * k)
        for i, it in enumerate(items, 1):
            title, _, rest = str(it).partition(" - ")
            tl = wrap(d, title, F_SEMI(ts), W - 144 - 90)
            rl = wrap(d, rest, F_BODY(rs), W - 144 - 90) if rest else []
            if draw:
                d.text((72, y + 2), f"{i:02d}", font=F_MONO_B(int(34 * k)), fill=accent)
                draw_lines(d, (162, y), tl, F_SEMI(ts), WHITE, int(ts * 1.35), snap=False)
                if rl:
                    draw_lines(d, (162, y + len(tl) * int(ts * 1.35) + 4), rl, F_BODY(rs), MUTED, int(rs * 1.4), snap=False)
            y += len(tl) * int(ts * 1.35) + (len(rl) * int(rs * 1.4) + 4 if rl else 0) + int(30 * k)
        return y

    k = 1.0
    while k > 0.55 and layout(k, False) > y1:
        k -= 0.04
    layout(k, True)


def s_cta(img, s, y0, y1, accent, tall):
    d = ImageDraw.Draw(img)
    W = img.size[0]
    y = y0 + (260 if tall else 170)
    y = paste_heading(img, 72, y, s.get("title", "Save this post"), F_HEAD(88), W - 144, lh=96) + 40
    y = draw_lines(d, (72, y), wrap(d, s.get("body", ""), F_BODY(42), W - 144), F_BODY(42), MUTED, 60) + 8
    pf = F_SEMI(34)
    b = snap_base(y + 56, 0)
    for a in s.get("actions", ["Save", "Share with a friend", "Follow for daily ABAP"]):
        top = b - asc(pf) - 16
        d.rounded_rectangle([72, top, 72 + d.textlength(a, font=pf) + 52, top + asc(pf) + 32 + 8], radius=40,
                            fill=BG, outline=accent, width=3)
        d.text((72 + 26, b - asc(pf)), a, font=pf, fill=accent)
        b += 2 * G if len(s.get("actions", [1, 2, 3])) <= 3 else G + 32


KINDS = {"cover": s_cover, "text": s_text, "code": s_code, "compare": s_compare, "list": s_list, "cta": s_cta}


def render_slide(s, idx, total, handle, tag, accent, tall):
    W, H = (1080, 1920) if tall else (1080, 1350)
    img = Image.new("RGB", (W, H), BG)
    y0, y1 = chrome(img, handle, tag, idx, total, accent, tall)
    kind = s.get("kind", "text")
    if kind in NEW_KINDS or (kind == "cover" and s.get("style")):
        blocks = build_blocks(s, accent, y0, y1 if not tall else y1 - 120)
        content = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_blocks(content, blocks, 0, final=True)
        img.paste(content, (0, 0), content)
        return img
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
        off = round((max(y0, target_top) - top) / G) * G   # whole ruled lines only
        while top + off < y0 - 8:
            off += G
        if top + off + content_h > y1 + 12:
            OVERLAPS.append(f"{s.get('kind')}: content runs {top + off + content_h - y1}px into the footer - shorten it")
        crop = layer.crop((0, top, W, bottom))
        mask = ImageChops.difference(crop, Image.new("RGB", crop.size, BG)).convert("L").point(lambda v: 255 if v > 0 else 0)
        img.paste(crop, (0, top + off), mask)
    return img


TTS_DIR = os.environ.get("ABAP_TTS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts"))
_KOKORO = None


DEVANAGARI = re.compile(r"[\u0900-\u097F]")
LATIN = re.compile(r"[A-Za-z0-9]")
# How English acronyms / T-codes should be spoken (Latin text in a voiceover)
SAY = {"SAP": "S A P", "ALV": "A L V", "SQL": "sequel", "BAPI": "bappy", "ABAP": "aa baap", "IDoc": "I doc",
       "IDOC": "I doc", "CDS": "C D S", "RAP": "rap", "BDC": "B D C", "RFC": "R F C", "SE11": "S E eleven",
       "SE16N": "S E sixteen N", "SE37": "S E thirty seven", "SE38": "S E thirty eight", "SE80": "S E eighty",
       "SE91": "S E ninety one", "SE09": "S E zero nine", "SE19": "S E nineteen", "SE18": "S E eighteen",
       "ST22": "S T twenty two", "ST05": "S T zero five", "SM37": "S M thirty seven", "SM30": "S M thirty",
       "WE02": "W E zero two", "WE19": "W E nineteen", "BD87": "B D eighty seven", "F5": "F five",
       "F6": "F six", "F7": "F seven", "F8": "F eight", "VBAK": "V back", "VBAP": "V bap", "VBRK": "V B R K",
       "VBRP": "V B R P", "LIKP": "L I K P", "LIPS": "lips", "MARA": "mara", "EKKO": "E K K O",
       "EKPO": "E K P O", "KNA1": "K N A one", "BKPF": "B K P F", "BSEG": "B seg", "MSEG": "M seg",
       "OOPS": "oops", "HANA": "hana", "S/4HANA": "S four hana", "UI": "U I", "API": "A P I", "PDF": "P D F"}


def phonemize_mixed(text):
    """Hinglish: Devanagari words -> Hindi phonemes, Latin words -> English phonemes, one voice."""
    tok = _kokoro().tokenizer
    groups, cur, cur_l = [], [], None
    for w in str(text).split():
        core = re.sub(r"[^\w/\u0900-\u097F]", "", w)
        if core in SAY:
            w = w.replace(core, SAY[core])
        elif core.isupper() and len(core) >= 2 and not core.isalpha():
            pass
        l = "hi" if DEVANAGARI.search(w) else ("en-us" if LATIN.search(w) else (cur_l or "hi"))
        if cur and l != cur_l:
            groups.append((cur_l, " ".join(cur)))
            cur = []
        cur.append(w)
        cur_l = l
    if cur:
        groups.append((cur_l, " ".join(cur)))
    return " ".join(tok.phonemize(t, lang=l) for l, t in groups)


def _kokoro():
    global _KOKORO
    if _KOKORO is None:
        from kokoro_onnx import Kokoro
        _KOKORO = Kokoro(os.path.join(TTS_DIR, "kokoro-v1.0.onnx"), os.path.join(TTS_DIR, "voices-v1.0.bin"))
    return _KOKORO


def tts(text, voice, lang, speed, out_wav):
    """Kokoro TTS (pip install kokoro-onnx soundfile; model files in TTS_DIR). Returns seconds.
    Hinglish mode: Hindi words in Devanagari, English/technical words in Latin script."""
    import soundfile as sf
    k = _kokoro()
    if lang in ("hi", "en"):   # "en": English script, same SAY pronunciations for T-codes/acronyms
        samples, sr = k.create(phonemize_mixed(text), voice=voice, speed=speed, is_phonemes=True)
    else:
        samples, sr = k.create(text, voice=voice, speed=speed, lang=lang)
    sf.write(out_wav, samples, sr)
    return len(samples) / sr


VOICE_POLISH = "highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=60,deesser=i=0.5:m=0.5:f=0.45"   # de-esser after compression (12 Nov)


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


def tighten_audio(data, sr, max_gap=0.2, thresh=0.012):
    """Trim silence at both ends and shorten pauses inside a TTS clip to at most max_gap seconds."""
    import numpy as np
    if len(data) == 0:
        return data
    hop = int(0.01 * sr)
    n = len(data) // hop
    if n < 3:
        return data
    env = np.abs(data[: n * hop]).reshape(n, hop).max(axis=1)
    loud = env > thresh
    idx = np.flatnonzero(loud)
    if len(idx) == 0:
        return data
    first, last = max(0, idx[0] - 2), min(n, idx[-1] + 4)
    keep, gap = [], int(max_gap / 0.01)
    run = 0
    for f in range(first, last):
        if loud[f]:
            run = 0
            keep.append(f)
        else:
            run += 1
            if run <= gap:
                keep.append(f)
    out = np.concatenate([data[f * hop:(f + 1) * hop] for f in keep])
    fade = min(len(out), int(0.006 * sr))
    if fade:
        out[:fade] *= np.linspace(0, 1, fade, dtype=out.dtype)
        out[-fade:] *= np.linspace(1, 0, fade, dtype=out.dtype)
    return out


def build_narration(slides, folder, p, default_secs):
    """Synthesize one clip per slide that has 'voiceover'. Returns (durations, wav path or None)."""
    voice = p.get("voice", "am_michael")
    lang = p.get("voice_lang", "hi")
    speed = float(p.get("voice_speed", 1.0))
    if not any(s.get("voiceover") for s in slides):
        return [default_secs] * len(slides), None, [(0.2, default_secs - 0.6)] * len(slides)
    import numpy as np
    import soundfile as sf
    pieces, durations, speech, sr = [], [], [], 24000
    lead, tail = p.get("_lead", 0.35), p.get("_tail", 0.45)  # silence before / after each line
    for i, s in enumerate(slides, 1):
        text = s.get("voiceover", "").strip()
        if text:
            wav = os.path.join(folder, f"vo_{i:02d}.wav")
            secs = tts(text, voice, lang, speed, wav)
            data, sr = sf.read(wav, dtype="float32")
            os.remove(wav)
            if p.get("_tighten"):
                data = tighten_audio(data, sr)
                secs = len(data) / sr
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
    raw = os.path.join(folder, "voiceover_raw.wav")
    out = os.path.join(folder, "voiceover.wav")
    sf.write(raw, full, sr)
    # broadcast-style polish: rumble cut, presence lift, gentle compression
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", VOICE_POLISH, "-ar", str(sr), out], check=True)
    os.remove(raw)
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
    spacing = grid_spacing(spacing)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = w or int(max((d0.textlength(l, font=font) for l in lines), default=1)) + 4
    h = spacing * (len(lines) - 1) + int(font.size * 1.3)
    im = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 0
    for ln in lines:
        d.text((0, y), ln, font=font, fill=fill)
        y += spacing
    if spacing == G or len(lines) == 1:
        im.info["base"] = asc(font)
    return im


class Blocks:
    def __init__(self):
        self.items = []

    def add(self, img, x, y, anim="up", pause=0.22, sfx=None, **extra):
        if "base" in getattr(img, "info", {}) and not extra.get("decor") and extra.get("until") is None \
                and not extra.get("nosnap"):
            y = snap_base(y, img.info["base"])
        b = {"img": img, "x": x, "y": y, "anim": anim, "pause": pause, "sfx": sfx}
        b.update(extra)
        self.items.append(b)
        return y + img.size[1]

    def overlay(self, fn, x, y, w, h, pause=0.2, dur=0.6, sfx="scratch", **extra):
        """Procedural drawing (circle, arrow, strike...) drawn progressively. fn(img, p, ox, oy)."""
        return self.add(Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0)), x, y, "overlay",
                        pause, sfx, overlay=fn, dur=dur, **extra)


def _code_blocks(B, x, y, w, code, accent, max_h, filename, typewriter=False, size=None):
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = code.rstrip("\n").split("\n")
    fixed = size
    size = fixed or 32
    while size > 20 and not fixed:
        f = F_MONO(size)
        longest = max((d0.textlength(l, font=f) for l in lines), default=0)
        if longest <= w - 64 and grid_box(0, 70 + len(lines) * int(size * 1.6) + 40)[1] + 16 <= max_h:
            break
        size -= 1
    f = F_MONO(size)
    lh = int(size * 1.6)
    h0 = 70 + len(lines) * lh + 40
    y, h = grid_box(y, h0)
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=22, fill=PANEL + (255,), outline=BORDER + (255,), width=2)
    d.rounded_rectangle([0, 0, w - 1, 64], radius=22, fill=PANEL_TOP + (255,))
    d.rectangle([0, 40, w - 1, 64], fill=PANEL_TOP + (255,))
    d.line([0, 64, w, 64], fill=BORDER + (255,), width=2)
    for i in range(3):
        cx = 34 + i * 30
        d.ellipse([cx - 8, 24, cx + 8, 40], fill=(205, 197, 182, 255))
    d.text((130, 18), filename, font=F_MONO(24), fill=DIM)
    B.add(frame, x, y, "up", 0.25, "pop", container=True)
    cy = y + 64 + 26 + (h - h0) // 2
    geo = {"x": x, "w": w, "lh": lh, "lines": [], "font": f}
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
                    col = NUM
                else:
                    col = CODE_INK
                dd.text((cx, 0), tok, font=f, fill=col)
                cx += dd.textlength(tok, font=f)
        geo["lines"].append((cy, lw))
        if ln.strip():
            if typewriter:
                B.add(im, x + 32, cy, "typec", 0.0, "tick", dur=max(0.25, len(ln.strip()) * 0.035))
            else:
                B.add(im, x + 32, cy, "type", 0.0)
        cy += lh
    B.last_code = geo
    return y + h


def build_blocks(s, accent, top_z=None, bottom_z=None):
    B = Blocks()
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    W = REEL_W
    x, w = 72, W - 144
    TOPZ = CONTENT_TOP if top_z is None else top_z
    BOTZ = CONTENT_BOTTOM if bottom_z is None else bottom_z
    kind = s.get("kind", "text")
    y = 0
    if kind in NEW_KINDS or (kind == "cover" and s.get("style")):
        build_new_kind(B, s, accent, x, w, BOTZ - TOPZ)
    elif kind == "cover":
        if s.get("kicker"):
            y = B.add(text_img([s["kicker"]], F_HAND(64), accent, 70), x, y, "up") + 24
        hf, hlh = head_font(s.get("title_size", 108))
        lines = wrap_marked(marked_tokens(s["title"]), hf, w)
        if len(lines) > 4:
            hf, hlh = head_font(64)
            lines = wrap_marked(marked_tokens(s["title"]), hf, w)
        for ln in lines:  # each title line pops separately = kinetic typography
            B.add(line_img(ln, hf), x - 6, y, "pop", 0.16, "pop")
            y = B.items[-1]["y"] + hlh          # next line exactly one title pitch lower
        y += 8
        if s.get("subtitle"):
            y = B.add(text_img(wrap(d0, s["subtitle"], F_BODY(44), w), F_BODY(44), MUTED, 62, w), x, y, "up")
        if s.get("code"):
            _code_blocks(B, x, y + 50, w, s["code"], accent, BOTZ - TOPZ - y - 60, "program.abap")
    elif kind == "text":
        if s.get("heading"):
            y = B.add(heading_img(s["heading"], F_HEAD(72), w, lh=82), x - 6, y, "up") + 40
        for para in str(s.get("body", "")).split("\n\n"):
            y = B.add(text_img(wrap(d0, para, F_BODY(46), w), F_BODY(46), MUTED, 66, w), x, y, "up", 0.35) + 30
        if s.get("highlight"):
            hf = F_SEMI(44)
            hl = wrap(d0, s["highlight"], hf, w - 72)
            b1 = snap_base(y + 60, 0)
            top, h = b1 - 54, (len(hl) - 1) * G + 88
            box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            dd = ImageDraw.Draw(box)
            dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=MARKER + (255,))
            dd.rectangle([0, 0, 9, h - 1], fill=accent + (255,))
            for i, ln in enumerate(hl):
                dd.text((36, 54 + i * G - asc(hf)), ln, font=hf, fill=INK)
            y = B.add(box, x, top, "pop", 0.3, "pop")
    elif kind == "code":
        if s.get("heading"):
            y = B.add(heading_img(s["heading"], F_HEAD(64), w, lh=74), x - 6, y, "up") + 34
        note_h = 0
        if s.get("note"):
            note_lines = wrap(d0, s["note"], F_BODY(40), w)
            note_h = len(note_lines) * 56 + 40
        y = _code_blocks(B, x, y, w, s["code"], accent, BOTZ - TOPZ - y - note_h, s.get("filename", "program.abap"),
                         typewriter=bool(s.get("typewriter")))
        if s.get("spotlight") is not None:
            add_spotlight(B, B.last_code, s["spotlight"])
        if s.get("note"):
            B.add(text_img(note_lines, F_BODY(40), MUTED, 56, w), x, y + 36, "up", 0.3)
    elif kind == "compare":
        if s.get("heading"):
            y = B.add(heading_img(s["heading"], F_HEAD(64), w, lh=74), x - 6, y, "up") + 34
        pairs = ((s.get("left_title", "Old way"), s["left"], RED), (s.get("right_title", "New way"), s["right"], GREEN))
        cs = code_size_for([c for _, c, _ in pairs], w, y, BOTZ - TOPZ)
        for title, code, col in pairs:
            avail = 9999
            tw = int(d0.textlength(title, font=F_SEMI(30))) + 40
            p = Image.new("RGBA", (tw, 52), (0, 0, 0, 0))
            ImageDraw.Draw(p).rounded_rectangle([0, 0, tw - 1, 51], radius=10, fill=col + (255,))
            ImageDraw.Draw(p).text((20, 9), title, font=F_SEMI(30), fill=(255, 255, 255))
            top, _ = grid_box(y + 66, 10)
            B.add(p, x, top - 66, "pop", 0.2, "pop")
            y = _code_blocks(B, x, top, w, code, accent, avail - 66, s.get("filename", "program.abap"), size=cs) + 34
    elif kind == "list":
        if s.get("heading"):
            y = B.add(heading_img(s["heading"], F_HEAD(66), w, lh=76), x - 6, y, "up") + 40
        its = s.get("items", [])
        rows = [list_row_img(i, it, w, accent, 42, 36, col=list_col(its, w, 42, 36))
                for i, it in enumerate(its, int(s.get("start", 1)))]
        need = sum(r.info["rows"] for r in rows) + len(rows) - 1
        gap = G if (need + 3) * G <= BOTZ - TOPZ - y else 0
        for r in rows:
            y = B.add(r, x, y, "up", 0.45) + gap
    elif kind == "cta":
        y = B.add(heading_img(s.get("title", "Save this post"), F_HEAD(92), w, lh=100), x - 6, y, "pop", 0.3, "pop") + 40
        y = B.add(text_img(wrap(d0, s.get("body", ""), F_BODY(44), w), F_BODY(44), MUTED, 62, w), x, y, "up") + 60
        for a in s.get("actions", ["Save", "Share", "Follow"]):
            tw = int(d0.textlength(a, font=F_SEMI(38))) + 64
            pimg = Image.new("RGBA", (tw, 80), (0, 0, 0, 0))
            dd = ImageDraw.Draw(pimg)
            dd.rounded_rectangle([0, 0, tw - 1, 79], radius=40, fill=BG + (255,), outline=accent + (255,), width=3)
            dd.text((32, 17), a, font=F_SEMI(38), fill=accent)
            y = B.add(pimg, x, y, "pop", 0.28, "pop") + 24
    check_overlaps(B.items, s)
    # centre vertically inside the content zone
    top = min(b["y"] for b in B.items)
    bottom = max(b["y"] + b["img"].size[1] for b in B.items)
    off = TOPZ + max(0, ((BOTZ - TOPZ) - (bottom - top)) // 2) - top
    off = (off // G) * G                          # move in whole ruled lines: baselines stay on rules
    while top + off < TOPZ - 8 and bottom + off + G <= BOTZ + 8:
        off += G
    if bottom + off > BOTZ + 12:
        OVERLAPS.append(f"{s.get('kind')}: content runs {bottom + off - BOTZ}px past the bottom of the "
                        f"content area (into captions/footer) - shorten it")
    for b in B.items:
        b["y"] += off
    return B.items


OVERLAPS = []


def _opaque_box(b):
    """Bounding box of the visible pixels of a block, in layout coordinates."""
    bb = b["img"].getchannel("A").getbbox() if b["img"].mode == "RGBA" else (0, 0) + b["img"].size
    if not bb:
        return None
    return (b["x"] + bb[0], b["y"] + bb[1], b["x"] + bb[2], b["y"] + bb[3])


def check_overlaps(items, s):
    """Record text blocks that collide (overlays, containers, decorations and timed blocks are exempt)."""
    solid = [(i, _opaque_box(b)) for i, b in enumerate(items)
             if b["anim"] != "overlay" and not b.get("container") and not b.get("decor") and b.get("until") is None]
    solid = [(i, r) for i, r in solid if r]
    for a in range(len(solid)):
        for c in range(a + 1, len(solid)):
            (_, r1), (_, r2) = solid[a], solid[c]
            ix = min(r1[2], r2[2]) - max(r1[0], r2[0])
            iy = min(r1[3], r2[3]) - max(r1[1], r2[1])
            if ix > 8 and iy > 8:
                OVERLAPS.append(f"slide kind={s.get('kind')} title={str(s.get('title') or s.get('heading') or s.get('question') or '')[:40]!r}: blocks overlap by {ix}x{iy}px")
                return


def schedule_blocks(blocks, speech_start, speech_len, pace_k=1.0, scene_dur=None):
    """Give every block an appear time. Code lines type in across the narration."""
    t = 0.12
    n_type = sum(1 for b in blocks if b["anim"] in ("type", "typec"))
    type_step = 0.1
    if n_type:
        type_step = min(0.45, max(0.09, (speech_len * 0.6) / n_type))
    for b in blocks:
        b["t"] = t
        if b["anim"] == "type":
            t += type_step
        elif b["anim"] == "typec":
            t += max(type_step, b.get("dur", 0.3) + 0.05)
        else:
            t += b["pause"] * pace_k
    # short scenes: compress the whole choreography so it finishes before the cut
    if scene_dur:
        def end_of(b):
            return b["t"] + (b.get("dur") or ANIM_DUR.get(b["anim"], 0.5))
        end = max((end_of(b) for b in blocks if b.get("until") is None), default=0)
        limit = scene_dur * 0.8
        if end > limit > 0:
            k = limit / end
            for b in blocks:
                b["t"] *= k
                if b.get("dur"):
                    b["dur"] *= k
                if b.get("until") is not None:
                    b["until"] *= k
    return blocks


def reel_chrome(handle, tag, accent):
    img = Image.new("RGB", (REEL_W, REEL_H), BG)
    paper(img)
    d = ImageDraw.Draw(img)
    pill(d, 72, 150, tag.upper(), F_MONO_B(28), (255, 255, 255), accent)
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
                        fill=INK + (int(235 * p),))
    for (w_, t0, t1), ww in zip(cur, widths):
        active = t0 <= tau < t1 + 0.05
        col = MARKER if active else (255, 255, 255)
        if tau < t0:
            col = (170, 176, 190)
        d.text((x, SUB_Y - 38), w_, font=f, fill=col)
        x += ww + gap


ANIM_DUR = {"type": 0.18, "stamp": 0.28, "draw": 0.5, "overlay": 0.6, "slide": 0.45, "fade": 0.4}


def _alpha(im, a):
    if a >= 1:
        return im
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v, a=a: int(v * a)))
    return im


def draw_blocks(content, blocks, tau, final=False):
    """Composite blocks onto an RGBA canvas at time tau (final=True: end state, for static slides)."""
    for b in blocks:
        if final:
            if b.get("until") is not None:
                continue
            p = 1.0
        else:
            dur_b = b.get("dur") or ANIM_DUR.get(b["anim"], 0.5)
            p = (tau - b["t"]) / dur_b
            if p <= 0:
                continue
            p = min(1.0, p)
            if b.get("until") is not None:
                left = b["t"] + b["until"] - tau
                if left <= 0:
                    continue
                if left < 0.15:
                    b = dict(b, img=_alpha(b["img"], left / 0.15))
        im = b["img"]
        x, y = b["x"], b["y"]
        a = b["anim"]
        if a == "overlay":
            b["overlay"](content, ease_out(p), x, y)
            continue
        if a == "type":
            e = ease_out(p)
            im = _alpha(im, e)
            x = int(x - (1 - e) * 24)
        elif a == "typec":
            # typewriter: reveal left -> right with a cursor
            wv = max(1, int(im.size[0] * p))
            if p < 1:
                im = im.crop((0, 0, wv, im.size[1]))
            content.alpha_composite(im, (int(x), int(y)))
            if p < 1 or (not final and int(tau * 2.5) % 2 == 0 and tau - b["t"] < b.get("dur", 0.3) + 0.6):
                d = ImageDraw.Draw(content)
                d.rectangle([x + wv + 2, y + 4, x + wv + 6, y + im.size[1] - 8], fill=SAP_BLUE + (255,))
            continue
        elif a == "pop":
            e = ease_back(p)
            sc = 0.86 + 0.14 * e
            if p < 1:
                w0, h0 = im.size
                im = im.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.BILINEAR)
                im = _alpha(im, min(1.0, p * 2.2))
                y = int(y + (h0 - im.size[1]) / 2)
        elif a == "stamp":
            e = ease_out(p)
            sc = 1.6 - 0.6 * e
            if p < 1:
                w0, h0 = im.size
                im = im.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.BILINEAR)
                im = _alpha(im, min(1.0, p * 3))
                x = int(x + (w0 - im.size[0]) / 2)
                y = int(y + (h0 - im.size[1]) / 2)
        elif a == "draw":
            if p < 1:
                im = im.crop((0, 0, max(1, int(im.size[0] * ease_out(p))), im.size[1]))
        elif a == "slide":
            e = ease_out(p)
            im = _alpha(im, e)
            x = int(x + (1 - e) * 140)
        elif a == "fade":
            im = _alpha(im, ease_out(p))
        else:  # "up"
            # follow-through (12 Nov): rise, overshoot ~5 px once, settle (ease_back on position, ease_out on opacity)
            im = _alpha(im, ease_out(p))
            y = int(round(y + (1 - ease_back(p)) * 46))
        content.alpha_composite(im, (int(x), int(y)))


def render_scene(base, blocks, tau, dur, sub_tl, accent, push=0.04, beat=0.0, stamp=None):
    content = Image.new("RGBA", (REEL_W, REEL_H), (0, 0, 0, 0))
    draw_blocks(content, blocks, tau)
    # slow camera push on the content
    z = 1.0 + push * ease_out(min(1.0, tau / max(dur, 0.1)))
    # "beat" punch-ins: on long scenes, a quick 1.5% step-zoom every `beat` seconds (a visual change every 2-3 s)
    # beats: list of times (keyword spoken / every ~2.6 s), each a quick 1.5% punch-in; or a number = interval
    times = beat if isinstance(beat, (list, tuple)) else []
    if not times and beat and dur > beat + 0.8:
        t = beat
        while t < dur - 0.6:
            times.append(t)
            t += beat
    if times:
        z += 0.015 * sum(ease_out(min(1.0, max(0.0, (tau - t) / 0.22))) for t in times)
    if z > 1.001:
        zw, zh = int(REEL_W * z), int(REEL_H * z)
        content = content.resize((zw, zh), Image.BILINEAR)
        cx, cy = (zw - REEL_W) // 2, int((zh - REEL_H) * 0.42)
        content = content.crop((cx, cy, cx + REEL_W, cy + REEL_H))
    frame = base.copy()
    frame.paste(content, (0, 0), content)
    if stamp is not None:   # mid-reel re-hook stamp, pops in under the header
        img, t0 = stamp
        if tau >= t0:
            a = min(1.0, (tau - t0) / 0.18)
            sc = 1.0 + 0.35 * (1 - ease_out(a))
            im = img.resize((max(1, int(img.size[0] * sc)), max(1, int(img.size[1] * sc))), Image.BICUBIC)
            x = REEL_W - 72 - img.size[0] - (im.size[0] - img.size[0]) // 2
            y = 214 - (im.size[1] - img.size[1]) // 2
            frame.paste(im, (x, y), im)
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
    if kind == "stamp":
        n = int(0.22 * sr)
        t = np.arange(n) / sr
        thud = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 22) * 0.5
        click = np.random.default_rng(3).standard_normal(n) * np.exp(-t * 160) * 0.18
        return (thud + click).astype("float32")
    if kind == "tick":
        n = int(0.04 * sr)
        t = np.arange(n) / sr
        return (np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 180) * 0.09).astype("float32")
    if kind == "scratch":
        n = int(0.32 * sr)
        noise = np.random.default_rng(11).standard_normal(n).astype("float32")
        hp = noise - np.convolve(noise, np.ones(6) / 6, mode="same")
        env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
        return (hp * env * 0.06).astype("float32")
    n = int(0.09 * sr)
    t = np.arange(n) / sr
    freq = 900 * np.exp(-t * 28) + 260
    phase = 2 * np.pi * np.cumsum(freq) / sr
    return (np.sin(phase) * np.exp(-t * 55) * 0.16).astype("float32")


TRANSITIONS = ["rise", "slide", "zoom", "rise"]   # rotated cut by cut; a post may set "transitions"
HEADER_H = 230   # tag + handle + progress bar stay fixed during transitions


def apply_transition(kind, prev, nxt, base, p):
    """Blend outgoing frame `prev` into incoming `nxt`; p goes 0 -> 1."""
    e = ease_out(min(1.0, max(0.0, p)))
    W, H = nxt.size
    if kind == "slide":
        # page push: content slides left, header stays put
        out = base.copy()
        body_prev = prev.crop((0, HEADER_H, W, H))
        body_next = nxt.crop((0, HEADER_H, W, H))
        dx = int(W * e)
        out.paste(body_prev, (-dx, HEADER_H))
        out.paste(body_next, (W - dx, HEADER_H))
        return out
    if kind == "zoom":
        # incoming scene settles from a slight zoom while fading in; header stays fixed
        sc = 1.06 - 0.06 * e
        body = nxt.crop((0, HEADER_H, W, H))
        bw, bh = body.size
        zw, zh = int(bw * sc), int(bh * sc)
        zb = body.resize((zw, zh), Image.BILINEAR).crop(((zw - bw) // 2, (zh - bh) // 2, (zw - bw) // 2 + bw, (zh - bh) // 2 + bh))
        z = nxt.copy()
        z.paste(zb, (0, HEADER_H))
        out = Image.blend(prev, z, e)
        out.paste(base.crop((0, 0, W, HEADER_H)), (0, 0))
        return out
    if kind == "whip":
        # fast whip-pan with motion blur, header fixed
        from PIL import ImageFilter
        out = base.copy()
        dx = int(W * e)
        blur = int(30 * (1 - abs(2 * e - 1))) + 1
        body_prev = prev.crop((0, HEADER_H, W, H)).filter(ImageFilter.BoxBlur(blur))
        body_next = nxt.crop((0, HEADER_H, W, H)).filter(ImageFilter.BoxBlur(blur))
        out.paste(body_prev, (-dx, HEADER_H))
        out.paste(body_next, (W - dx, HEADER_H))
        return out
    if kind == "flip":
        # page flip: body squashes to a line, then the next page opens
        out = base.copy()
        src = prev if e < 0.5 else nxt
        k = abs(1 - 2 * e)
        bh = H - HEADER_H
        nh = max(2, int(bh * k))
        body = src.crop((0, HEADER_H, W, H)).resize((W, nh), Image.BILINEAR)
        out.paste(body, (0, HEADER_H + (bh - nh) // 2))
        return out
    if kind == "wipe":
        # highlighter wipe: a yellow band sweeps left -> right revealing the next scene
        out = prev.copy()
        edge = int((W + 160) * e) - 80
        if edge > 0:
            out.paste(nxt.crop((0, HEADER_H, min(W, edge), H)), (0, HEADER_H))
        d = ImageDraw.Draw(out)
        d.rectangle([edge - 30, HEADER_H, edge + 50, H], fill=MARKER)
        return out
    # "rise": outgoing scene drifts up while fading
    prev = prev.transform(prev.size, Image.AFFINE, (1, 0, 0, 0, 1, int(60 * e)), fillcolor=BG)
    return Image.blend(prev, nxt, e)


def make_motion_reel(p, slides, folder, handle, accent):
    import numpy as np
    import soundfile as sf
    default = float(p.get("seconds_per_slide", 3.5))
    fmt = FORMATS.get(p.get("format", ""), {})
    # approved 12 Nov: the research-based "snappy" pace is the default for every reel (old "fast"/"calm" only if set explicitly)
    pace = PACES.get(p.get("pace") or "snappy", PACES["snappy"])
    p = dict(p)
    p.setdefault("voice_speed", pace["voice_speed"])
    p["voice_speed"] = p.get("voice_speed_override", pace["voice_speed"])
    p["_lead"], p["_tail"] = pace["lead"], pace["tail"]
    p["_tighten"] = pace.get("tighten", False)
    has_vo = any(s.get("voiceover") for s in slides)
    if has_vo:
        durations, vo_wav, speech = build_narration(slides, folder, p, default)
        dmin, dmax = (COURSE_MIN, COURSE_MAX) if p.get("series") == "course" else (REEL_MIN, REEL_MAX)
        rmin, rmax = float(p.get("min_len", dmin)), float(p.get("max_len", dmax))
        for _ in range(2):   # slightly long? speed the voice up (max +15%) and re-synthesize
            total0 = sum(durations)
            if total0 <= rmax:
                break
            f = total0 / rmax
            if p["voice_speed"] * f > pace["voice_speed"] * 1.15:
                break
            p["voice_speed"] = round(p["voice_speed"] * f * 1.02, 3)
            durations, vo_wav, speech = build_narration(slides, folder, p, default)
        if sum(durations) < rmin:   # short? hold the last frame longer
            durations[-1] += rmin - sum(durations)
        if sum(durations) > rmax + 0.5:
            msg = f"WARNING: reel is {sum(durations):.1f}s (target {rmin:.0f}-{rmax:.0f}s). Shorten the voiceover."
            print(msg)
            with open(os.path.join(folder, "LENGTH_WARNING.txt"), "w") as fh:
                fh.write(msg + "\n")
        voice, sr = sf.read(vo_wav, dtype="float32")
    else:
        durations, speech, sr = [default] * len(slides), [(0.2, default - 0.6)] * len(slides), 24000
        voice = np.zeros(int(sum(durations) * sr), dtype="float32")
    base = reel_chrome(handle, p.get("tag", "SAP ABAP"), accent)
    scenes = []
    for s, dur, (st, ln) in zip(slides, durations, speech):
        blocks = schedule_blocks(build_blocks(s, accent), st, ln, pace["pause_k"], dur)
        sub = s.get("spoken") or s.get("voiceover") or ""   # subtitles always on
        tl = word_timeline(sub, st, ln) if (sub and ln > 0) else []
        scenes.append((blocks, dur, tl))
    starts = [sum(durations[:i]) for i in range(len(durations))]
    total = sum(durations)

    # ---- visual beats (approved 12 Nov): something changes every 2-3 s
    READ_KINDS = {"code", "screen", "compare", "table", "bug"}
    beat_iv = pace.get("beat", 0.0)
    scene_beats = []
    for s, dur, (st, ln) in zip(slides, durations, speech):
        bt = []
        if beat_iv and s.get("kind") not in READ_KINDS:
            # punch exactly when a *highlighted* word of the title/heading is spoken
            vo = (s.get("voiceover") or "").lower()
            for word in re.findall(r"\*([^*]+)\*", (s.get("title") or "") + " " + (s.get("heading") or "")):
                pos = vo.find(word.lower().split()[0]) if word.split() else -1
                if pos >= 0 and ln > 0 and len(vo):
                    bt.append(st + ln * pos / len(vo))
            # fill gaps so there is a visual change at least every ~beat_iv seconds
            t = beat_iv
            while t < dur - 0.6:
                if all(abs(t - b) > 1.2 for b in bt):
                    bt.append(t)
                t += beat_iv
            bt = sorted(b for b in bt if 0.5 < b < dur - 0.4)
        scene_beats.append(bt)

    # ---- mid-reel re-hook stamp for reels over ~20 s
    rehook = p.get("rehook")
    stamps = [None] * len(slides)
    if rehook is not False and total > 20 and len(slides) >= 4:
        mid = total * 0.45
        cand = [i for i in range(1, len(slides) - 1) if slides[i].get("kind") != "cta"]
        if isinstance(rehook, dict) and isinstance(rehook.get("slide"), int):
            idx = rehook["slide"]
        elif cand:
            idx = min(cand, key=lambda i: abs(starts[i] - mid))
        else:
            idx = None
        if idx is not None and 0 <= idx < len(slides):
            text = (rehook.get("stamp") if isinstance(rehook, dict) else None) or \
                   ("Remember this" if p.get("series") == "course" else "Watch this")
            stamps[idx] = (_stamp(text, EMPH_RED, 40), 0.25)

    # ---- audio: voice + sfx, loudness-normalised later by ffmpeg
    mix = np.zeros(int(total * sr) + sr, dtype="float32")
    mix[: len(voice)] += voice
    whoosh = synth_sfx("whoosh", sr)
    sfx_bank = {k: synth_sfx(k, sr) for k in ("pop", "stamp", "tick", "scratch")}
    use_whoosh = bool(p.get("whoosh", False))   # transition whoosh removed by default (sounded odd)
    for i, st0 in enumerate(starts):
        if stamps[i] is not None:
            snd = sfx_bank["stamp"]
            a = int((st0 + stamps[i][1]) * sr)
            mix[a:a + len(snd)] += snd[: max(0, len(mix) - a)]
        if i > 0 and use_whoosh:
            a = max(0, int((st0 - 0.2) * sr))
            mix[a:a + len(whoosh)] += whoosh[: len(mix) - a]
        for b in scenes[i][0]:
            snd = sfx_bank.get(b.get("sfx") or "")
            if snd is not None and b["t"] < durations[i]:
                a = int((st0 + b["t"]) * sr)
                mix[a:a + len(snd)] += snd[: max(0, len(mix) - a)]
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
    trans = pace["trans"]
    transitions = p.get("transitions") or fmt.get("transitions") or TRANSITIONS
    n_frames = int(total * FPS)
    last_small, static_run, worst_static = None, 0.0, 0.0
    for fi in range(n_frames):
        t = fi / FPS
        i = max(k for k, st0 in enumerate(starts) if st0 <= t + 1e-9)
        tau = t - starts[i]
        blocks, dur, tl = scenes[i]
        frame = render_scene(base, blocks, tau, dur, tl, accent, pace["push"], scene_beats[i], stamps[i])
        kind_t = transitions[(i - 1) % len(transitions)] if i > 0 else None
        tlen = trans + (0.1 if kind_t in ("slide", "zoom", "flip", "wipe") else 0)
        if kind_t == "whip":
            tlen = 0.28
        if i > 0 and tau < tlen:
            pb, pd, ptl = scenes[i - 1]
            prev = render_scene(base, pb, pd + tau, pd, ptl, accent, pace["push"], scene_beats[i - 1], stamps[i - 1])
            frame = apply_transition(kind_t, prev, frame, base, tau / tlen)
        # progress bar
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([72, 100, REEL_W - 72, 106], radius=3, fill=BORDER)
        d.rounded_rectangle([72, 100, 72 + int((REEL_W - 144) * (t / total)), 106], radius=3, fill=accent)
        proc.stdin.write(frame.tobytes())
        if fi % 15 == 0:   # static-hold check: sample every 0.5 s
            small = np.asarray(frame.convert("L").resize((108, 192)), dtype=np.int16)
            if last_small is not None:
                changed = (np.abs(small - last_small) > 12).mean()
                static_run = static_run + 0.5 if changed < 0.0015 else 0.0
                worst_static = max(worst_static, static_run)
            last_small = small
        if fi == int((starts[i] + dur * 0.9) * FPS):
            frame.save(os.path.join(folder, f"frame_{i + 1:02d}.png"), optimize=True)
    proc.stdin.close()
    proc.wait()
    if worst_static > 3.0:
        OVERLAPS.append(f"STATIC: the picture barely changes for {worst_static:.1f}s in {p.get('slug')} "
                        f"- add a reveal/highlight/outline in that scene (rule: a visible change every 3 s)")
    for f_ in (mix_wav, os.path.join(folder, "voiceover.wav")):
        if os.path.exists(f_):
            os.remove(f_)
    return out_mp4


# =====================================================================
# Phase 1 formats: drawn emphasis, new slide kinds, recipes
# =====================================================================
EMPH_RED = (214, 64, 52)


def _hand_ellipse(d, box, p, color, width=6):
    """Hand-drawn ellipse that draws itself (p 0->1); two slightly offset strokes."""
    x0, y0, x1, y1 = box
    sweep = 380 * p
    if sweep <= 1:
        return
    d.arc([x0, y0, x1, y1], start=200, end=200 + sweep, fill=color, width=width)
    if p > 0.5:
        d.arc([x0 - 4, y0 + 3, x1 + 3, y1 - 2], start=210, end=210 + (sweep - 190), fill=color, width=max(2, width - 3))


def _hand_line(d, x0, y0, x1, y1, p, color, width=6, head=False):
    xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    d.line([x0, y0, xe, ye], fill=color, width=width)
    if head and p > 0.85:
        import math
        ang = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            d.line([x1, y1, x1 + 34 * math.cos(ang + da), y1 + 34 * math.sin(ang + da)], fill=color, width=width)


def ov_circle(w, h, color=EMPH_RED, pad=14):
    def fn(img, p, ox, oy):
        _hand_ellipse(ImageDraw.Draw(img), [ox - pad, oy - pad, ox + w + pad, oy + h + pad], p, color + (255,))
    return fn


def ov_box(w, h, color=GREEN, pad=8, width=7):
    """Hand-drawn outline around a card, drawn clockwise as p goes 0 -> 1 (never covers the text)."""
    def fn(img, p, ox, oy):
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = ox - pad, oy - pad, ox + w + pad, oy + h + pad
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        seg = [abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1]) for i in range(4)]
        left = sum(seg) * p
        for i in range(4):
            if left <= 0:
                break
            f = min(1.0, left / seg[i])
            a, b = pts[i], pts[i + 1]
            d.line([a, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)], fill=color + (255,), width=width)
            left -= seg[i]
    return fn


def ov_strike(w, h, color=EMPH_RED):
    def fn(img, p, ox, oy):
        d = ImageDraw.Draw(img)
        _hand_line(d, ox - 6, oy + h * 0.55, ox + w + 6, oy + h * 0.45, p, color + (255,), 7)
    return fn


def ov_arrow(x0, y0, x1, y1, color=EMPH_RED):
    """Arrow from (x0,y0) to (x1,y1), coordinates relative to the overlay origin."""
    def fn(img, p, ox, oy):
        _hand_line(ImageDraw.Draw(img), ox + x0, oy + y0, ox + x1, oy + y1, p, color + (255,), 6, head=True)
    return fn


def ov_tick(size, color=GREEN):
    def fn(img, p, ox, oy):
        d = ImageDraw.Draw(img)
        a = (ox + size * 0.15, oy + size * 0.55)
        b = (ox + size * 0.42, oy + size * 0.82)
        c = (ox + size * 0.9, oy + size * 0.18)
        if p < 0.4:
            q = p / 0.4
            d.line([a, (a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q)], fill=color + (255,), width=8)
        else:
            q = (p - 0.4) / 0.6
            d.line([a, b], fill=color + (255,), width=8)
            d.line([b, (b[0] + (c[0] - b[0]) * q, b[1] + (c[1] - b[1]) * q)], fill=color + (255,), width=8)
    return fn


def add_spotlight(B, geo, idx):
    """Dim every code line except `idx` (int or list) once the code has typed in."""
    keep = set(idx if isinstance(idx, list) else [idx])
    lines, lh, x, w = geo["lines"], geo["lh"], geo["x"], geo["w"]
    y_first = lines[0][0] if lines else 0
    total_h = (lines[-1][0] - y_first + lh) if lines else 1

    def fn(img, p, ox, oy):
        d = ImageDraw.Draw(img)
        for i, (ly, _) in enumerate(lines):
            if i in keep:
                continue
            yy = oy + (ly - y_first)
            d.rectangle([ox + 20, yy - 2, ox + w - 20, yy + lh - 6], fill=PANEL + (int(135 * p),))
    B.overlay(fn, x, y_first, w, total_h, pause=0.3, dur=0.5, sfx=None)


def _card(w, lines, font, fill=INK, bg=PANEL, border=BORDER, pad=30, lh=None, radius=18):
    lh = lh or int(font.size * 1.35)
    h = pad * 2 + lh * len(lines) - int(font.size * 0.25)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=bg + (255,), outline=border + (255,), width=3)
    y = pad
    for ln in lines:
        d.text((pad, y), ln, font=font, fill=fill)
        y += lh
    return im


def _label(text, font, fg, bg, padx=22, pady=10, radius=10):
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = int(d0.textlength(text, font=font))
    im = Image.new("RGBA", (tw + padx * 2, font.size + pady * 2 + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius=radius, fill=bg + (255,))
    d.text((padx, pady - 2), text, font=font, fill=fg)
    return im


def _stamp(text, color=EMPH_RED, size=56):
    """Rubber-stamp label: outlined, slightly rotated."""
    f = F_HEAD(size)
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = int(d0.textlength(text, font=f))
    im = Image.new("RGBA", (tw + 60, size + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, im.size[0] - 5, im.size[1] - 5], radius=12, outline=color + (255,), width=6)
    d.text((30, 18), text, font=f, fill=color + (255,))
    return im.rotate(-6, expand=True, resample=Image.BICUBIC)


NEW_KINDS = {"quiz", "answer", "chat", "myth", "number", "story", "bug", "table", "flow", "tip",
             "fact", "choice", "checklist", "screen"}


def build_new_kind(B, s, accent, x, w, avail_h):
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    kind = s.get("kind")
    y = 0

    def heading(text, size=66, anim="up"):
        nonlocal y
        if text:
            y = B.add(heading_img(text, F_HEAD(size), w, lh=int(size * 1.14)), x - 6, y, anim) + 34

    def body(text, size=44, pause=0.35, color=MUTED):
        nonlocal y
        for para in str(text).split("\n\n"):
            if para.strip():
                y = B.add(text_img(wrap(d0, para, F_BODY(size), w), F_BODY(size), color, int(size * 1.42), w),
                          x, y, "up", pause) + 24

    def marker_box(text, size=44):
        nonlocal y
        hl = wrap(d0, text, F_SEMI(size), w - 72)
        h = len(hl) * int(size * 1.36) + 64
        box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dd = ImageDraw.Draw(box)
        dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=MARKER + (255,))
        dd.rectangle([0, 0, 9, h - 1], fill=accent + (255,))
        yy = 30
        for ln in hl:
            dd.text((36, yy), ln, font=F_SEMI(size), fill=INK)
            yy += int(size * 1.36)
        y = B.add(box, x, y + 10, "pop", 0.3, "pop") + 10

    if kind == "cover":
        style = s.get("style")
        if s.get("kicker"):
            y = B.add(text_img([s["kicker"]], F_HAND(64), accent, 70), x, y, "up") + 20
        if style == "number":
            num = text_img([str(s.get("number", "7"))], F_HAND(300), accent, 300)
            B.add(num, x - 10, y - 30, "stamp", 0.3, "stamp")
            tx, tw_ = x + num.size[0] + 40, w - num.size[0] - 40
            im = heading_img(s["title"], F_HEAD(84), tw_, lh=94)
            B.add(im, tx, y + 40, "up", 0.3)
            y = y + max(num.size[1] - 40, im.size[1] + 40) + 30
        elif style == "question":
            y = B.add(heading_img(s["title"], F_HEAD(100), w, lh=110), x - 6, y, "pop", 0.3, "pop") + 10
            y = B.add(text_img(["?"], F_HAND(220), accent, 220), x + w - 160, y - 30, "stamp", 0.3, "stamp", decor=True) + 10
        elif style == "checklist":
            heading(s["title"], 92)
            for it in s.get("items", [])[:4]:
                row = Image.new("RGBA", (w, 76), (0, 0, 0, 0))
                dd = ImageDraw.Draw(row)
                dd.rounded_rectangle([0, 10, 52, 62], radius=8, outline=INK + (255,), width=4)
                dd.text((80, 8), it, font=F_SEMI(46), fill=INK)
                row.info["base"] = 8 + asc(F_SEMI(46))
                B.add(row, x, y, "up", 0.2)
                y = B.items[-1]["y"]
                B.overlay(ov_tick(56), x - 2, y + 6, 60, 60, pause=0.25, dur=0.35, sfx="tick")
                y += 92
        elif style == "bug":
            heading(s["title"], 92)
            if s.get("code"):
                y = _code_blocks(B, x, y, w, s["code"], accent, avail_h - y - 40, "zbug.abap")
                ln_i = int(s.get("bug_line", 0))
                geo = B.last_code
                if 0 <= ln_i < len(geo["lines"]):
                    ly, lw = geo["lines"][ln_i]
                    B.overlay(ov_circle(min(lw, w - 80), geo["lh"] - 10), x + 32, ly, min(lw, w - 80), geo["lh"] - 10,
                              pause=0.3, dur=0.6)
        else:
            heading(s["title"], 96, "pop")
        if s.get("subtitle"):
            y += 10
            body(s["subtitle"], 44, 0.3)

    elif kind == "quiz":
        heading(s.get("question", ""), 64)
        opts = s.get("options", [])
        letters = "ABCD"
        boxes = []
        for i, o in enumerate(opts[:4]):
            f = F_SEMI(42)
            lines = wrap(d0, o, f, w - 150)
            card = _card(w, lines, f, pad=28)
            d = ImageDraw.Draw(card)
            # letter badge
            card2 = Image.new("RGBA", (w, card.size[1]), (0, 0, 0, 0))
            card2.alpha_composite(card)
            d2 = ImageDraw.Draw(card2)
            d2.rounded_rectangle([0, 0, w - 1, card.size[1] - 1], radius=18, fill=PANEL + (255,), outline=BORDER + (255,), width=3)
            d2.ellipse([22, card.size[1] // 2 - 30, 82, card.size[1] // 2 + 30], fill=accent + (255,))
            d2.text((40, card.size[1] // 2 - 26), letters[i], font=F_HEAD(42), fill=(255, 255, 255))
            yy = 28
            for ln in lines:
                d2.text((104, yy), ln, font=f, fill=INK)
                yy += int(f.size * 1.35)
            boxes.append((y, card2.size[1]))
            y = B.add(card2, x, y, "slide", 0.3, "pop") + 20
        reveal = s.get("reveal", True)
        ans = s.get("answer")
        do_reveal = reveal and ans is not None and 0 <= int(ans) < len(boxes)
        area_y = y + 10
        if s.get("countdown", True) or do_reveal:
            y = area_y + 200   # reserved strip below the options: countdown, then the stamp
        if s.get("countdown", True):
            for n in ("3", "2", "1"):
                num = text_img([n], F_HAND(200), accent, 200)
                B.add(num, x + (w - num.size[0]) // 2, area_y - 10, "stamp", 0.75, "tick", until=0.72, decor=True)
        if do_reveal:
            by, bh = boxes[int(ans)]
            B.overlay(ov_box(w, bh), x, by, w, bh, pause=0.2, dur=0.6)
            st = _stamp("CORRECT: " + "ABCD"[int(ans)], GREEN, 52)
            B.add(st, x + (w - st.size[0]) // 2, area_y + 20, "stamp", 0.3, "stamp")

    elif kind == "answer":
        st = _stamp(s.get("label", "ANSWER"), GREEN, 52)
        y = B.add(st, x, y, "stamp", 0.35, "stamp") + 20
        heading(s.get("heading", ""), 72)
        body(s.get("body", ""))
        if s.get("highlight"):
            marker_box(s["highlight"])

    elif kind == "chat":
        heading(s.get("heading", ""), 60)
        for m in s.get("messages", []):
            me = str(m.get("from", "")).lower() in ("you", "me", "candidate")
            f = F_BODY(42)
            bw = int(w * 0.8)
            lines = wrap(d0, m.get("text", ""), f, bw - 70)
            lh = int(f.size * 1.38)
            h = 56 + lh * len(lines) + 34
            im = Image.new("RGBA", (bw, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            bg = accent if me else PANEL
            fg = (255, 255, 255) if me else INK
            d.rounded_rectangle([0, 0, bw - 1, h - 1], radius=28, fill=bg + (255,),
                                outline=(bg if me else BORDER) + (255,), width=3)
            d.text((34, 18), m.get("from", ""), font=F_SEMI(30), fill=(220, 232, 250) if me else accent)
            yy = 58
            for ln in lines:
                d.text((34, yy), ln, font=f, fill=fg)
                yy += lh
            bx = x + (w - bw if me else 0)
            reading = 0.5 + len(m.get("text", "")) / 45
            y = B.add(im, bx, y, "pop", reading, "pop") + 22

    elif kind == "myth":
        lab = _label("MYTH", F_HEAD(34), (255, 255, 255), EMPH_RED)
        y = B.add(lab, x, y, "pop", 0.25, "pop") + 18
        m_lines = wrap(d0, s.get("myth", ""), F_SEMI(52), w)
        mt = text_img(m_lines, F_SEMI(52), INK, 70, w)
        y = B.add(mt, x, y, "up", 0.6) + 36
        my = B.items[-1]["y"]          # actual (grid-snapped) position of the myth text
        # strike through every myth line, exactly as long as the line
        for i, ln in enumerate(m_lines):
            lw_ = int(d0.textlength(ln, font=F_SEMI(52)))
            B.overlay(ov_strike(lw_, 60), x, my + i * G, lw_, 60,
                      pause=0.15 if i < len(m_lines) - 1 else 0.4, dur=0.35)
        st = _stamp("FACT", GREEN, 56)
        y = B.add(st, x, y, "stamp", 0.35, "stamp") + 16
        marker_box(s.get("fact", ""), 46)
        if s.get("detail"):
            body(s["detail"], 40)

    elif kind == "number":
        num = text_img([str(s.get("number", 1))], F_HAND(320), accent, 320)
        B.add(num, x - 10, y - 40, "stamp", 0.35, "stamp")
        y = y + num.size[1] - 70
        heading(s.get("title", ""), 70)
        body(s.get("body", ""), 44)
        if s.get("code"):
            y = _code_blocks(B, x, y + 10, w, s["code"], accent, avail_h - y - 20, s.get("filename", "program.abap")) + 10

    elif kind == "story":
        k = " · ".join(t for t in (s.get("time"), s.get("place")) if t)
        if k:
            y = B.add(text_img([k], F_HAND(70), accent, 76), x, y, "fade", 0.4) + 24
        heading(s.get("heading", ""), 66)
        for ln in s.get("lines", []):
            im = text_img(wrap(d0, ln, F_BODY(46), w), F_BODY(46), INK, 66, w)
            y = B.add(im, x, y, "fade", 0.5 + len(ln) / 60) + 22
        if s.get("lesson"):
            marker_box(s["lesson"], 44)

    elif kind == "bug":
        heading(s.get("heading", ""), 62)
        note = s.get("note", "")
        note_h = 110 if note else 0
        y = _code_blocks(B, x, y, w, s.get("code", ""), accent, avail_h - y - note_h - 20,
                         s.get("filename", "zbug.abap"), typewriter=bool(s.get("typewriter")))
        geo = B.last_code
        ln_i = int(s.get("bug_line", 0))
        if 0 <= ln_i < len(geo["lines"]):
            ly, lw = geo["lines"][ln_i]
            cw = min(lw, w - 80)
            B.overlay(ov_circle(cw, geo["lh"] - 10), x + 32, ly, cw, geo["lh"] - 10, pause=0.25, dur=0.6)
            if note:
                nt = text_img([note], F_HAND(62), EMPH_RED, 66)
                ny = y + 26
                # arrow runs up the right margin from the note to the circled line
                ax0 = w - 40
                ax1 = min(w - 60, 32 + cw + 40)
                B.overlay(ov_arrow(ax0, 20, ax1, -(ny - ly) + geo["lh"] // 2), x, ny, w, 10, pause=0.15, dur=0.4)
                B.add(nt, x + max(0, w - 60 - nt.size[0]), ny + 4, "fade", 0.3, nosnap=True)
                y = ny + nt.size[1] + 10

    elif kind == "screen":
        # A simplified SAP GUI screen (e.g. SE11 domain) with tabs and field rows; key rows get an outline + note.
        heading(s.get("heading", ""), 60)
        fields = s.get("fields", [])
        focus = s.get("focus", [])
        focus = set(focus if isinstance(focus, list) else [focus])
        lf, vf = F_BODY(34), F_MONO(30)
        head_h, tab_h, row_h, pad = 64, (60 if s.get("tabs") else 0), 74, 22
        h = head_h + tab_h + pad + len(fields) * row_h + pad
        fr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dd = ImageDraw.Draw(fr)
        dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=18, fill=PANEL + (255,), outline=BORDER + (255,), width=2)
        dd.rounded_rectangle([0, 0, w - 1, head_h], radius=18, fill=PANEL_TOP + (255,))
        dd.rectangle([0, head_h - 20, w - 1, head_h], fill=PANEL_TOP + (255,))
        tc = str(s.get("tcode", "SE11"))
        tw_ = int(d0.textlength(tc, font=F_MONO_B(26))) + 28
        dd.rounded_rectangle([20, 14, 20 + tw_, 50], radius=8, fill=accent + (255,))
        dd.text((34, 18), tc, font=F_MONO_B(26), fill=(255, 255, 255))
        dd.text((20 + tw_ + 18, 19), str(s.get("object", "")), font=F_MONO(26), fill=DIM)
        dd.line([0, head_h, w, head_h], fill=BORDER + (255,), width=2)
        tx = 24
        for i, t in enumerate(s.get("tabs", [])):
            tf = F_SEMI(28) if i == s.get("active", 0) else F_BODY(28)
            tl = int(d0.textlength(t, font=tf))
            col = accent if i == s.get("active", 0) else MUTED
            dd.text((tx, head_h + 16), t, font=tf, fill=col)
            if i == s.get("active", 0):
                dd.rectangle([tx, head_h + tab_h - 6, tx + tl, head_h + tab_h - 2], fill=accent + (255,))
            tx += tl + 40
        if tab_h:
            dd.line([0, head_h + tab_h, w, head_h + tab_h], fill=BORDER + (255,), width=2)
        B.add(fr, x, y, "up", 0.25, "pop", container=True)
        y0 = B.items[-1]["y"]
        label_w = int(w * 0.44)
        ry = y0 + head_h + tab_h + pad
        rows_geo = []
        for i, (lab, val) in enumerate(fields):
            row = Image.new("RGBA", (w - 40, row_h - 10), (0, 0, 0, 0))
            rd = ImageDraw.Draw(row)
            rd.text((4, (row_h - 10 - 34) // 2), str(lab), font=lf, fill=MUTED)
            vb0 = label_w
            rd.rounded_rectangle([vb0, 4, w - 44, row_h - 14], radius=8, fill=(255, 255, 255, 255),
                                 outline=BORDER + (255,), width=2)
            rd.text((vb0 + 16, (row_h - 10 - 30) // 2), str(val), font=vf, fill=INK)
            B.add(row, x + 20, ry, "type", 0.18 if i not in focus else 0.3, nosnap=True)
            rows_geo.append(ry)
            ry += row_h
        for i in sorted(focus):
            if 0 <= i < len(rows_geo):
                B.overlay(ov_box(w - 40, row_h - 10, EMPH_RED, pad=6, width=5), x + 20, rows_geo[i], w - 40, row_h - 10,
                          pause=0.2, dur=0.5)
        y = y0 + h + 26
        if s.get("note"):
            nt = text_img([s["note"]], F_HAND(52), EMPH_RED, 56)
            y = B.add(nt, x + max(0, w - nt.size[0]), y, "fade", 0.3, nosnap=True) + 16
        if s.get("body"):
            body(s["body"], 40)

    elif kind == "table":
        heading(s.get("heading", ""), 62)
        cols = s.get("columns", [])
        rows = s.get("rows", [])
        n = max(1, len(cols))
        cw = w // n
        fs = 38 if len(rows) <= 6 else 32
        rh = int(fs * 1.9)
        hdr = Image.new("RGBA", (w, rh), (0, 0, 0, 0))
        d = ImageDraw.Draw(hdr)
        d.rounded_rectangle([0, 0, w - 1, rh - 1], radius=12, fill=accent + (255,))
        for i, c in enumerate(cols):
            d.text((i * cw + 22, (rh - fs) // 2 - 4), str(c), font=F_SEMI(fs), fill=(255, 255, 255))
        y = B.add(hdr, x, y, "up", 0.25) + 4
        for r_i, r in enumerate(rows):
            row = Image.new("RGBA", (w, rh), (0, 0, 0, 0))
            d = ImageDraw.Draw(row)
            if r_i % 2 == 0:
                d.rectangle([0, 0, w - 1, rh - 1], fill=PANEL + (255,))
            for i, c in enumerate(r[:n]):
                font = F_MONO_B(fs - 2) if i == 0 else F_BODY(fs)
                txt = str(c)
                while d0.textlength(txt, font=font) > cw - 30 and len(txt) > 3:
                    txt = txt[:-2] + "…"
                d.text((i * cw + 22, (rh - fs) // 2 - 4), txt, font=font, fill=INK if i else accent)
            y = B.add(row, x, y, "up", 0.2) + 0

    elif kind == "flow":
        heading(s.get("heading", ""), 62)
        steps = s.get("steps", [])
        bw = int(w * 0.86)
        bx = x + (w - bw) // 2
        gap = 64
        for i, st_ in enumerate(steps):
            card = _card(bw, wrap(d0, st_, F_SEMI(40), bw - 60), F_SEMI(40), pad=24)
            y = B.add(card, bx, y, "pop", 0.25, "pop")
            if i < len(steps) - 1:
                B.overlay(ov_arrow(0, 6, 0, gap - 6, accent), x + w // 2, y, 2, gap, pause=0.2, dur=0.35, sfx=None)
                y += gap

    elif kind == "tip":
        if s.get("kicker"):
            y = B.add(text_img([s["kicker"]], F_HAND(62), accent, 66), x, y, "up") + 16
        q = text_img(["“"], F_HEAD(220), MARKER, 180)
        B.add(q, x - 10, y - 30, "stamp", 0.2, decor=True)
        y += 90
        heading(s.get("quote", ""), 76)
        if s.get("by"):
            y = B.add(text_img(["— " + s["by"]], F_HAND(56), MUTED, 60), x, y, "fade", 0.3) + 10

    elif kind == "fact":
        y = B.add(text_img([s.get("title", "Did you know?")], F_HAND(84), accent, 88), x, y, "up", 0.3) + 10
        heading(s.get("text", ""), 74, "pop")
        if s.get("detail"):
            body(s["detail"], 42)

    elif kind == "choice":
        heading(s.get("question", ""), 66)
        GAP = 96
        half = (w - GAP) // 2
        cards = []
        for key in ("a", "b"):
            o = s.get(key, {}) or {}
            f = F_SEMI(40)
            lines = wrap(d0, o.get("label", ""), f, half - 50)
            sub = wrap(d0, o.get("sub", ""), F_BODY(32), half - 50) if o.get("sub") else []
            h = 120 + len(lines) * 54 + len(sub) * 44 + 30
            cards.append((key, lines, sub, h))
        ch = max(c[3] for c in cards)
        built = []
        for key, lines, sub, _ in cards:
            f = F_SEMI(40)
            h = ch                                   # both cards the same height
            im = Image.new("RGBA", (half, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, half - 1, h - 1], radius=20, fill=PANEL + (255,), outline=BORDER + (255,), width=3)
            d.text((26, 18), key.upper(), font=F_HAND(84), fill=accent)
            yy = 112
            for ln in lines:
                d.text((26, yy), ln, font=f, fill=INK)
                yy += 54
            for ln in sub:
                d.text((26, yy), ln, font=F_BODY(32), fill=MUTED)
                yy += 44
            built.append(im)
        cards = built
        B.add(cards[0], x, y, "slide", 0.3, "pop")
        orim = text_img(["or"], F_HAND(60), MUTED, 60)
        bb = orim.getchannel("A").getbbox() or (0, 0) + orim.size
        ox = x + half + (GAP - (bb[2] - bb[0])) // 2 - bb[0]     # centre the visible glyphs in the gap
        oy = y + (ch - (bb[3] - bb[1])) // 2 - bb[1]
        B.add(orim, ox, oy, "fade", 0.25, nosnap=True)
        B.add(cards[1], x + half + GAP, y, "slide", 0.4, "pop")
        ans = str(s.get("answer", "")).lower()
        if ans in ("a", "b"):
            cx_ = x if ans == "a" else x + half + GAP
            B.overlay(ov_box(half, ch), cx_, y, half, ch, pause=0.2, dur=0.6)
        y += ch + 20
        if s.get("explain"):
            body(s["explain"], 40)

    elif kind == "checklist":
        heading(s.get("heading", ""), 64)
        for it in s.get("items", []):
            title, _, rest = str(it).partition(" - ")
            tl = wrap(d0, title, F_SEMI(42), w - 100)
            rl = wrap(d0, rest, F_BODY(34), w - 100) if rest else []
            h = len(tl) * 56 + len(rl) * 46 + 16
            row = Image.new("RGBA", (w, max(h, 70)), (0, 0, 0, 0))
            d = ImageDraw.Draw(row)
            d.rounded_rectangle([0, 8, 52, 60], radius=8, outline=INK + (255,), width=4)
            yy = 4
            for ln in tl:
                d.text((84, yy), ln, font=F_SEMI(42), fill=INK)
                yy += 56
            for ln in rl:
                d.text((84, yy), ln, font=F_BODY(34), fill=MUTED)
                yy += 46
            row.info["base"] = 4 + asc(F_SEMI(42))
            B.add(row, x, y, "up", 0.15)
            y = B.items[-1]["y"]
            B.overlay(ov_tick(56), x - 2, y + 4, 60, 60, pause=0.35, dur=0.35, sfx="tick")
            y += row.size[1] + 24
    if not B.items:
        B.add(text_img([" "], F_BODY(20), INK, 20), x, 0)


# ---------------------------------------------------------------------
# Recipes: format -> pace + transitions (reels); rotation tracked in state.json
# ---------------------------------------------------------------------
PACES = {   # reels are short (12-18 s), so even "calm" is brisk
    "fast": {"voice_speed": 1.1, "lead": 0.12, "tail": 0.22, "pause_k": 0.6, "push": 0.06, "trans": 0.26},
    "calm": {"voice_speed": 1.0, "lead": 0.2, "tail": 0.32, "pause_k": 0.85, "push": 0.035, "trans": 0.36},
    # research-based pace (12 Nov): ~6% silence instead of ~16%, +5% voice, a visual "beat" every ~2.6 s
    "snappy": {"voice_speed": 1.03, "lead": 0.1, "tail": 0.22, "pause_k": 0.55, "push": 0.03, "trans": 0.24,
               "tighten": True, "beat": 2.6},
}
REEL_MIN, REEL_MAX = 6.0, 30.0        # any length the topic needs, never over 30 s (else split into parts)
COURSE_MIN, COURSE_MAX = 6.0, 30.0    # same rule for course reels
FORMATS = {
    "bug_hunt":       {"pace": "fast", "transitions": ["whip", "zoom", "slide", "whip"]},
    "before_after":   {"pace": "fast", "transitions": ["slide", "wipe", "zoom", "slide"]},
    "quiz":           {"pace": "fast", "transitions": ["zoom", "whip", "rise", "zoom"]},
    "three_things":   {"pace": "fast", "transitions": ["flip", "slide", "flip", "slide"]},
    "myth_fact":      {"pace": "fast", "transitions": ["wipe", "zoom", "wipe", "rise"]},
    "live_coding":    {"pace": "calm", "transitions": ["rise", "wipe", "rise", "flip"]},
    "interview_chat": {"pace": "calm", "transitions": ["slide", "rise", "slide", "rise"]},
    "story":          {"pace": "calm", "transitions": ["rise", "flip", "wipe", "rise"]},
}


OUTRO = {"kind": "cta", "title": "Follow for more *ABAP tricks*",
         "body": "3 new ABAP reels every day.",
         "actions": ["Follow @abapcodevault"],
         "voiceover": "Follow for more tips and tricks.",
         "spoken": "Follow for more tips and tricks."}


OUTRO_NEXT = {"kind": "cta", "title": "Part {n} is *next*",
              "body": "Follow so you don't miss it.",
              "actions": ["Follow @abapcodevault"],
              "voiceover": "The next part is coming soon. Follow so you don't miss it.",
              "spoken": "The next part is coming soon. Follow so you don't miss it."}


def next_card(nx):
    """End card that teases the next reel: {"title": "...", "when": "tomorrow at 9 AM", "voice": optional spoken title}."""
    title = str(nx.get("title", "")).strip()
    when = str(nx.get("when", "")).strip()
    said = str(nx.get("voice") or title.replace("*", "")).strip()
    vo = f"Next: {said}, {when}. Follow so you don't miss it." if when else f"Next: {said}. Follow so you don't miss it."
    return {"kind": "cta", "label": "NEXT", "title": f"Next: {title if '*' in title else '*' + title + '*'}",
            "body": (when[:1].upper() + when[1:] + ".") if when else "Follow so you don't miss it.",
            "actions": ["Follow @abapcodevault"], "voiceover": vo, "spoken": vo}


def with_outro(p, slides):
    """Every reel ends with an end card:
    - "next": {...} on the post -> a "Next: <title>" card (replaces a reel's own follow CTA at the end);
    - otherwise course parts that continue get "Part N is next", everything else the follow card.
    "outro": false turns it off."""
    if p.get("outro") is False or not slides:
        return slides
    last = slides[-1]
    own_cta = last.get("kind") == "cta" and "follow" in json.dumps(last, ensure_ascii=False).lower()
    if p.get("next"):
        base = list(slides[:-1]) if own_cta else list(slides)
        return base + [next_card(p["next"])]
    if own_cta:
        return slides
    part, parts = int(p.get("part") or 0), int(p.get("parts") or 0)
    if part and parts and part < parts:
        card = dict(OUTRO_NEXT)
        card["title"] = card["title"].format(n=part + 1)
        return list(slides) + [card]
    return list(slides) + [dict(OUTRO)]


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    handle = spec.get("handle", "@abapcodevault")
    captions = []
    accents = {"carousel": SAP_BLUE, "post": SAP_BLUE, "reel": SAP_BLUE}
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
            slides = with_outro(p, slides)
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
    if OVERLAPS:
        uniq = sorted(set(OVERLAPS))
        print("OVERLAP WARNING:\n  " + "\n  ".join(uniq))
        with open(os.path.join(out, "OVERLAP_WARNING.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(uniq) + "\n")


if __name__ == "__main__":
    main()
