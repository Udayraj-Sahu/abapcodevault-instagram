// Custom scenes for "Tables part 16 · Table key points" (28 Nov).
// "keyorder": a key field sits under a non-key field (red, not allowed); the key fields slide to the top, MANDT lands first.
// "activate": Activate is pressed in SE11, a beam drops into the database and the same table with the same fields appears there.
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
function box(g, x, y, on, a = 1) { g.save(); g.globalAlpha *= a; g.strokeStyle = on ? ACC : 'rgba(232,234,240,.4)'; g.lineWidth = 3; rr(g, x, y, 36, 36, 8); g.stroke();
  if (on) { g.lineWidth = 5; g.beginPath(); g.moveTo(x + 8, y + 19); g.lineTo(x + 15, y + 27); g.lineTo(x + 29, y + 10); g.stroke(); } g.restore(); }
const keyorder = {
  plan(s) { s._e = Math.max(s.t0 + 0.6, cue(s, s.say_err || 'top', 0.3, s.t0)); s._f = Math.max(s._e + 0.8, cue(s, s.say_fix || 'first', 0.5, s._e));
    s._m = Math.max(s._f + 0.8, cue(s, s.say_m || 'MANDT', 0.85, s._f));
    return [['error', s._e], ['fly', s._f], ['land', s._f + 0.6], ['snap', s._m]]; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 10, rows = s.rows || [['CARRNAME', false], ['MANDT', true], ['CARRID', true], ['COUNTRY', false]];
    const fixed = [...rows].sort((a, b) => (b[1] - a[1]));
    const rh = 92, H = 90 + rows.length * rh + 20;
    if (card(g, X0, y0, CW, H, drop(t, s.t0 + 0.05, 0.35))) {
      T(g, (s.table || 'ZTAIRLINE') + ' · Fields', X0 + 40, y0 + 46, 32, { fam: 'mono', wt: 700, color: PAL.dim });
      T(g, 'Key', X0 + CW - 120, y0 + 46, 28, { fam: 'mono', wt: 700, color: PAL.dim, align: 'center' });
      const u = eio(seg(t, s._f, s._f + 0.6));
      rows.forEach((r, i) => { const j = fixed.indexOf(r), y = y0 + 90 + lerp(i, j, u) * rh, bad = t >= s._e && t < s._f && i === 1, first = t >= s._m && j === 0;
        cell(g, X0 + 30, y, CW - 220, rh - 18, r[0], { px: 34, align: 'left', ring: bad ? PAL.red : null, accent: first });
        box(g, X0 + CW - 138, y + (rh - 18) / 2 - 18, r[1]);
        if (first) T(g, '1st', X0 + CW - 290, y + (rh - 18) / 2, 30, { fam: 'mono', wt: 700, color: '#0A0B0F', alpha: ss(seg(t, s._m, s._m + 0.3)) }); });
      g.restore(); }
    const py = y0 + H + 50;
    if (t >= s._e && t < s._f + 0.2) { g.save(); g.globalAlpha *= 1 - seg(t, s._f, s._f + 0.2); pill(g, 'a key field below a normal field', py, drop(t, s._e, 0.3), { red: true }); g.restore(); }
    if (t >= s._f + 0.6) pill(g, t >= s._m ? 'keys on top · MANDT first' : 'keys on top', py, drop(t, s._f + 0.6, 0.3), { accent: t >= s._m });
  },
};
const activate = {
  plan(s) { s._p = Math.max(s.t0 + 0.4, cue(s, s.say_p || 'activate', 0.12, s.t0)); s._db = Math.max(s._p + 0.6, cue(s, s.say_db || 'creates', 0.35, s._p));
    s._same = Math.max(s._db + 0.6, cue(s, s.say_same || 'same', 0.6, s._db)); s._tr = Math.max(s._same + 0.8, cue(s, s.say_tr || 'transparent', 0.88, s._same));
    return [['press', s._p], ['shimmer', s._db], ['row', s._same], ['row', s._same + 0.15], ['row', s._same + 0.3], ['row', s._same + 0.45], ['glint', s._tr]]; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 10, tab = s.table || 'ZTAIRLINE', F = s.fields || ['MANDT', 'CARRID', 'CARRNAME', 'COUNTRY'];
    if (card(g, X0, y0, CW, 170, drop(t, s.t0 + 0.05, 0.35))) {
      T(g, 'SE11 · Table ' + tab, X0 + 40, y0 + 52, 32, { fam: 'mono', wt: 700, color: PAL.dim });
      const on = t >= s._p + 0.2; T(g, on ? 'Status: active' : 'Status: inactive', X0 + 40, y0 + 118, 32, { fam: 'mono', wt: 600, color: on ? ACC : '#FFB3B5' });
      const pr = seg(t, s._p - 0.1, s._p) * (1 - seg(t, s._p + 0.1, s._p + 0.25));
      H_.E && (function () { g.save(); const bx = X0 + CW - 290, by = y0 + 50, k = 1 - pr * 0.08; g.translate(bx + 120, by + 40); g.scale(k, k);
        const p = new Path2D(); p.roundRect(-120, -40, 240, 80, 16); if (on) E.litShape(g, p, { accent: true, glowR: 18, bbox: [-120, -40, 240, 80] }); else E.panel(g, -120, -40, 240, 80, { r: 16, fill: PAL.surf3, shadow: 0.6 });
        T(g, 'Activate', 0, 1, 32, { wt: 700, align: 'center', color: on ? '#0A0B0F' : PAL.text }); g.restore(); })();
      g.restore(); }
    // beam
    const bt = seg(t, s._db - 0.2, s._db + 0.3), dy = y0 + 280;
    if (bt > 0) { g.save(); g.strokeStyle = rgba(ACC, 0.8); g.lineWidth = 5; g.setLineDash([14, 12]); g.beginPath(); g.moveTo(540, y0 + 180); g.lineTo(540, lerp(y0 + 180, dy, eo(bt))); g.stroke(); g.restore(); }
    // database
    const da = drop(t, s._db, 0.35);
    if (card(g, X0, dy, CW, 330, da, { fill: PAL.surf3 })) {
      icon(g, 'db', X0 + 60, dy + 52, 46, ACC); T(g, 'database table ' + tab, X0 + 110, dy + 52, 32, { fam: 'mono', wt: 700 });
      const w = (CW - 60 - (F.length - 1) * 12) / F.length;
      F.forEach((f, i) => { const a = drop(t, s._same + i * 0.15, 0.3); if (a <= 0) return; g.save(); g.globalAlpha *= clamp(a * 2);
        cell(g, X0 + 30 + i * (w + 12), dy + 110, w, 70, f, { px: 26 });
        for (let r = 0; r < 2; r++) { g.fillStyle = 'rgba(255,255,255,.05)'; rr(g, X0 + 30 + i * (w + 12), dy + 195 + r * 56, w, 44, 10); g.fill(); }
        g.restore(); });
      g.restore(); }
    if (t >= s._tr) pill(g, 'transparent table: 1 SE11 table = 1 database table', dy + 390, drop(t, s._tr, 0.3), { accent: true });
  },
};
export default { keyorder, activate };
