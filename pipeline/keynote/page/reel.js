// reel.js — @abapcodevault reels in the Dark Tech Keynote style (1080×1920).
// Renders the existing day-file slide schema (cover, answer, screen, flow, versus, output, code, ...) from a
// spec written by pipeline/generate.py (slide times, speech window, word timings, captions).
import * as E from './engine.js';
const { W, H, PAL, clamp, lerp, seg, ss, eo, eio, back, hash, TAU, rr, font, rgba } = E;

let S = null;                          // spec
const SLOT = 1500;                     // world distance between slides
const X0 = 70, CW = 940;               // content column (world x)
const ACC = '#B7F34A';
E.setAccent(ACC);

// ───────── text helpers ─────────
function T(g, s, x, y, px, o = {}) {
  const { wt = 500, fam = 'ui', color = PAL.text, align = 'left', base = 'middle', alpha = 1 } = o;
  if (!s) return 0;
  g.save(); g.globalAlpha *= alpha; g.font = font(px, wt, fam); g.fillStyle = color; g.textAlign = align; g.textBaseline = base;
  g.fillText(s, x, y); const w = g.measureText(s).width; g.restore(); return w;
}
function measure(g, s, px, wt = 500, fam = 'ui') { g.save(); g.font = font(px, wt, fam); const w = g.measureText(s).width; g.restore(); return w; }
function fitPx(g, s, px, maxw, wt = 500, fam = 'ui', min = 20) { while (px > min && measure(g, s, px, wt, fam) > maxw) px -= 2; return px; }
// "*key words*" markup → word tokens; hl marks highlighted words
function tokens(text, hlPhrase = null) {
  const out = []; let hi = false;
  String(text || '').split(/(\*)/).forEach(part => { if (part === '*') { hi = !hi; return; }
    part.split(/\s+/).filter(Boolean).forEach(w => out.push({ w, hi })); });
  if (hlPhrase) {   // also mark a plain phrase (answer.highlight)
    const ph = hlPhrase.toLowerCase().split(/\s+/).map(norm);
    for (let i = 0; i + ph.length <= out.length; i++)
      if (ph.every((p, k) => norm(out[i + k].w) === p)) { for (let k = 0; k < ph.length; k++) out[i + k].ph = true; break; }
  }
  return out;
}
function wrapTok(g, toks, px, wt, maxw, fam = 'ui') {
  g.save(); g.font = font(px, wt, fam); const sp = g.measureText(' ').width;
  const lines = []; let cur = [], w = 0;
  toks.forEach(t => { const tw = g.measureText(t.w).width; if (cur.length && w + sp + tw > maxw) { lines.push({ toks: cur, w }); cur = []; w = 0; }
    t.tw = tw; w += (cur.length ? sp : 0) + tw; cur.push(t); });
  if (cur.length) lines.push({ toks: cur, w }); g.restore(); lines.sp = sp; return lines;
}
// draw wrapped rich text; reveal(i) → 0..1 per word index; returns height
function rich(g, text, x, y, px, o = {}) {
  const { wt = 700, maxw = CW, lh = px * 1.18, align = 'left', color = PAL.text, hi = ACC, reveal = null, hl = null, under = 0, fam = 'ui', maxLines = 9 } = o;
  const toks = tokens(text, hl); let lines = wrapTok(g, toks, px, wt, maxw, fam);
  let size = px; while (lines.length > maxLines && size > 24) { size -= 4; lines = wrapTok(g, toks, size, wt, maxw, fam); }
  const LH = lh * size / px; let k = 0;
  g.save(); g.font = font(size, wt, fam); g.textBaseline = 'middle';
  lines.forEach((L, li) => {
    let cx = align === 'center' ? x - L.w / 2 : x; const yy = y + li * LH;
    L.toks.forEach(t => {
      const r = reveal ? reveal(k) : 1;
      if (r > 0) {
        g.save(); g.globalAlpha *= clamp(r * 2.5); const dy = (1 - eo(r)) * size * 0.35;
        if (t.ph && under > 0) { g.fillStyle = rgba(ACC, 0.22); g.fillRect(cx - 4, yy + size * 0.36, (t.tw + 8) * clamp(under), size * 0.14); }
        g.fillStyle = t.hi || t.ph ? hi : color; g.fillText(t.w, cx, yy + dy); g.restore();
      }
      cx += t.tw + lines.sp; k++;
    });
  });
  g.restore(); return lines.length * LH;
}
const norm = w => String(w).toLowerCase().replace(/[^a-z0-9]/g, '');
const drop = (t, t0, d = 0.3) => back(seg(t, t0, t0 + d), 1.3);
const blink = t => (Math.floor(t * 2.2) % 2 ? 0.25 : 1);
const plain = s => String(s || '').replace(/\*/g, '');
function sayWord(text) {
  for (const w of plain(text).split(/\s+/)) { let k = norm(w); if (k === 'no') k = 'number'; if (k.length >= 1) return k; } return null;
}
// time the first word starting with key is spoken in slide s (after `after`); fallback = fraction of the speech window
function cue(s, key, frac, after = -1) {
  if (key) { const k = norm(key);
    const hit = s.words.find(([w, a]) => a > after && k && (norm(w) === k || (k.length >= 3 && norm(w).startsWith(k)) || (norm(w).length >= 4 && k.startsWith(norm(w)))));
    if (hit) return hit[1]; }
  return s.st + s.ln * frac;
}
function seqCues(s, keys, f0 = 0.12, f1 = 0.8) {   // ordered cues: each item after the previous one
  const out = []; let last = s.t0 - 0.01; const n = keys.length;
  keys.forEach((k, i) => { const fb = s.st + s.ln * (n > 1 ? lerp(f0, f1, i / (n - 1)) : f0);
    let c = cue(s, k, -1, last); if (c < 0 || c === s.st - s.ln) c = fb; if (c < last + 0.25) c = Math.max(fb, last + 0.35); out.push(c); last = c; });
  return out.map(c => Math.min(c, s.t1 - 0.5));
}

