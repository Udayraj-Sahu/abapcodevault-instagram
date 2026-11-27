// Custom scene for "BINARY SEARCH on an unsorted table" (28 Nov, 1 PM).
// "halving": binary search checks the middle row and throws half away; unsorted, it throws away the half with 1000 (sy-subrc 4); sorted (sorted: true), it finds it in two checks (sy-subrc 0).
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
const halving = {
  plan(s) {
    const srt = !!s.sorted;
    const k = srt ? [s.say1 || 'middle', s.say2 || 'left', s.say3 || 'found', s.say4 || 'zero'] : [s.say1 || 'middle', s.say2 || 'throws', s.say3 || 'wrong', s.say4 || 'four'];
    [s._1, s._2, s._3, s._4] = seqCues(s, k, 0.15, 0.85);
    return [['ping', s._1], ['snap', s._2], ['ping', s._3], [srt ? 'glint' : 'error', s._4]]; },
  cam(s, t) { if (s.sorted) return {}; const u = seg(t, s._4, s._4 + 0.3); return { sx: u > 0 && u < 1 ? Math.sin(t * 90) * 8 * (1 - u) : 0 }; },
  draw(g, s, t) {
    const srt = !!s.sorted, V = s.values || (srt ? ['1000', '2000', '3000', '4000', '5000'] : ['3000', '1000', '5000', '2000', '4000']);
    const tgt = s.target || '1000', ti = V.indexOf(tgt);
    const y0 = head(g, s, t) + 20, rh = 104, rx = X0 + 150, rw = CW - 300;
    T(g, (s.itab || 'lt_kna1') + (srt ? '  · sorted by kunnr' : '  · not sorted'), X0, y0, 30, { fam: 'mono', wt: 600, color: PAL.dim });
    // search state: first check = middle of all (index 2); keep left 0..1; second check = index 0
    const m1 = 2, m2 = 0;
    const dropped = i => (t >= s._2 && i >= m1) || (!srt && t >= s._3 + 0.5 && i === m2);
    V.forEach((v, i) => { const y = y0 + 40 + i * rh, a = drop(t, s.t0 + 0.05 + i * 0.07, 0.3); if (a <= 0) return;
      const isT = i === ti, found = srt && isT && t >= s._3, skipped = !srt && isT && t >= s._4;
      g.save(); g.globalAlpha *= clamp(a * 2) * (dropped(i) && !found ? 0.28 : 1);
      cell(g, rx, y, rw, rh - 20, 'KUNNR ' + v, { px: 36, accent: found, ring: skipped ? PAL.red : (isT && !found ? 'rgba(232,234,240,.35)' : null) });
      if (dropped(i) && !found) { g.strokeStyle = 'rgba(232,234,240,.6)'; g.lineWidth = 3; g.beginPath(); g.moveTo(rx + 20, y + (rh - 20) / 2); g.lineTo(rx + 20 + (rw - 40) * ss(seg(t, i >= m1 ? s._2 : s._3 + 0.5, (i >= m1 ? s._2 : s._3 + 0.5) + 0.3)), y + (rh - 20) / 2); g.stroke(); }
      g.restore();
      if (skipped) T(g, 'never checked', rx + rw + 20, y + (rh - 20) / 2, 26, { fam: 'mono', wt: 600, color: '#FFB3B5', alpha: ss(seg(t, s._4, s._4 + 0.3)) });
    });
    // the pointer: first check, then second check
    const at = t < s._1 ? -1 : (t < s._3 ? m1 : m2);
    if (at >= 0) { const yy = y0 + 40 + at * rh + (rh - 20) / 2, mv = seg(t, s._3, s._3 + 0.35), yA = y0 + 40 + m1 * rh + (rh - 20) / 2, yB = y0 + 40 + m2 * rh + (rh - 20) / 2;
      const py = t < s._3 ? yA : lerp(yA, yB, eio(mv));
      g.save(); g.globalAlpha *= ss(seg(t, s._1, s._1 + 0.2)); g.fillStyle = ACC; g.beginPath(); g.moveTo(rx - 30, py); g.lineTo(rx - 80, py - 26); g.lineTo(rx - 80, py + 26); g.closePath(); g.fill(); g.restore();
      T(g, 'check', X0, py - 50, 24, { fam: 'mono', wt: 700, color: ACC, alpha: ss(seg(t, s._1, s._1 + 0.2)) }); }
    const ny = y0 + 40 + V.length * rh + 10;
    const note1 = tgt + ' < ' + V[m1] + ' → keep the left half', note2 = srt ? tgt + ' = ' + V[m2] + ' → found' : tgt + ' < ' + V[m2] + ' → nothing left';
    if (t >= s._1 + 0.3) T(g, t < s._3 ? note1 : note2, X0, ny, 32, { fam: 'mono', wt: 600, color: PAL.text, alpha: ss(seg(t, t < s._3 ? s._1 + 0.3 : s._3, (t < s._3 ? s._1 : s._3) + 0.6)) });
    if (t >= s._4) pill(g, srt ? 'sy-subrc = 0 · found in 2 checks' : 'sy-subrc = 4 · but ' + tgt + ' is in the table', ny + 60, drop(t, s._4, 0.3), srt ? { accent: true } : { red: true });
  },
};
export default { halving };
