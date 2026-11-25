// Custom scene for "BAPI missing commit" (26 Nov).
// "ghost": RETURN shows a green success message, the program ends, the order card turns into a dashed ghost and VA03 answers with a red error.
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
const ghost = {
  plan(s) { s._m = Math.max(s.t0 + 0.5, cue(s, s.say_msg || 'saved', 0.25, s.t0) - 0.5); s._e = Math.max(s._m + 0.9, cue(s, s.say_end || 'ends', 0.5, s._m));
    s._v = Math.max(s._e + 0.7, cue(s, s.say_err || 'VA03', 0.75, s._e));
    return [['notify', s._m], ['zero', s._e, { d: 0.3 }], ['crt', s._e + 0.05], ['key', s._v], ['error', s._v + 0.45]]; },
  cam(s, t) { const u = seg(t, s._v + 0.45, s._v + 0.75); return { zoom: lerp(1, 1.04, seg(t, s.t0, s._v)), sx: u > 0 && u < 1 ? Math.sin(t * 90) * 10 * (1 - u) : 0 }; },
  draw(g, s, t) {
    const y0 = sy(s, 360);
    // 1) RETURN table with the success message
    const a = drop(t, s.t0 + 0.05, 0.35); g.save(); g.globalAlpha *= clamp(a * 2);
    const r = E.windowBox(g, X0, y0, CW, 300, { title: 'lt_return  (RETURN)', app: 6, bar: 72 });
    const cols = [['TYPE', 140], ['MESSAGE', CW - 180]]; let x = r[0] + 20;
    cols.forEach(([c, w]) => { T(g, c, x + 10, r[1] + 46, 28, { fam: 'mono', wt: 700, color: PAL.dim }); x += w; });
    const mp = seg(t, s._m, s._m + 0.4);
    if (mp > 0) { g.save(); g.globalAlpha *= mp; const ry = r[1] + 90; g.fillStyle = rgba(ACC, 0.12); rr(g, r[0] + 14, ry, CW - 28, 100, 14); g.fill();
      T(g, 'S', r[0] + 70, ry + 50, 40, { fam: 'mono', wt: 700, color: ACC, align: 'center' });
      const msg = plain(s.msg || 'Order has been saved'), n = Math.floor(msg.length * seg(t, s._m + 0.05, s._m + 0.8));
      T(g, msg.slice(0, n), r[0] + 170, ry + 50, fitPx(g, msg, 34, CW - 210, 600, 'mono'), { fam: 'mono', wt: 600 }); g.restore(); }
    g.restore();
    // 2) the order card: solid until the program ends, then a dashed ghost
    const cy = y0 + 360, gh = seg(t, s._e, s._e + 0.5);
    if (t > s._m + 0.3) { const p = drop(t, s._m + 0.3, 0.35); g.save(); g.globalAlpha *= clamp(p * 2) * (1 - gh * 0.55);
      const w = 560, x = 540 - w / 2, h = 170;
      if (gh < 0.5) { E.panel(g, x, cy, w, h, { r: 24, fill: PAL.surf3, shadow: 0.8 }); }
      else { g.setLineDash([16, 12]); g.strokeStyle = PAL.dim; g.lineWidth = 3; rr(g, x, cy, w, h, 24); g.stroke(); g.setLineDash([]); }
      icon(g, 'table', x + 80, cy + h / 2, 70, gh < 0.5 ? ACC : PAL.mute);
      T(g, 'Order ' + (s.order || '12345'), x + 150, cy + 62, 44, { fam: 'mono', wt: 700, color: gh < 0.5 ? PAL.text : PAL.mute });
      T(g, gh < 0.5 ? 'queued for update' : 'never committed', x + 150, cy + 116, 30, { fam: 'mono', color: gh < 0.5 ? PAL.dim : PAL.red });
      g.restore();
      if (t >= s._e) T(g, 'program ends · no COMMIT', 540, cy + h + 50, 32, { fam: 'mono', wt: 600, align: 'center', color: PAL.dim, alpha: ss(seg(t, s._e, s._e + 0.3)) }); }
    // 3) VA03 with the red error in the status bar
    if (t > s._v - 0.1) { const p = drop(t, s._v - 0.1, 0.35), vy = cy + 300; g.save(); g.globalAlpha *= clamp(p * 2);
      const r2 = E.windowBox(g, X0, vy, CW, 330, { title: (s.tcode || 'VA03') + ' · Display Sales Order', app: 6, bar: 72 });
      T(g, 'Order', r2[0] + 30, r2[1] + 60, 32, { color: PAL.dim });
      const typed = (s.order || '12345').slice(0, Math.floor(5 * seg(t, s._v, s._v + 0.35)));
      H_.E.panel(g, r2[0] + 170, r2[1] + 26, 300, 70, { r: 12, fill: PAL.surf2, shadow: 0 }); T(g, typed, r2[0] + 190, r2[1] + 62, 36, { fam: 'mono', wt: 600 });
      const ep = seg(t, s._v + 0.45, s._v + 0.75);
      if (ep > 0) { const ey = r2[1] + r2[3] - 110 + (1 - eo(ep)) * 40; g.save(); g.globalAlpha *= ep; g.fillStyle = rgba(PAL.red, 0.16); rr(g, r2[0] + 14, ey, CW - 28, 96, 12); g.fill();
        g.strokeStyle = rgba(PAL.red, 0.8); g.lineWidth = 2; rr(g, r2[0] + 14, ey, CW - 28, 96, 12); g.stroke(); mark(g, 'no', r2[0] + 60, ey + 48, 44, PAL.red);
        const em = plain(s.err || 'Document is not in the database'); rich(g, em, r2[0] + 100, ey + 32, 28, { wt: 600, maxw: CW - 140, lh: 34, maxLines: 2, color: '#FFB3B5', fam: 'mono' }); g.restore(); }
      g.restore(); }
  },
};
export default { ghost };