// ───────── shared drawing ─────────
function padlock(g, x, y, s, color, open = 0) {
  g.save(); g.strokeStyle = color; g.fillStyle = color; g.lineWidth = s * 0.14; g.lineCap = 'round';
  g.beginPath(); g.arc(x, y - s * 0.12 - open * s * 0.22, s * 0.28, Math.PI, 0); g.lineTo(x + s * 0.28, y + s * 0.05 - open * s * 0.22); g.stroke();
  if (open < 0.5) { g.beginPath(); g.moveTo(x - s * 0.28, y - s * 0.12); g.lineTo(x - s * 0.28, y + s * 0.05); g.stroke(); }
  rr(g, x - s * 0.42, y, s * 0.84, s * 0.62, s * 0.12); g.fill(); g.restore();
}
function pointer(g, x, y, press = 0) {
  g.save(); g.translate(x, y); const k = 1 - press * 0.15; g.scale(k, k);
  g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 44); g.lineTo(11, 33); g.lineTo(19, 52); g.lineTo(27, 48); g.lineTo(19, 30); g.lineTo(34, 30); g.closePath();
  g.shadowColor = 'rgba(0,0,0,.6)'; g.shadowBlur = 12; g.fillStyle = '#F2F4F8'; g.fill(); g.shadowColor = 'transparent'; g.lineWidth = 2; g.strokeStyle = '#0A0B0F'; g.stroke(); g.restore();
}
function chip(g, text, x, y, o = {}) {        // small mono label pill (left anchored)
  const { px = 26, color = PAL.dim, fill = PAL.surf2, alpha = 1, dot = false } = o; if (!text) return 0;
  const w = measure(g, text, px, 700, 'mono') + px * 1.6 + (dot ? px : 0), h = px * 2;
  g.save(); g.globalAlpha *= alpha; E.panel(g, x, y - h / 2, w, h, { r: h / 2, fill, shadow: 0.4 });
  if (dot) { E.glow(g, x + px * 0.95, y, px, ACC, 0.5); g.fillStyle = ACC; g.beginPath(); g.arc(x + px * 0.95, y, px * 0.2, 0, TAU); g.fill(); }
  T(g, text, x + px * 0.8 + (dot ? px : 0), y + 1, px, { wt: 700, fam: 'mono', color }); g.restore(); return w;
}
function win(g, x, y, w, h, title, o = {}) { return E.windowBox(g, x, y, w, h, { title, app: 6, bar: 72, ...o }); }
function mark(g, kind, x, y, s, color) {      // ✓ / ✗ in a circle
  g.save(); g.strokeStyle = color; g.lineWidth = s * 0.12; g.lineCap = 'round';
  g.beginPath(); g.arc(x, y, s / 2, 0, TAU); g.stroke(); g.beginPath();
  if (kind === 'ok') { g.moveTo(x - s * 0.2, y); g.lineTo(x - s * 0.04, y + s * 0.17); g.lineTo(x + s * 0.22, y - s * 0.16); }
  else { g.moveTo(x - s * 0.16, y - s * 0.16); g.lineTo(x + s * 0.16, y + s * 0.16); g.moveTo(x + s * 0.16, y - s * 0.16); g.lineTo(x - s * 0.16, y + s * 0.16); }
  g.stroke(); g.restore();
}
function codeLine(g, line, x, y, px, n) {     // light syntax colouring: strings accent, comments mute, keywords bold
  let cx = x;
  if (/^\s*["*]/.test(line)) return T(g, line, cx, y, px, { fam: 'mono', color: PAL.mute });
  line.split(/('[^']*'?|`[^`]*`?|\s+)/).filter(s => s !== '').forEach(p => {
    const str = /^['`]/.test(p), kw = /^[A-Z][A-Z_-]{1,}$/.test(p.replace(/[.,:]$/, ''));
    cx += T(g, p, cx, y, px, { fam: 'mono', wt: kw ? 700 : 500, color: str ? ACC : kw ? PAL.text : '#C9CEDA' }); });
  return cx - x;
}
function header(g, s, t, Y) {                  // label chip + heading at the top of a slide
  let y = Y - 540;
  if (s.label) { chip(g, plain(s.label), X0, y, { alpha: ss(seg(t, s.t0 - 0.1, s.t0 + 0.15)), color: PAL.dim }); y += 70; }
  const head = s.heading || s.title || '';
  if (head) { const t0 = s.t0 - 0.05;
    const h = rich(g, head, X0, y + 10, 78, { wt: 700, reveal: k => seg(t, t0 + k * 0.05, t0 + k * 0.05 + 0.22), maxLines: 3 }); y += h + 30; }
  return y + 30;
}

// ───────── per-kind plan (cue times) and draw ─────────
const K = {};
K.cover = {
  plan(s) { s._sub = s.t0 + 0.6; return [['pop', s.t0 + 0.05]]; },
  draw(g, s, t, Y) {
    const t0 = s.t0 - (s.i === 0 ? 0.35 : 0.05);
    chip(g, plain(s.kicker), X0, Y - 330, { alpha: ss(seg(t, t0, t0 + 0.25)), dot: true, px: 28 });
    let y = Y - 210;
    if (s.number) { E.scramble(g, String(s.number), X0, y + 120, t, [...String(s.number)].map((c, i) => s.t0 + 0.4 + i * 0.08), { px: 220, start: s.t0 - 0.4, color: ACC }); y += 230; }
    const h = rich(g, s.title, X0, y, 108, { wt: 700, lh: 122, reveal: k => seg(t, t0 + k * 0.06, t0 + k * 0.06 + 0.25), maxLines: 6 });
    if (s.subtitle) rich(g, s.subtitle, X0, y + h + 40, 44, { wt: 500, color: PAL.dim, reveal: () => ss(seg(t, s._sub, s._sub + 0.3)) });
    E.caret(g, X0 + 12, y + h + (s.subtitle ? 150 : 50), 64, { on: blink(t), glow: 0.8 });
  },
};
function bodyPlan(s) { s._b = s.st + 0.15; s._hl = s.highlight ? cue(s, sayWord(s.highlight), 0.6, s.st) : null; return [['soft', s._b]].concat(s._hl ? [['glint', s._hl]] : []); }
K.answer = K.text = {
  plan: bodyPlan,
  draw(g, s, t, Y) {
    let y = header(g, s, t, Y) + 20;
    const n = tokens(s.body).length, span = Math.max(0.8, Math.min(s.ln * 0.7, n * 0.12));
    const by = Math.max(y + 20, Y - 220);
    const h = Math.min(7, wrapTok(g, tokens(s.body), 58, 500, CW - 80).length) * 78;
    const pa = ss(seg(t, s._b - 0.25, s._b + 0.05));
    if (pa > 0) { g.save(); g.globalAlpha *= pa; const pb = new Path2D(); pb.roundRect(X0, by, CW, h + 80, 28); E.litShape(g, pb, { bbox: [X0, by, CW, h + 80] });
      g.fillStyle = ACC; rr(g, X0, by + 30, 6, h + 20, 3); g.fill(); g.restore(); }
    rich(g, s.body, X0 + 40, by + 80, 58, { wt: 500, color: '#D5D9E3', maxw: CW - 80, lh: 78, hl: s.highlight, under: s._hl ? eo(seg(t, s._hl, s._hl + 0.4)) : 0,
      reveal: k => seg(t, s._b + span * k / n, s._b + span * k / n + 0.2), maxLines: 7 });
  },
};
K.list = K.checklist = {
  plan(s) { const items = s.items || []; s._c = seqCues(s, items.map(it => sayWord(typeof it === 'string' ? it : it.title || it.text))); return s._c.map(c => ['row', c]); },
  draw(g, s, t, Y) {
    let y = header(g, s, t, Y); const items = s.items || []; const rowH = Math.min(180, (Y + 480 - y) / Math.max(1, items.length));
    items.forEach((it, i) => { const p = drop(t, s._c[i], 0.3); if (p <= 0) return; const txt = typeof it === 'string' ? it : (it.title || it.text || '');
      const yy = y + i * rowH; g.save(); g.globalAlpha *= clamp(p * 2); g.translate((1 - p) * 60, 0);
      E.panel(g, X0, yy, CW, rowH - 20, { r: 22, fill: PAL.surf2, shadow: 0.6 });
      const on = t >= s._c[i] && (i === items.length - 1 || t < s._c[i + 1]);
      if (s.kind === 'checklist') mark(g, 'ok', X0 + 60, yy + (rowH - 20) / 2, 44, on ? ACC : PAL.dim);
      else T(g, String(i + 1).padStart(2, '0'), X0 + 36, yy + (rowH - 20) / 2, 34, { wt: 700, fam: 'mono', color: on ? ACC : PAL.mute });
      rich(g, txt, X0 + 120, yy + (rowH - 20) / 2 - (measure(g, plain(txt), 46, 600) > CW - 160 ? 26 : 0), 46, { wt: 600, maxw: CW - 160, lh: 54, maxLines: 2 });
      if (on) { g.strokeStyle = rgba(ACC, 0.6); g.lineWidth = 2; rr(g, X0 + 0.5, yy + 0.5, CW - 1, rowH - 21, 22); g.stroke(); }
      g.restore(); });
  },
};
K.flow = {
  plan(s) { s._c = seqCues(s, (s.steps || []).map(sayWord), 0.08, 0.75); return s._c.map(c => ['snap', c]); },
  draw(g, s, t, Y) {
    let y = header(g, s, t, Y); const st = s.steps || []; const gap = Math.min(230, (Y + 480 - y) / Math.max(1, st.length));
    const cx = X0 + 60; const pts = st.map((_, i) => [cx, y + i * gap + 55]);
    st.forEach((step, i) => {
      const p = drop(t, s._c[i], 0.3); if (p <= 0) return;
      if (i > 0) { const q = eo(seg(t, s._c[i] - 0.25, s._c[i])); const a = pts[i - 1], b = pts[i];
        const pts2 = []; for (let k = 0; k <= 20; k++) pts2.push([a[0], lerp(a[1] + 40, b[1] - 40, q * k / 20)]); E.trail(g, pts2, { width: 6 }); }
      const yy = pts[i][1]; const on = t >= s._c[i] && (i === st.length - 1 || t < s._c[i + 1]);
      g.save(); g.globalAlpha *= clamp(p * 2);
      const path = new Path2D(); path.arc(cx, yy, 40 * p, 0, TAU);
      E.litShape(g, path, { accent: on, glowR: on ? 30 : 0, bbox: [cx - 40, yy - 40, 80, 80] });
      T(g, String(i + 1), cx, yy + 2, 36, { wt: 700, fam: 'mono', color: on ? '#0A0B0F' : PAL.text, align: 'center' });
      g.translate((1 - p) * 50, 0);
      rich(g, step, cx + 80, yy - (measure(g, plain(step), 52, 600) > CW - 180 ? 30 : 0), 52, { wt: 600, maxw: CW - 180, lh: 60, maxLines: 2, color: on ? PAL.text : '#C9CEDA' });
      g.restore(); });
  },
};
K.screen = {
  plan(s) {
    const f = s.fields || [], focus = s.focus || [];
    const keys = f.map((fd, i) => (s.focus_say && focus.indexOf(i) >= 0 && s.focus_say[focus.indexOf(i)]) || sayWord(fd[0]));
    s._click = s.st + 0.25; s._c = seqCues(s, keys, 0.2, 0.75);
    s._note = s.note ? Math.max(s._c[s._c.length - 1] || 0, cue(s, sayWord(s.note), 0.82, s.st)) : null;
    return [['click', s._click]].concat(s._c.map((c, i) => [focus.includes(i) ? 'type' : 'row', c]), s._note ? [['notify', s._note]] : []);
  },
  draw(g, s, t, Y) {
    let y = header(g, s, t, Y); const f = s.fields || [], tabs = s.tabs || [], focus = s.focus || [];
    const stack = f.map(fd => measure(g, fd[0], 38) > 330), rowHs = stack.map(st => st ? 176 : 124);
    const h = 72 + (tabs.length ? 110 : 20) + rowHs.reduce((a, b) => a + b, 0) + 30;
    const pw = drop(t, s.t0 + 0.05, 0.35); if (pw <= 0) return;
    g.save(); g.globalAlpha *= clamp(pw * 2); g.translate(0, (1 - pw) * 40);
    const c = win(g, X0, y, CW, h, `${s.tcode || 'SAP'} · ${plain(s.object || '')}`);
    let yy = c[1] + 20;
    if (tabs.length) { let tx = X0 + 24; const px = fitPx(g, tabs.join('    '), 30, CW - 60 - tabs.length * 30, 600);
      tabs.forEach((tb, i) => { const w = measure(g, tb, px, 600) + 30, act = i === (s.active || 0) && t >= s._click;
        g.fillStyle = act ? 'rgba(183,243,74,.10)' : 'rgba(255,255,255,.04)'; rr(g, tx, yy, w, 64, 12); g.fill();
        if (act) { g.fillStyle = ACC; rr(g, tx + 8, yy + 60, w - 16, 4, 2); g.fill(); }
        T(g, tb, tx + 15, yy + 33, px, { wt: 600, color: act ? PAL.text : PAL.dim }); if (i === (s.active || 0)) s._tabxy = [tx + w / 2, yy + 28]; tx += w + 10; });
      yy += 110; }
    const lx = X0 + 36, vx0 = X0 + Math.min(420, 36 + Math.max(0, ...f.filter((_, i) => !stack[i]).map(fd => measure(g, fd[0], 38))) + 40);
    let ry = yy;
    f.forEach((fd, i) => { const p = drop(t, s._c[i], 0.26); let yr = ry; ry += rowHs[i]; if (p <= 0) return;
      g.save(); g.globalAlpha *= clamp(p * 2);
      const on = focus.includes(i); const vx = stack[i] ? lx : vx0;
      T(g, fd[0], lx, yr + (stack[i] ? 26 : 52), stack[i] ? 34 : fitPx(g, fd[0], 38, vx - lx - 20), { color: on ? PAL.text : PAL.dim, wt: on ? 600 : 500 });
      if (stack[i]) yr += 56;
      const vw = X0 + CW - 36 - vx; g.fillStyle = 'rgba(255,255,255,.045)'; rr(g, vx, yr + 6, vw, 92, 14); g.fill();
      g.strokeStyle = on ? rgba(ACC, 0.85 * p) : 'rgba(255,255,255,.1)'; g.lineWidth = on ? 3 : 1; rr(g, vx + 0.5, yr + 6.5, vw - 1, 91, 14); g.stroke();
      const v = String(fd[1] ?? ''); const typed = on ? v.slice(0, Math.round(v.length * clamp((t - s._c[i]) / Math.max(0.3, v.length * 0.045)))) : v;
      const vpx = fitPx(g, v, 40, vw - 50, 600, 'mono');
      const tw = T(g, typed, vx + 24, yr + 53, vpx, { fam: 'mono', wt: 600, color: on ? ACC : PAL.text });
      if (on && t < s._c[i] + v.length * 0.045 + 0.8) E.caret(g, vx + 32 + tw, yr + 52, 48, { on: blink(t), glow: 0.4 });
      g.restore(); });
    g.restore();
    if (s._tabxy && t > s._click - 0.6 && t < s._click + 0.8) { const p = eio(seg(t, s._click - 0.6, s._click));
      pointer(g, lerp(X0 + CW - 120, s._tabxy[0], p), lerp(y + h + 40, s._tabxy[1], p), Math.max(0, 1 - Math.abs(t - s._click) / 0.1)); }
    if (s._note) { const p = drop(t, s._note, 0.3); if (p > 0) { g.save(); g.globalAlpha *= clamp(p * 2);
      const ny = y + h + 50 + (1 - p) * 20; const npx = fitPx(g, plain(s.note), 40, CW - 120);
      E.panel(g, X0, ny, CW, 100, { r: 50, fill: PAL.surf2 }); E.glow(g, X0 + 50, ny + 50, 26, ACC, 0.5); g.fillStyle = ACC; g.beginPath(); g.arc(X0 + 50, ny + 50, 9, 0, TAU); g.fill();
      T(g, plain(s.note), X0 + 86, ny + 51, npx, { wt: 500 }); g.restore(); } }
  },
};
K.versus = {
  plan(s) { s._bad = cue(s, (s.bad || {}).say || sayWord((s.bad || {}).title), 0.12, s.t0); s._good = Math.max(s._bad + 0.6, cue(s, (s.good || {}).say || sayWord((s.good || {}).title), 0.55, s._bad));
    s._good = Math.min(s._good, s.t1 - 0.6); return [['error', s._bad], ['snap', s._good]]; },
  draw(g, s, t, Y) {
    const y = header(g, s, t, Y); const hh = Math.min(400, (Y + 470 - y - 40) / 2);
    const card = (o, yy, good, t0) => { const p = drop(t, t0, 0.32); if (p <= 0) return; g.save(); g.globalAlpha *= clamp(p * 2); g.translate(good ? (1 - p) * 80 : -(1 - p) * 80, 0);
      const dim = good ? 0 : ss(seg(t, s._good, s._good + 0.3));
      const path = new Path2D(); path.roundRect(X0, yy, CW, hh, 30); E.litShape(g, path, { bbox: [X0, yy, CW, hh] });
      g.strokeStyle = good ? rgba(ACC, 0.8) : rgba(PAL.red, 0.75 - dim * 0.4); g.lineWidth = 3; g.stroke(path);
      if (good) E.glow(g, X0 + 90, yy + hh / 2, 90, ACC, 0.18);
      mark(g, good ? 'ok' : 'no', X0 + 90, yy + hh / 2, 76, good ? ACC : PAL.red);
      T(g, good ? 'DO' : 'DON\'T', X0 + 170, yy + 56, 30, { wt: 700, fam: 'mono', color: good ? ACC : PAL.red });
      rich(g, o.title || '', X0 + 170, yy + 130, 58, { wt: 700, maxw: CW - 210, lh: 66, maxLines: 2 });
      if (o.sub) rich(g, o.sub, X0 + 170, yy + hh - 100, 38, { wt: 500, maxw: CW - 210, lh: 46, color: PAL.dim, maxLines: 2 });
      if (dim > 0) { g.fillStyle = `rgba(8,9,12,${0.45 * dim})`; g.fill(path); g.strokeStyle = rgba(PAL.red, 0.9); g.lineWidth = 6;
        g.beginPath(); g.moveTo(X0 + 160, yy + 130); g.lineTo(X0 + 160 + (CW - 220) * eo(dim), yy + 130); g.stroke(); }
      g.restore(); };
    card(s.bad || {}, y, false, s._bad); card(s.good || {}, y + hh + 40, true, s._good);
  },
};
K.compare = {
  plan(s) { s._l = s.st + 0.1; s._r = s.st + s.ln * 0.5; return [['snap', s._l], ['snap', s._r]]; },
  draw(g, s, t, Y) {
    const y = header(g, s, t, Y); const hh = (Y + 500 - y - 40) / 2;
    [[s.left_title, s.left, s._l, false], [s.right_title, s.right, s._r, true]].forEach(([ti, body, t0, good], k) => {
      const p = drop(t, t0, 0.3); if (p <= 0) return; const yy = y + k * (hh + 40);
      g.save(); g.globalAlpha *= clamp(p * 2); const path = new Path2D(); path.roundRect(X0, yy, CW, hh, 30); E.litShape(g, path, { bbox: [X0, yy, CW, hh] });
      if (good) { g.strokeStyle = rgba(ACC, 0.7); g.lineWidth = 2; g.stroke(path); }
      T(g, plain(ti), X0 + 40, yy + 60, 34, { wt: 700, fam: 'mono', color: good ? ACC : PAL.dim });
      const lines = Array.isArray(body) ? body : String(body || '').split('\n');
      const px = fitPx(g, lines.reduce((a, b) => a.length > b.length ? a : b, ''), 34, CW - 80, 500, 'mono');
      lines.slice(0, 7).forEach((ln, i) => codeLine(g, ln, X0 + 40, yy + 130 + i * px * 1.5, px));
      g.restore(); });
  },
};
function codeOf(s) { const c = s.code; return (Array.isArray(c) ? c : String(c || '').split('\n')); }
K.code = {
  plan(s) { const L = codeOf(s); const chars = L.join('').length || 1;
    s._a = s.st + 0.1; s._b = s.typewriter === false ? s._a + 0.4 : Math.min(s.st + s.ln * 0.85, s._a + Math.max(1.2, chars * 0.05));
    const ev = []; for (let k = 0; k < 12; k++) ev.push(['key', lerp(s._a, s._b, k / 12)]); return ev; },
  draw(g, s, t, Y) {
    const y = header(g, s, t, Y); const L = codeOf(s); const long = L.reduce((a, b) => Math.max(a, b.length), 0);
    const px = Math.min(38, Math.floor((CW - 130) / (long * 0.6 + 1))), lh = px * 1.75, h = 72 + 40 + L.length * lh + 30;
    const pw = drop(t, s.t0 + 0.05, 0.35); if (pw <= 0) return;
    g.save(); g.globalAlpha *= clamp(pw * 2);
    const c = win(g, X0, y, CW, h, s.filename || 'program.abap');
    const total = L.join('').length; const shown = Math.round(total * clamp((t - s._a) / (s._b - s._a)));
    let used = 0, cur = -1, curX = 0;
    L.forEach((ln, i) => { const yy = c[1] + 40 + i * lh + lh / 2; const n = Math.max(0, Math.min(ln.length, shown - used)); used += ln.length;
      T(g, String(i + 1).padStart(2, ' '), X0 + 24, yy, px * 0.8, { fam: 'mono', color: PAL.mute });
      if (n > 0) { const w = codeLine(g, ln.slice(0, n), X0 + 90, yy, px); if (n < ln.length || i === L.length - 1 || shown < used + 1) { cur = i; curX = w; } } });
    if (cur >= 0 && t < s._b + 0.8) E.caret(g, X0 + 98 + curX, c[1] + 40 + cur * lh + lh / 2, px * 1.2, { on: blink(t), glow: 0.4 });
    if (s.note) { const p = ss(seg(t, s._b, s._b + 0.3)); T(g, plain(s.note), X0 + 10, y + h + 50, 32, { color: PAL.dim, alpha: p }); }
    g.restore();
  },
};
K.sap_error = K.bug = {
  plan(s) { s._m = cue(s, s.say || 'error', 0.4, s.st); return [['error', s._m]]; },
  draw(g, s, t, Y) {
    const y = header(g, s, t, Y); const L = codeOf(s); const long = L.reduce((a, b) => Math.max(a, b.length), 0);
    const px = Math.min(36, Math.floor((CW - 130) / (long * 0.6 + 1))), lh = px * 1.8, h = 72 + 40 + L.length * lh + 30;
    const pw = drop(t, s.t0 + 0.05, 0.35); if (pw <= 0) return;
    const sh = t > s._m && t < s._m + 0.3 ? Math.sin(t * 90) * 10 * (1 - seg(t, s._m, s._m + 0.3)) : 0;
    g.save(); g.globalAlpha *= clamp(pw * 2); g.translate(sh, 0);
    const c = win(g, X0, y, CW, h, `${s.tcode || 'ST22'} · ${plain(s.title || '')}`);
    const bad = s.bad_line ?? -1, on = ss(seg(t, s._m - 0.1, s._m + 0.15));
    L.forEach((ln, i) => { const yy = c[1] + 40 + i * lh + lh / 2;
      if (i === bad && on > 0) { g.fillStyle = rgba(PAL.red, 0.16 * on); g.fillRect(X0 + 1, yy - lh / 2, CW - 2, lh); g.fillStyle = rgba(PAL.red, on); g.fillRect(X0 + 1, yy - lh / 2, 6, lh); }
      T(g, String(i + 1).padStart(2, ' '), X0 + 24, yy, px * 0.8, { fam: 'mono', color: PAL.mute }); codeLine(g, ln, X0 + 90, yy, px); });
    g.restore();
    const p = drop(t, s._m, 0.3); if (p > 0 && s.message) { g.save(); g.globalAlpha *= clamp(p * 2); const my = y + h + 40 + (1 - p) * 30;
      const lines = wrapTok(g, tokens(plain(s.message)), 34, 600, CW - 130, 'mono'); const mh = 50 + lines.length * 46;
      E.panel(g, X0, my, CW, mh, { r: 20, fill: '#2A1517', stroke: rgba(PAL.red, 0.6) });
      mark(g, 'no', X0 + 52, my + mh / 2, 46, PAL.red);
      lines.forEach((L2, i) => T(g, L2.toks.map(t2 => t2.w).join(' '), X0 + 100, my + 48 + i * 46, 34, { fam: 'mono', wt: 600, color: '#FFB3B5' }));
      g.restore(); }
  },
};
K.output = K.table = {
  plan(s) { const rows = s.rows || []; s._c = seqCues(s, rows.map((r, i) => (s.row_say && s.row_say[i]) || sayWord(r[0])), 0.15, 0.78);
    s._v = s.verdict ? Math.min(s.t1 - 0.6, Math.max(s._c[s._c.length - 1] + 0.6, s.st + s.ln * 0.85)) : null;
    return s._c.map(c => ['row', c]).concat(s._v ? [['notify', s._v]] : []); },
  draw(g, s, t, Y) {
    const y = header(g, s, t, Y); const cols = s.columns || [], rows = s.rows || [];
    const rowH = Math.min(124, (Y + 400 - y - 170) / Math.max(1, rows.length)), h = 72 + 90 + rows.length * rowH + 20;
    const pw = drop(t, s.t0 + 0.05, 0.35); if (pw <= 0) return;
    g.save(); g.globalAlpha *= clamp(pw * 2);
    const c = win(g, X0, y, CW, h, s.kind === 'output' ? `${s.tcode || 'SE16N'} · ${plain(s.title || '')}` : plain(s.title || 'Table'));
    // column widths by content
    const wds = cols.map((cn, k) => Math.max(measure(g, cn, 26, 700, 'mono'), ...rows.map(r => measure(g, String(r[k] ?? ''), 40, 600, 'mono'))) + 44);
    const tot = wds.reduce((a, b) => a + b, 0), sc = Math.min(1, (CW - 60) / tot), xs = []; let xx = X0 + 30; wds.forEach(w => { xs.push(xx); xx += w * sc; });
    cols.forEach((cn, k) => T(g, cn.toUpperCase(), xs[k], c[1] + 48, 28 * Math.max(0.8, sc), { fam: 'mono', wt: 700, color: PAL.mute }));
    g.fillStyle = PAL.line; g.fillRect(X0 + 20, c[1] + 84, CW - 40, 1);
    const hlRow = typeof s.highlight === 'number' ? s.highlight : -1;
    rows.forEach((r, i) => { const p = drop(t, s._c[i], 0.26); if (p <= 0) return; const yy = c[1] + 94 + i * rowH + rowH / 2;
      const on = i === hlRow || (hlRow < 0 && t >= s._c[i] && (i === rows.length - 1 || t < s._c[i + 1]));
      g.save(); g.globalAlpha *= clamp(p * 2); g.translate((1 - p) * 40, 0);
      if (on) { g.fillStyle = 'rgba(183,243,74,.08)'; rr(g, X0 + 14, yy - rowH / 2 + 6, CW - 28, rowH - 12, 10); g.fill(); g.fillStyle = ACC; rr(g, X0 + 14, yy - rowH / 2 + 6, 6, rowH - 12, 3); g.fill(); }
      r.forEach((v, k) => { const str = String(v ?? ''); T(g, str, xs[k], yy, fitPx(g, str, 40 * Math.max(0.75, sc), wds[k] * sc - 16, 600, 'mono'), { fam: 'mono', wt: on || k === 0 ? 700 : 500, color: on ? PAL.text : k === 0 ? '#D5D9E3' : PAL.dim }); });
      g.restore(); });
    g.restore();
    if (s._v) { const p = drop(t, s._v, 0.3); if (p > 0) { g.save(); g.globalAlpha *= clamp(p * 2); const vy = y + h + 40;
      const path = new Path2D(); path.roundRect(X0, vy, CW, 104, 52); E.litShape(g, path, { accent: true, glowR: 30, bbox: [X0, vy, CW, 104] });
      T(g, plain(s.verdict), X0 + CW / 2, vy + 53, fitPx(g, plain(s.verdict), 42, CW - 60, 700), { wt: 700, color: '#0A0B0F', align: 'center' }); g.restore(); } }
  },
};
K.chat = {
  plan(s) { const m = s.messages || []; s._c = seqCues(s, m.map(x => sayWord(x.text)), 0.05, 0.75); return s._c.map((c, i) => ['pop', c]); },
  draw(g, s, t, Y) {
    let y = header(g, s, t, Y); const m = s.messages || [];
    const hs = m.map(x => wrapTok(g, tokens(plain(x.text)), 38, 500, 700).length * 50 + 80); const tot = hs.reduce((a, b) => a + b + 24, 0);
    let yy = Math.max(y, y + (Y + 480 - y - tot)); if (tot > Y + 480 - y) yy = Y + 480 - tot;   // keep the newest at the bottom
    m.forEach((x, i) => { const p = drop(t, s._c[i], 0.3); const h = hs[i]; if (p > 0) {
      const me = /you|me|answer/i.test(x.from || ''), w = Math.min(780, Math.max(...wrapTok(g, tokens(plain(x.text)), 38, 500, 700).map(L => L.w)) + 80, measure(g, x.from || '', 24, 700, 'mono') + 80);
      const bx = me ? X0 + CW - w : X0; g.save(); g.globalAlpha *= clamp(p * 2); g.translate(0, (1 - p) * 30);
      E.panel(g, bx, yy, w, h, { r: 28, fill: me ? '#1E2A12' : PAL.surf2, stroke: me ? rgba(ACC, 0.5) : PAL.line });
      T(g, (x.from || '').toUpperCase(), bx + 34, yy + 34, 22, { fam: 'mono', wt: 700, color: me ? ACC : PAL.mute });
      rich(g, x.text, bx + 34, yy + 78, 38, { wt: 500, maxw: 700, lh: 50, color: PAL.text }); g.restore(); }
      yy += h + 24; });
  },
};
K.quiz = {
  plan(s) { const o = s.options || []; s._c = seqCues(s, o.map(sayWord), 0.18, 0.45);
    s._rev = s.reveal === false ? null : Math.min(s.t1 - 0.5, Math.max(s.st + s.ln * 0.6, cue(s, sayWord(o[s.answer || 0]), 0.72, s._c[s._c.length - 1] + 0.4)));
    s._cd = s.countdown ? [s._rev - 1.2, s._rev - 0.8, s._rev - 0.4] : [];
    return s._c.map(c => ['row', c]).concat(s._cd.map(c => ['tick', c]), s._rev ? [['snap', s._rev]] : []); },
  draw(g, s, t, Y) {
    let y = Y - 520; chip(g, 'QUIZ', X0, y, { dot: true, alpha: ss(seg(t, s.t0 - 0.1, s.t0 + 0.2)) }); y += 80;
    const h = rich(g, s.question, X0, y, 72, { wt: 700, lh: 84, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22), maxLines: 4 }); y += h + 60;
    (s.options || []).forEach((o, i) => { const p = drop(t, s._c[i], 0.3); if (p <= 0) return; const yy = y + i * 150;
      const right = s._rev && t >= s._rev && i === (s.answer || 0), wrong = s._rev && t >= s._rev && !right;
      g.save(); g.globalAlpha *= clamp(p * 2) * (wrong ? 0.4 : 1); g.translate((1 - p) * 60, 0);
      const path = new Path2D(); path.roundRect(X0, yy, CW, 124, 28); E.litShape(g, path, { accent: right, glowR: right ? 36 : 0, bbox: [X0, yy, CW, 124] });
      T(g, 'ABCD'[i], X0 + 50, yy + 63, 40, { wt: 700, fam: 'mono', color: right ? '#0A0B0F' : ACC });
      rich(g, o, X0 + 110, yy + 62, 44, { wt: 600, maxw: CW - 150, color: right ? '#0A0B0F' : PAL.text, hi: right ? '#0A0B0F' : ACC, maxLines: 1 });
      g.restore(); });
    s._cd.forEach((c, k) => { const p = seg(t, c, c + 0.4); if (p > 0 && p < 1) T(g, String(3 - k), X0 + CW - 60, Y - 520, 120 * (1.3 - p * 0.3), { wt: 700, fam: 'disp', color: rgba(ACC, 1 - p), align: 'center' }); });
  },
};
K.myth = {
  plan(s) { s._m = s.st + 0.05; s._f = cue(s, 'fact', 0.45, s.st + 0.6); return [['error', s._m], ['snap', s._f]]; },
  draw(g, s, t, Y) { K.versus.draw(g, { ...s, label: 'MYTH VS FACT', heading: s.heading || '', bad: { title: s.myth, sub: '' }, good: { title: s.fact, sub: s.detail }, _bad: s._m, _good: s._f }, t, Y); },
};
K.number = {
  plan(s) { s._n = s.t0 + 0.2; return [['digit', s._n + 0.5]]; },
  draw(g, s, t, Y) { const n = String(s.number ?? '');
    E.scramble(g, n, X0, Y - 200, t, [...n].map((c, i) => s._n + 0.4 + i * 0.09), { px: fitPx(g, n, 300, CW, 600, 'disp'), start: s._n, color: ACC });
    rich(g, s.title || '', X0, Y - 20, 64, { wt: 700, reveal: k => seg(t, s._n + 0.6 + k * 0.05, s._n + 0.9 + k * 0.05) });
    if (s.body) rich(g, s.body, X0, Y + 170, 42, { wt: 500, color: PAL.dim, reveal: () => ss(seg(t, s._n + 1.2, s._n + 1.5)) }); },
};
K.story = {
  plan(s) { const L = s.lines || []; s._c = seqCues(s, L.map(sayWord), 0.1, 0.75); return s._c.map(c => ['soft', c]); },
  draw(g, s, t, Y) { chip(g, [s.time, s.place].filter(Boolean).join(' · '), X0, Y - 600, { dot: true });
    let y = Y - 500; y += rich(g, s.heading || '', X0, y, 66, { wt: 700, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22) }) + 50;
    (s.lines || []).forEach((ln, i) => { const p = drop(t, s._c[i], 0.3); if (p <= 0) return; g.save(); g.globalAlpha *= clamp(p * 2);
      y += rich(g, ln, X0 + 30, y, 44, { wt: 500, color: '#D5D9E3', maxw: CW - 30 }) + 30; g.restore(); });
    if (s.lesson && t > s.t1 - 1.5) chip(g, plain(s.lesson), X0, Math.min(y + 40, Y + 450), { color: ACC, alpha: ss(seg(t, s.t1 - 1.5, s.t1 - 1.2)) }); },
};
K.cta = {
  plan(s) { s._f = s.t0 + 0.9; s._click = Math.min(s.t1 - 0.6, s.t0 + 1.7); const o = s.options || []; s._c = seqCues(s, o.map(sayWord), 0.25, 0.6);
    return [['pop', s._f], ['click', s._click]].concat(s._c.map(c => ['row', c])); },
  draw(g, s, t, Y) {
    let y = Y - 520; chip(g, plain(s.label || (s.options ? 'QUIZ' : 'NEXT')), X0, y, { dot: true, alpha: ss(seg(t, s.t0, s.t0 + 0.2)) }); y += 80;
    y += rich(g, s.title, X0, y, 76, { wt: 700, lh: 88, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22), maxLines: 4 }) + 30;
    if (s.body) y += rich(g, s.body, X0, y, 40, { wt: 500, color: PAL.dim, reveal: () => ss(seg(t, s.t0 + 0.4, s.t0 + 0.7)) }) + 40;
    (s.options || []).forEach((o, i) => { const p = drop(t, s._c[i], 0.3); if (p <= 0) return; const yy = y + i * 128; g.save(); g.globalAlpha *= clamp(p * 2);
      const path = new Path2D(); path.roundRect(X0, yy, CW, 108, 26); E.litShape(g, path, { bbox: [X0, yy, CW, 108] });
      T(g, 'ABCD'[i], X0 + 46, yy + 55, 38, { wt: 700, fam: 'mono', color: ACC }); rich(g, o, X0 + 100, yy + 54, 40, { wt: 600, maxw: CW - 140, maxLines: 1 }); g.restore(); });
    if (s.options) y += s.options.length * 128 + 10;
    // follow button → Following, comment pill, handle
    const fy = Math.max(y + 40, Y + 60); const pf = drop(t, s._f, 0.3);
    if (pf > 0) { g.save(); g.globalAlpha *= clamp(pf * 2); const done = t >= s._click; const bw = 420;
      const path = new Path2D(); path.roundRect(X0, fy, bw, 104, 52);
      E.litShape(g, path, { accent: !done, glowR: done ? 0 : 34, bbox: [X0, fy, bw, 104] });
      const k = Math.max(0, 1 - Math.abs(t - s._click) / 0.12);
      T(g, done ? 'Following ✓' : 'Follow', X0 + bw / 2, fy + 54, 42 * (1 - k * 0.06), { wt: 700, align: 'center', color: done ? PAL.text : '#0A0B0F' });
      T(g, S.handle, X0 + bw + 40, fy + 54, 34, { wt: 700, fam: 'mono', color: ACC });
      if (S.comment && !s.options) { const cp = drop(t, s._click + 0.4, 0.3); if (cp > 0) { g.globalAlpha *= clamp(cp * 2); chip(g, `Comment "${S.comment}"`, X0, fy + 180, { px: 30, color: PAL.text, dot: true }); } }
      g.restore();
      if (t > s._f && t < s._click + 0.5) { const p = eio(seg(t, s._f + 0.1, s._click)); pointer(g, lerp(X0 + 700, X0 + bw * 0.6, p), lerp(fy + 330, fy + 60, p), k); } }
    E.caret(g, X0 + 12, Y + 470, 60, { on: blink(t), glow: 0.8 });
  },
};
K.fallback = {
  plan(s) { s._b = s.st + 0.2; return [['soft', s._b]]; },
  draw(g, s, t, Y) { const y = header(g, s, t, Y); const b = s.body || s.text || s.subtitle || '';
    if (b) rich(g, b, X0, y + 20, 48, { wt: 500, color: '#D5D9E3', reveal: () => ss(seg(t, s._b, s._b + 0.3)) }); },
};
const kindOf = s => K[s.kind] ? s.kind : 'fallback';

