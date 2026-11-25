// Custom scene for "Tables part 11 · Buffering" (26 Nov).
// "buffer": the first SELECT travels the long way to the database and fills the buffer on the application server; the next SELECT is answered straight from memory.
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
const buffer = {
  plan(s) { s._1 = Math.max(s.t0 + 0.4, cue(s, s.say_first || 'first', 0.05, s.t0)); s._fill = s._1 + 1.6;
    s._2 = Math.max(s._fill + 0.5, cue(s, s.say_next || 'next', 0.55, s._1)); s._x = Math.max(s._2 + 0.6, cue(s, s.say_fast || 'faster', 0.85, s._2));
    return [['whoosh', s._1], ['ping', s._1 + 0.8], ['snap', s._fill], ['whoosh', s._2], ['ping', s._2 + 0.35], ['glint', s._x]]; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 20;
    // three stations: program -> application server (buffer) -> database
    const st = [['code', 'Program', y0], ['table', 'App server · buffer', y0 + 200], ['db', 'Database', y0 + 500]];
    const filled = t >= s._fill;
    st.forEach(([ic, name, y], i) => { const a = drop(t, s.t0 + 0.05 + i * 0.08, 0.3); g.save(); g.globalAlpha *= clamp(a * 2);
      const w = i === 1 ? CW : 620, x = i === 1 ? X0 : 540 - 310, h = i === 1 ? 220 : 130;
      if (i === 1 && filled) { const p = new Path2D(); p.roundRect(x, y, w, h, 24); E.panel(g, x, y, w, h, { r: 24, fill: PAL.surf2, shadow: 0.8 }); g.strokeStyle = rgba(ACC, 0.8); g.lineWidth = 3; g.stroke(p); }
      else E.panel(g, x, y, w, h, { r: 24, fill: PAL.surf2, shadow: 0.8 });
      icon(g, ic, x + 70, y + (i === 1 ? 60 : h / 2), 56, i === 1 && filled ? ACC : PAL.dim); T(g, name, x + 130, y + (i === 1 ? 60 : h / 2), 40, { wt: 700 });
      if (i === 1) { for (let k = 0; k < 4; k++) { const fp = seg(t, s._fill - 0.3 + k * 0.08, s._fill + k * 0.08); const bx = x + 40 + k * 222;
          g.fillStyle = fp > 0 ? rgba(ACC, 0.18 * fp) : 'rgba(255,255,255,.04)'; rr(g, bx, y + 120, 200, 70, 12); g.fill();
          if (fp > 0) T(g, (s.table || 'T001') + ' row', bx + 100, y + 155, 26, { fam: 'mono', align: 'center', alpha: fp, color: PAL.text }); } }
      g.restore(); });
    // packets: first read goes all the way down and back; next read stops at the buffer
    const lane = 540, top = y0 + 130, mid = y0 + 200, bot = y0 + 500;
    const pk = (y, col) => { E.glow(g, lane, y, 36, col, 0.6); g.fillStyle = col; g.beginPath(); g.arc(lane, y, 16, 0, TAU); g.fill(); };
    g.save(); g.strokeStyle = 'rgba(255,255,255,.10)'; g.lineWidth = 4; g.setLineDash([10, 12]); g.beginPath(); g.moveTo(lane, top); g.lineTo(lane, mid); g.moveTo(lane, mid + 220); g.lineTo(lane, bot); g.stroke(); g.restore();
    if (t >= s._1 && t < s._fill + 0.1) { const u = seg(t, s._1, s._fill), y = u < 0.5 ? lerp(top, bot, eio(u * 2)) : lerp(bot, mid + 110, eio((u - 0.5) * 2)); pk(y, PAL.text); }
    if (t >= s._2 && t < s._2 + 0.8) { const u = seg(t, s._2, s._2 + 0.7), y = u < 0.5 ? lerp(top, mid + 40, eo(u * 2)) : lerp(mid + 40, top, eo((u - 0.5) * 2)); pk(y, ACC); }
    // labels
    const lx = X0 + CW - 10;
    if (t >= s._1) T(g, '1st read: database', lx, y0 + 462, 32, { fam: 'mono', wt: 600, align: 'right', color: PAL.dim, alpha: ss(seg(t, s._1, s._1 + 0.3)) });
    if (t >= s._2) T(g, 'next read: memory', X0 + 10, y0 + 165, 32, { fam: 'mono', wt: 600, color: ACC, alpha: ss(seg(t, s._2, s._2 + 0.3)) });
    pill(g, 'no database trip', y0 + 680, drop(t, s._x, 0.3), { accent: true });
  },
};
export default { buffer };
