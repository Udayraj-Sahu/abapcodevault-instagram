// Custom scene for "Tables part 14 · Cardinality" (27 Nov).
// "links": T005 countries on the left, ZTAIRLINE airlines on the right; each airline draws exactly one line to its country, US collects two, FR none; 1 and CN badges land on the sides.
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
const links = {
  plan(s) { s._1 = Math.max(s.t0 + 0.5, cue(s, s.say_one || 'exactly', 0.2, s.t0)); s._l = Math.max(s._1 + 0.4, cue(s, s.say_left || 'left', 0.35, s._1));
    s._m = Math.max(s._l + 0.4, cue(s, s.say_many || 'many', 0.55, s._l)); s._z = Math.max(s._m + 0.4, cue(s, s.say_none || 'none', 0.7, s._m));
    s._r = Math.max(s._z + 0.4, cue(s, s.say_right || 'right', 0.9, s._z));
    return [['draw', s._1], ['draw', s._1 + 0.2], ['draw', s._1 + 0.4], ['snap', s._l], ['glint', s._m], ['ping', s._z], ['snap', s._r]]; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 90;
    const C = s.countries || ['DE', 'US', 'FR'], A = s.airlines || [['LH', 'DE'], ['AA', 'US'], ['UA', 'US']];
    const lx = X0, lw = 300, rx = X0 + CW - 380, rw = 380, h = 110, gap = 40;
    T(g, s.left || 'T005', lx + lw / 2, y0 - 30, 30, { fam: 'mono', wt: 700, color: PAL.dim, align: 'center' });
    T(g, s.right_t || 'ZTAIRLINE', rx + rw / 2, y0 - 30, 30, { fam: 'mono', wt: 700, color: PAL.dim, align: 'center' });
    const cy = i => y0 + 20 + i * (h + gap), ay = i => y0 + 20 + i * (h + gap);
    // lines
    A.forEach((a, i) => { const ci = C.indexOf(a[1]); if (ci < 0) return; const p = seg(t, s._1 + i * 0.2, s._1 + i * 0.2 + 0.4); if (p <= 0) return;
      const x1 = rx, y1 = ay(i) + h / 2, x2 = lx + lw, y2 = cy(ci) + h / 2, glowUS = a[1] === (s.many || 'US') && t >= s._m;
      g.save(); g.strokeStyle = glowUS ? ACC : 'rgba(232,234,240,.55)'; g.lineWidth = glowUS ? 5 : 3; g.beginPath(); g.moveTo(x1, y1);
      g.lineTo(lerp(x1, x2, eio(p)), lerp(y1, y2, eio(p))); g.stroke(); g.restore(); });
    C.forEach((c, i) => { const a = drop(t, s.t0 + 0.05 + i * 0.08, 0.3); if (a <= 0) return; const many = c === (s.many || 'US') && t >= s._m, none = c === (s.none_c || 'FR') && t >= s._z;
      g.save(); g.globalAlpha *= clamp(a * 2); cell(g, lx, cy(i), lw, h, c, { px: 44, accent: many, ring: none ? 'rgba(232,234,240,.35)' : null }); g.restore();
      if (none) T(g, '0 airlines · OK', lx + 10, cy(i) + h + 30, 28, { fam: 'mono', wt: 600, color: PAL.dim, alpha: ss(seg(t, s._z, s._z + 0.3)) }); });
    A.forEach((a, i) => { const p = drop(t, s.t0 + 0.2 + i * 0.08, 0.3); if (p <= 0) return; g.save(); g.globalAlpha *= clamp(p * 2);
      cell(g, rx, ay(i), rw, h, a[0] + ' · ' + a[1], { px: 40 }); g.restore(); });
    // badges
    const by = y0 + 20 + 3 * (h + gap) + 40;
    const b1 = drop(t, s._l, 0.3), b2 = drop(t, s._r, 0.3);
    if (b1 > 0) pill(g, 'left: 1', by, b1, { accent: true, x: lx, w: 420, h: 110 });
    if (b2 > 0) pill(g, 'right: CN', by, b2, { accent: true, x: X0 + CW - 420, w: 420, h: 110 });
  },
};
export default { links };
