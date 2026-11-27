// Custom scenes for "Tables part 17 · Mistakes + interview" (28 Nov).
// "mistakes": four red mistake cards land on their number word, each consequence types in when it is spoken.
// "proposal": the domain LAND1 proposes value table T005; the foreign key makes T005 the real check table (lock).
import { H_ } from '../reel.js';
import { sy, icon } from '../moments.js';
const { E, T, measure, fitPx, rich, chip, drop, cue, seqCues, plain, mark, pointer, X0, CW, ACC } = H_;
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
  const { ring = null, fill = 'rgba(255,255,255,.045)', color = '#D5D9E3', px = 34, alpha = 1, accent = false, align = 'center' } = o;
  g.save(); g.globalAlpha *= alpha;
  if (accent) { const p = new Path2D(); p.roundRect(x, y, w, h, 12); E.litShape(g, p, { accent: true, glowR: 16, bbox: [x, y, w, h] }); }
  else { g.fillStyle = fill; rr(g, x, y, w, h, 12); g.fill(); }
  if (ring) { g.strokeStyle = ring; g.lineWidth = 3; rr(g, x + 1, y + 1, w - 2, h - 2, 12); g.stroke(); }
  const tx = align === 'left' ? x + 24 : x + w / 2;
  T(g, String(txt), tx, y + h / 2 + 1, fitPx(g, String(txt), px, w - 40, 600, 'mono'), { fam: 'mono', wt: 600, align, color: accent ? '#0A0B0F' : color });
  g.restore();
}
function card(g, x, y, w, h, a, o = {}) { if (a <= 0) return false; g.save(); g.globalAlpha *= clamp(a * 2); g.translate(0, (1 - clamp(a)) * 30);
  E.panel(g, x, y, w, h, { r: 24, fill: o.fill || PAL.surf2, shadow: 0.8 }); if (o.ring) { g.strokeStyle = o.ring; g.lineWidth = 3; rr(g, x + 1, y + 1, w - 2, h - 2, 24); g.stroke(); } return true; }
const mistakes = {
  plan(s) { const M = s.items; s._c = seqCues(s, M.flatMap(m => [m.say, m.say_c]), 0.05, 0.92);
    return s._c.map((c, i) => [i % 2 ? 'tick' : 'land', c]).concat([['error', s._c[s._c.length - 1] + 0.1]]); },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 10, M = s.items, rh = 178;
    M.forEach((m, i) => { const ta = s._c[2 * i], tc = s._c[2 * i + 1], y = y0 + i * (rh + 16);
      if (!card(g, X0, y, CW, rh, drop(t, ta, 0.3), { ring: rgba(PAL.red, 0.7) })) return;
      T(g, String(i + 1), X0 + 56, y + rh / 2, 56, { fam: 'mono', wt: 700, color: PAL.red, align: 'center' });
      T(g, m.title, X0 + 120, y + 62, fitPx(g, m.title, 40, CW - 160, 700, 'ui'), { wt: 700 });
      if (t >= tc) { const n = Math.floor(m.cons.length * ss(seg(t, tc, tc + 0.5))); T(g, '→ ' + m.cons.slice(0, n), X0 + 120, y + 126, fitPx(g, '→ ' + m.cons, 32, CW - 160, 600, 'mono'), { fam: 'mono', wt: 600, color: '#FFB3B5' }); }
      g.restore(); });
  },
};
const proposal = {
  plan(s) { s._d = Math.max(s.t0 + 0.4, cue(s, s.say_d || 'domain', 0.2, s.t0)); s._p = Math.max(s._d + 0.8, cue(s, s.say_p || 'proposal', 0.45, s._d));
    s._c = Math.max(s._p + 0.6, cue(s, s.say_c || 'check', 0.65, s._p)); s._r = Math.max(s._c + 0.6, cue(s, s.say_r || 'really', 0.85, s._c));
    return [['pop', s._d], ['draw', s._p], ['land', s._c], ['snap', s._r]]; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 10;
    if (card(g, X0, y0, CW, 190, drop(t, s._d, 0.35))) {
      T(g, 'Domain ' + (s.domain || 'LAND1'), X0 + 40, y0 + 50, 32, { fam: 'mono', wt: 700, color: PAL.dim });
      cell(g, X0 + 30, y0 + 90, CW - 60, 72, 'Value table: ' + (s.vt || 'T005'), { px: 34, align: 'left' }); g.restore(); }
    const p = seg(t, s._p, s._p + 0.5), ay = y0 + 200;
    if (p > 0) { g.save(); g.strokeStyle = 'rgba(232,234,240,.6)'; g.lineWidth = 4; g.setLineDash([12, 12]); g.beginPath(); g.moveTo(540, ay); g.lineTo(540, ay + 130 * eo(p)); g.stroke(); g.restore();
      T(g, 'proposes', 570, ay + 66, 30, { fam: 'mono', wt: 600, color: PAL.dim, alpha: ss(p) }); }
    const fy = ay + 150, on = t >= s._c;
    if (card(g, X0, fy, CW, 190, drop(t, s._p + 0.35, 0.35), { ring: on ? rgba(ACC, 0.9) : null })) {
      T(g, 'Foreign key ' + (s.field || 'ZTAIRLINE-COUNTRY'), X0 + 40, fy + 50, fitPx(g, 'Foreign key ' + (s.field || 'ZTAIRLINE-COUNTRY'), 32, CW - 80, 700, 'mono'), { fam: 'mono', wt: 700, color: PAL.dim });
      cell(g, X0 + 30, fy + 90, CW - 160, 72, 'Check table: ' + (s.vt || 'T005'), { px: 34, align: 'left', accent: on });
      icon(g, on ? 'lock' : 'open', X0 + CW - 70, fy + 126, 50, on ? ACC : PAL.dim); g.restore(); }
    if (t >= s._r) pill(g, 'value table = proposal · check table = the check', fy + 250, drop(t, s._r, 0.3), { accent: true });
  },
};
export default { mistakes, proposal };