// ───────── camera: track down the stack, a gentle push inside each slide ─────────
function camAt(t) {
  const n = S.slides.length; let i = 0; while (i < n - 1 && t >= S.slides[i + 1].t0) i++;
  const s = S.slides[i]; let y = s.Y, x = 540;
  const prev = S.slides[i - 1]; const tr = 0.5;
  if (prev && t < s.t0 + tr / 2) { const p = eio(seg(t, s.t0 - tr / 2, s.t0 + tr / 2)); y = lerp(prev.Y, s.Y, p); }
  const nxt = S.slides[i + 1]; if (nxt && t > nxt.t0 - tr / 2) { const p = eio(seg(t, nxt.t0 - tr / 2, nxt.t0 + tr / 2)); y = lerp(s.Y, nxt.Y, p); }
  const u = seg(t, s.t0, s.t1);
  let zoom = i === 0 ? lerp(1.05, 1.0, eo(u)) : lerp(1.0, 1.035, u);
  if (s.kind === 'cta') zoom = lerp(0.96, 1.0, eo(seg(t, s.t0, s.t0 + 0.8)));
  return E.camera({ x, y: y - 40, zoom });
}

// ───────── captions + chrome ─────────
function drawCaption(g, t) {
  const c = S.caps.find(c => t >= c.t0 - 0.04 && t < c.t1); if (!c) return;
  E.toast(g, c.text, Math.min(seg(t, c.t0 - 0.04, c.t0 + 0.12), 1), { y: 1560, px: 44, dense: 0.4 });
}
function chrome(g, t) {
  // segmented progress (one segment per slide) + series tag
  const n = S.slides.length, x0 = 60, x1 = 1020, gap = 8, w = (x1 - x0 - gap * (n - 1)) / n, y = 214;
  S.slides.forEach((s, i) => { const x = x0 + i * (w + gap); g.fillStyle = 'rgba(255,255,255,.12)'; rr(g, x, y, w, 6, 3); g.fill();
    const p = clamp((t - s.t0) / (s.t1 - s.t0)); if (p > 0) { g.fillStyle = ACC; rr(g, x, y, w * p, 6, 3); g.fill(); } });
  if (S.tag) T(g, S.tag, x0, y + 42, 26, { wt: 700, fam: 'mono', color: PAL.mute });
}

