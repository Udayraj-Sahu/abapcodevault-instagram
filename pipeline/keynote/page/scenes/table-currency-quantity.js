// Custom scene for "Tables part 9 · Currency and quantity fields" (26 Nov).
// "partner": a CURR field stands alone and fails activation (red); its CUKY reference field flies in and a cable links them; the amount gets its currency.
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
function card(g, x, y, w, h, o = {}) {     // field card: name (mono, big), type (dim), value
  const { name = '', type = '', value = '', ring = null, accent = false } = o;
  const p = new Path2D(); p.roundRect(x, y, w, h, 22);
  if (accent) E.litShape(g, p, { accent: true, glowR: 26, bbox: [x, y, w, h] }); else E.panel(g, x, y, w, h, { r: 22, fill: PAL.surf2, shadow: 0.8 });
  if (ring) { g.save(); g.strokeStyle = ring; g.lineWidth = 4; g.stroke(p); g.restore(); }
  const c = accent ? '#0A0B0F' : PAL.text;
  T(g, name, x + w / 2, y + 58, fitPx(g, name, 50, w - 40, 700, 'mono'), { fam: 'mono', wt: 700, align: 'center', color: c });
  T(g, type, x + w / 2, y + 112, 32, { fam: 'mono', wt: 500, align: 'center', color: accent ? '#1D2410' : PAL.dim });
  if (value) T(g, value, x + w / 2, y + h - 50, fitPx(g, value, 44, w - 40, 600, 'mono'), { fam: 'mono', wt: 600, align: 'center', color: accent ? '#0A0B0F' : '#D5D9E3' });
}
function pill(g, text, y, a, o = {}) {      // full-width message pill
  const { red = false, accent = false, h = 100 } = o; if (a <= 0) return;
  g.save(); g.globalAlpha *= clamp(a * 2); const yy = y + (1 - clamp(a)) * 30;
  const p = new Path2D(); p.roundRect(X0, yy, CW, h, h / 2);
  if (accent) E.litShape(g, p, { accent: true, glowR: 30, bbox: [X0, yy, CW, h] }); else { E.panel(g, X0, yy, CW, h, { r: h / 2, fill: PAL.surf2, shadow: 0.7 }); }
  if (red) { g.strokeStyle = rgba(PAL.red, 0.9); g.lineWidth = 3; g.stroke(p); mark(g, 'no', X0 + 56, yy + h / 2, 48, PAL.red); }
  const tx = red ? X0 + 100 : X0 + CW / 2, al = red ? 'left' : 'center', mw = red ? CW - 130 : CW - 60;
  T(g, text, tx, yy + h / 2 + 1, fitPx(g, text, 38, mw, 600, red ? 'mono' : 'ui'), { fam: red ? 'mono' : 'ui', wt: 600, align: al, color: accent ? '#0A0B0F' : (red ? '#FFB3B5' : PAL.text) });
  g.restore();
}
const partner = {
  plan(s) { s._f = Math.max(s.t0 + 0.9, cue(s, s.say_fail || 'refuses', 0.3, s.t0)); s._r = Math.max(s._f + 0.6, cue(s, s.say_ref || 'reference', 0.6, s._f));
    s._l = Math.max(s._r + 0.6, cue(s, s.say_link || 'holds', 0.85, s._r));
    return [['pop', s.t0 + 0.2], ['error', s._f], ['fly', s._r], ['land', s._r + 0.4], ['snap', s._l], ['glint', s._l + 0.2]]; },
  cam(s, t) { const u = seg(t, s._f, s._f + 0.3); return { zoom: lerp(1, 1.03, seg(t, s.t0, s._l)), sx: u > 0 && u < 1 ? Math.sin(t * 90) * 10 * (1 - u) : 0 }; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 60, w = 400, h = 240, gap = CW - 2 * w;
    const f = s.field || {}, r = s.ref || {};
    const fail = t >= s._f ? 1 - seg(t, s._l, s._l + 0.4) : 0;
    // the CURR field: centred alone, slides left when its partner arrives
    const mv = eio(seg(t, s._r, s._r + 0.5)), fx = lerp(540 - w / 2, X0, mv);
    const a = drop(t, s.t0 + 0.1, 0.35); g.save(); g.globalAlpha *= clamp(a * 2);
    card(g, fx, y0, w, h, { name: f.name, type: f.type, value: t >= s._l + 0.2 ? (f.value || '') + ' ' + (r.value || '') : (f.value || '') + ' ???', ring: fail > 0 ? rgba(PAL.red, 0.9 * fail) : null });
    g.restore();
    // the reference field flies in from the right
    if (t > s._r - 0.05) { const p = eo(seg(t, s._r, s._r + 0.5)), rx = lerp(1200, X0 + w + gap, p);
      g.save(); g.globalAlpha *= clamp(p * 2); card(g, rx, y0, w, h, { name: r.name, type: r.type, value: r.value, accent: t >= s._l }); g.restore();
      T(g, 'reference field', rx + w / 2, y0 + h + 44, 30, { fam: 'mono', wt: 600, align: 'center', color: PAL.dim, alpha: clamp(p * 2) }); }
    // the cable
    if (t >= s._l) { const p = eo(seg(t, s._l, s._l + 0.35)), x1 = X0 + w, x2 = X0 + w + gap, cy = y0 + h / 2;
      g.save(); g.strokeStyle = ACC; g.lineWidth = 8; g.lineCap = 'round'; E.glow(g, lerp(x1, x2, p), cy, 40, ACC, 0.5);
      g.beginPath(); g.moveTo(x1 + 6, cy); g.lineTo(lerp(x1 + 6, x2 - 6, p), cy); g.stroke(); g.restore(); }
    // messages
    const my = y0 + h + 120;
    pill(g, plain(s.fail_text || 'activation error: no reference field'), my, drop(t, s._f, 0.3) * fail, { red: true });
    pill(g, plain(s.link_text || ((f.name || '') + ' → ' + (r.name || '') + ' · activates')), my, drop(t, s._l + 0.25, 0.3), { accent: true });
  },
};
export default { partner };
