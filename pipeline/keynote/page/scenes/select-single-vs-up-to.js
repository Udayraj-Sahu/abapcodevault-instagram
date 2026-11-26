// Custom scene for "SELECT SINGLE vs UP TO 1 ROWS" (27 Nov).
// "anyrow": three VBAK orders of one customer; SELECT SINGLE with only part of the key shuffles between them and lands on a random one, while the newest order (the one you wanted) is tagged.
import { H_ } from '../reel.js';
import { sy, icon } from '../moments.js';
const { E, T, measure, fitPx, rich, chip, drop, cue, plain, mark, X0, CW, ACC } = H_;
const { PAL, clamp, lerp, seg, ss, eo, eio, back, rr, rgba, TAU } = E;
function head(g, s, t) {
  let y = sy(s, 330);
  if (s.label) { chip(g, plain(s.label), X0, y, { alpha: ss(seg(t, s.t0 - 0.1, s.t0 + 0.15)) }); y += 70; }
  if (s.heading) y += rich(g, s.heading, X0, y + 10, 68, { wt: 700, maxLines: 2, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22) }) + 50;
  return y;
}
function pill(g, text, y, a, o = {}) {
  const { red = false, accent = false, h = 100, x = X0, w = CW } = o; if (a <= 0) return;
  g.save(); g.globalAlpha *= clamp(a * 2); const yy = y + (1 - clamp(a)) * 30;
  const p = new Path2D(); p.roundRect(x, yy, w, h, h / 2);
  if (accent) E.litShape(g, p, { accent: true, glowR: 30, bbox: [x, yy, w, h] }); else E.panel(g, x, yy, w, h, { r: h / 2, fill: PAL.surf2, shadow: 0.7 });
  if (red) { g.strokeStyle = rgba(PAL.red, 0.9); g.lineWidth = 3; g.stroke(p); mark(g, 'no', x + 56, yy + h / 2, 48, PAL.red); }
  const tx = red ? x + 100 : x + w / 2, al = red ? 'left' : 'center', mw = red ? w - 130 : w - 60;
  T(g, text, tx, yy + h / 2 + 1, fitPx(g, text, 38, mw, 600, red ? 'mono' : 'ui'), { fam: red ? 'mono' : 'ui', wt: 600, align: al, color: accent ? '#0A0B0F' : (red ? '#FFB3B5' : PAL.text) });
  g.restore();
}
function cell(g, x, y, w, h, txt, o = {}) {
  const { ring = null, fill = 'rgba(255,255,255,.045)', color = '#D5D9E3', px = 34, alpha = 1, accent = false } = o;
  g.save(); g.globalAlpha *= alpha;
  if (accent) { const p = new Path2D(); p.roundRect(x, y, w, h, 12); E.litShape(g, p, { accent: true, glowR: 16, bbox: [x, y, w, h] }); }
  else { g.fillStyle = fill; rr(g, x, y, w, h, 12); g.fill(); }
  if (ring) { g.strokeStyle = ring; g.lineWidth = 3; rr(g, x + 1, y + 1, w - 2, h - 2, 12); g.stroke(); }
  T(g, String(txt), x + w / 2, y + h / 2 + 1, fitPx(g, String(txt), px, w - 20, 600, 'mono'), { fam: 'mono', wt: 600, align: 'center', color: accent ? '#0A0B0F' : color });
  g.restore();
}
const anyrow = {
  plan(s) { s._k = Math.max(s.t0 + 0.4, cue(s, s.say_full || 'full', 0.12, s.t0)); s._p = Math.max(s._k + 0.5, cue(s, s.say_part || 'part', 0.4, s._k));
    s._r = Math.max(s._p + 1.0, cue(s, s.say_rand || 'random', 0.65, s._p)); s._n = Math.max(s._r + 0.4, cue(s, s.say_new || 'newest', 0.85, s._r));
    const ev = [['key', s._k], ['pop', s._p]]; for (let i = 0; i < 6; i++) ev.push(['tick', lerp(s._p + 0.1, s._r, i / 6)]);
    return ev.concat([['land', s._r], ['error', s._n]]); },
  draw(g, s, t) {
    const y0 = head(g, s, t);
    // the WHERE line
    const wa = drop(t, s.t0 + 0.05, 0.3); g.save(); g.globalAlpha *= clamp(wa * 2);
    E.panel(g, X0, y0, CW, 110, { r: 20, fill: PAL.surf2, shadow: 0.6 });
    T(g, 'SELECT SINGLE … WHERE', X0 + 30, y0 + 56, 34, { fam: 'mono', wt: 600, color: PAL.dim });
    const kp = ss(seg(t, s._k, s._k + 0.3)), pp = ss(seg(t, s._p, s._p + 0.3));
    T(g, pp > 0.5 ? (s.part_key || 'kunnr = 1000') : (s.full_key || 'vbeln = 4712'), X0 + 520, y0 + 56, fitPx(g, 'kunnr = 1000', 38, CW - 540, 700, 'mono'), { fam: 'mono', wt: 700, color: pp > 0.5 ? PAL.red : ACC, alpha: Math.max(kp, pp) });
    g.restore();
    const rows = s.rows || [['4711', '02.10.2026'], ['4712', '15.11.2026'], ['4713', '20.08.2026']], newest = s.newest ?? 1, pick = s.pick ?? 2;
    const a = drop(t, s.t0 + 0.15, 0.35); g.save(); g.globalAlpha *= clamp(a * 2);
    const r = E.windowBox(g, X0, y0 + 150, CW, 120 + rows.length * 100, { title: 'VBAK · customer 1000', app: 6, bar: 72 });
    T(g, 'VBELN', r[0] + 200, r[1] + 40, 26, { fam: 'mono', wt: 700, color: PAL.dim, align: 'center' }); T(g, 'ERDAT', r[0] + 550, r[1] + 40, 26, { fam: 'mono', wt: 700, color: PAL.dim, align: 'center' });
    // which row is "lit": full key -> the 4712 row; part key -> shuffling, then lands on `pick`
    let lit = -1; if (t >= s._k && t < s._p) lit = 1;
    if (t >= s._p && t < s._r) lit = Math.floor((t - s._p) * 7) % rows.length; if (t >= s._r) lit = pick;
    rows.forEach((rw, i) => { const ry = r[1] + 76 + i * 100, on = i === lit;
      cell(g, r[0] + 30, ry, 340, 80, rw[0], { accent: on && t < s._r && t >= s._k && t < s._p ? true : false, ring: on ? (t >= s._r ? PAL.red : ACC) : null });
      cell(g, r[0] + 400, ry, 300, 80, rw[1], { ring: on ? (t >= s._r ? PAL.red : ACC) : null });
      if (i === newest && t >= s._n) { const q = drop(t, s._n, 0.3); g.save(); g.globalAlpha *= clamp(q * 2); chip(g, 'newest', r[0] + 720, ry + 40, { px: 24, color: ACC, dot: true }); g.restore(); } });
    g.restore();
    const by = y0 + 150 + 120 + rows.length * 100 + 40;
    if (t >= s._k && t < s._p) pill(g, 'full key → exactly one row', by, drop(t, s._k, 0.3), { accent: true });
    if (t >= s._r) pill(g, 'part of the key → a random row', by, drop(t, s._r, 0.3), { red: true });
  },
};
export default { anyrow };
