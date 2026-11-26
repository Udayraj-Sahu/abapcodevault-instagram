// Custom scene for "Tables part 13 · Foreign key and check table" (27 Nov).
// "gate": values head for ZTAIRLINE-COUNTRY through the check table T005; DE is found and passes, XX bounces off with the check-entry error.
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
const gate = {
  plan(s) { s._g = s.t0 + 0.25; s._gl = Math.max(s.t0 + 0.6, cue(s, s.say_gate || 'T005', 0.3, s.t0)); s._ok = Math.max(s._g + 0.6, cue(s, s.say_ok || 'DE', 0.6, s._g));
    s._bad = Math.max(s._ok + 1.0, cue(s, s.say_bad || 'XX', 0.8, s._ok)); s._hit = s._bad + 0.5;
    return [['snap', s._g], ['glint', s._gl], ['fly', s._ok], ['ping', s._ok + 0.5], ['land', s._ok + 0.9], ['fly', s._bad], ['bump', s._hit], ['error', s._hit + 0.15]]; },
  cam(s, t) { const u = seg(t, s._hit, s._hit + 0.3); return { sx: u > 0 && u < 1 ? Math.sin(t * 90) * 9 * (1 - u) : 0 }; },
  draw(g, s, t) {
    const y0 = head(g, s, t), gy = y0 + 200, ty = gy + 330;
    const vals = s.values || ['DE', 'US', 'IN', 'FR'];
    // check table T005 = the gate
    const ga = drop(t, s._g, 0.35); if (ga > 0) { g.save(); g.globalAlpha *= clamp(ga * 2);
      const p = new Path2D(); p.roundRect(X0, gy, CW, 190, 26); E.panel(g, X0, gy, CW, 190, { r: 26, fill: PAL.surf2, shadow: 0.8 });
      const okFlash = 1 - seg(t, s._ok + 0.5, s._ok + 1.2), badFlash = 1 - seg(t, s._hit, s._hit + 0.9);
      const gl = seg(t, s._gl, s._gl + 0.25) * (1 - seg(t, s._gl + 0.6, s._gl + 1.1)); if (gl > 0) { g.strokeStyle = rgba(ACC, 0.8 * gl); g.lineWidth = 4; g.stroke(p); }
      if (t > s._ok + 0.45 && okFlash > 0) { g.strokeStyle = rgba(ACC, okFlash); g.lineWidth = 4; g.stroke(p); }
      if (t > s._hit && badFlash > 0) { g.strokeStyle = rgba(PAL.red, badFlash); g.lineWidth = 4; g.stroke(p); }
      icon(g, 'table', X0 + 60, gy + 52, 44, PAL.dim); T(g, 'check table ' + (s.check || 'T005'), X0 + 110, gy + 52, 32, { fam: 'mono', wt: 700, color: PAL.dim });
      const w = (CW - 60 - (vals.length - 1) * 20) / vals.length;
      vals.forEach((v, i) => cell(g, X0 + 30 + i * (w + 20), gy + 95, w, 70, v, { ring: i === 0 && t > s._ok + 0.45 && okFlash > 0 ? ACC : null })); g.restore(); }
    // the target field
    const ta = drop(t, s.t0 + 0.1, 0.35); g.save(); g.globalAlpha *= clamp(ta * 2);
    E.panel(g, X0, ty, CW, 160, { r: 26, fill: PAL.surf3, shadow: 0.8 });
    T(g, (s.table || 'ZTAIRLINE') + '-' + (s.field || 'COUNTRY'), X0 + 40, ty + 80, 36, { fam: 'mono', wt: 700 });
    if (t > s._ok + 0.9) { cell(g, X0 + CW - 260, ty + 40, 140, 80, 'DE', { accent: true }); mark(g, 'ok', X0 + CW - 70, ty + 80, 52, ACC); }
    g.restore();
    // the values travelling
    const lane = 540;
    const pk = (txt, y, red) => { cell(g, lane - 80, y - 40, 160, 80, txt, { ring: red ? PAL.red : ACC, fill: PAL.surf3, color: red ? '#FFB3B5' : PAL.text }); };
    if (t >= s._ok && t < s._ok + 0.9) { const u = seg(t, s._ok, s._ok + 0.9); pk(s.ok_val || 'DE', lerp(y0 + 60, ty + 80, eio(u)), false); }
    if (t >= s._bad) { const u = seg(t, s._bad, s._hit), b = seg(t, s._hit, s._hit + 0.5);
      const y = t < s._hit ? lerp(y0 + 60, gy - 30, eio(u)) : lerp(gy - 30, y0 + 80, eo(b)) - Math.sin(b * Math.PI) * 30; pk(s.bad_val || 'XX', y, t >= s._hit); }
    if (t > s._hit + 0.15) pill(g, s.err || 'Entry XX does not exist in T005 (check entry)', ty + 220, drop(t, s._hit + 0.15, 0.3), { red: true });
  },
};
export default { gate };