// ───────── public: init, render, events ─────────
export function init(spec) {
  S = spec; S.caps = S.caps || [];
  S.slides.forEach((s, i) => { s.i = i; s.Y = 860 + i * SLOT; s.words = s.words || []; if (!(s.ln > 0)) { s.st = s.t0 + 0.2; s.ln = Math.max(0.5, s.t1 - s.t0 - 0.6); }
    s._ev = K[kindOf(s)].plan(s) || []; });
  return S.dur;
}
export function events() {
  const ev = [];
  S.slides.forEach((s, i) => { if (i > 0) ev.push({ t: s.t0 - 0.2, type: 'move' }); s._ev.forEach(([type, t]) => ev.push({ t: Math.round(t * 1000) / 1000, type })); });
  return ev.filter(e => e.t >= 0 && e.t < S.dur).sort((a, b) => a.t - b.t);
}
export function render(g, t) {
  const cam = camAt(t);
  g.setTransform(1, 0, 0, 1, 0, 0);
  E.bg(g, { cy: H * 0.3 });
  const o0 = cam.proj(0, 0, 0); E.grid(g, { ox: o0.x, oy: o0.y, scale: cam.zoom, module: 48 });
  cam.apply(g, 0);
  S.slides.forEach(s => { if (t >= s.t0 - 0.5 && t < s.t1 + 0.5) { g.save(); K[kindOf(s)].draw(g, s, t, s.Y); g.restore(); } });
  g.setTransform(1, 0, 0, 1, 0, 0);
  E.vignette(g, 0.5);
  chrome(g, t);
  drawCaption(g, t);
}
export function texts() { return []; }
