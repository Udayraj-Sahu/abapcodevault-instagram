// Custom scenes for "Tables part 10 · Technical settings" (26 Nov).
// "shelves": three shelves APPL0 / APPL1 / APPL2; MARA, VBAK and T001 fly onto their shelf on the spoken data class.
// "dial":    a size-category dial 0-9; the needle sweeps as the rows grow, then an F4 list shows one range per category.
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
const shelves = {
  plan(s) { const L = s.shelves || []; s._c = H_.seqCues(s, L.map(x => x.say || x.cls), 0.08, 0.7); return s._c.flatMap(c => [['fly', c - 0.1], ['land', c + 0.3]]); },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 40, L = s.shelves || [], sh = 220;
    L.forEach((x, i) => { const y = y0 + i * (sh + 30), a = drop(t, s.t0 + 0.05 + i * 0.08, 0.3);
      g.save(); g.globalAlpha *= clamp(a * 2); E.panel(g, X0, y, CW, sh, { r: 22, fill: PAL.surf, shadow: 0.6 });
      const on = t >= s._c[i] + 0.3;
      const p = new Path2D(); p.roundRect(X0 + 24, y + 24, 230, 70, 35); if (on) E.litShape(g, p, { accent: true, glowR: 20, bbox: [X0 + 24, y + 24, 230, 70] }); else { g.fillStyle = PAL.surf3; g.fill(p); }
      T(g, x.cls, X0 + 139, y + 60, 36, { fam: 'mono', wt: 700, align: 'center', color: on ? '#0A0B0F' : PAL.dim });
      T(g, x.name, X0 + 290, y + 60, 40, { wt: 700, color: on ? PAL.text : PAL.dim });
      g.fillStyle = 'rgba(255,255,255,.10)'; g.fillRect(X0 + 24, y + sh - 34, CW - 48, 6);   // the shelf board
      g.restore();
      // the table flies onto its shelf
      const c = s._c[i]; if (t > c - 0.15) { const q = eo(seg(t, c - 0.15, c + 0.3)), tw = 300, th = 88;
        const tx = lerp(1150, X0 + CW - tw - 40, q), ty = lerp(y - 160, y + sh - 34 - th, q) - Math.sin(q * Math.PI) * 30;
        g.save(); g.globalAlpha *= clamp(q * 2); E.panel(g, tx, ty, tw, th, { r: 16, fill: PAL.surf3, shadow: 0.9 });
        icon(g, 'table', tx + 55, ty + th / 2, 48, ACC); T(g, x.table, tx + 100, ty + th / 2 + 1, 40, { fam: 'mono', wt: 700 }); g.restore(); }
    });
  },
};
const dial = {
  plan(s) { s._g = Math.max(s.t0 + 0.7, cue(s, s.say_turn || 'expect', 0.3, s.t0)); s._f = Math.max(s._g + 1.4, cue(s, s.say_f4 || 'F4', 0.6, s._g));
    s._rows = [0, 1, 2, 3, 4].map(i => s._f + 0.3 + i * 0.18);
    return [['tick', s._g], ['tick', s._g + 0.5], ['tick', s._g + 1.0], ['press', s._f]].concat(s._rows.map(r => ['row', r])); },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 30, cx = 540, cy = y0 + 270, R = 200;
    const a = drop(t, s.t0 + 0.05, 0.35); g.save(); g.globalAlpha *= clamp(a * 2);
    // dial arc with 10 ticks (0..9)
    g.strokeStyle = 'rgba(255,255,255,.12)'; g.lineWidth = 26; g.lineCap = 'round'; g.beginPath(); g.arc(cx, cy, R, Math.PI, 0); g.stroke();
    const v = 9 * eio(seg(t, s._g, s._g + 1.3)) * (1 - 0.65 * eio(seg(t, s._f - 0.2, s._f + 0.3)));   // sweeps to 9, settles at ~3
    g.strokeStyle = ACC; g.beginPath(); g.arc(cx, cy, R, Math.PI, Math.PI + Math.PI * v / 9); g.stroke();
    for (let i = 0; i <= 9; i++) { const an = Math.PI + Math.PI * i / 9, x = cx + Math.cos(an) * (R + 52), y = cy + Math.sin(an) * (R + 52);
      T(g, String(i), x, y, 34, { fam: 'mono', wt: 700, align: 'center', color: Math.round(v) === i ? ACC : PAL.dim }); }
    const an = Math.PI + Math.PI * v / 9; g.strokeStyle = PAL.text; g.lineWidth = 8; g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.cos(an) * (R - 50), cy + Math.sin(an) * (R - 50)); g.stroke();
    g.fillStyle = PAL.text; g.beginPath(); g.arc(cx, cy, 16, 0, TAU); g.fill();
    T(g, 'expected rows', cx, cy + 50, 32, { fam: 'mono', wt: 600, align: 'center', color: PAL.dim });
    g.restore();
    // F4 list: one row range per category
    if (t > s._f - 0.05) { const p = drop(t, s._f - 0.05, 0.3), ly = cy + 110; g.save(); g.globalAlpha *= clamp(p * 2);
      const r = E.windowBox(g, X0, ly, CW, 420, { title: 'F4 · Size category', app: 6, bar: 72 });
      [['0', 'smallest range'], ['1', 'more rows'], ['2', 'more rows'], ['3', 'more rows'], ['… 9', 'largest range']].forEach(([c, d], i) => { const rp = seg(t, s._rows[i], s._rows[i] + 0.25); if (rp <= 0) return; const yy = r[1] + 22 + i * 64;
        g.save(); g.globalAlpha *= rp; 
        T(g, c, r[0] + 50, yy + 24, 34, { fam: 'mono', wt: 700, color: i === 0 ? ACC : PAL.text }); T(g, d, r[0] + 190, yy + 24, 32, { fam: 'mono', color: PAL.dim });
        g.restore(); });
      g.restore(); }
  },
};
export default { shelves, dial };
