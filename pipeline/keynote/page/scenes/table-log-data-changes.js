// Custom scenes for "Tables part 12 · Log data changes" (27 Nov).
// "nolog":   a ZTAIRLINE row silently flips EUR -> USD; Who? When? Old value? cards drop in, nobody can answer.
// "logbook": the same change now writes an entry into DBTABLOG: user, time, field, old -> new fill in on spoken words.
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
function rowCard(g, s, t, y, tc) {          // the ZTAIRLINE row; CURRCODE flips at tc
  const a = drop(t, s.t0 + 0.05, 0.35); g.save(); g.globalAlpha *= clamp(a * 2);
  const r = E.windowBox(g, X0, y, CW, 250, { title: s.table || 'ZTAIRLINE', app: 6, bar: 72 });
  const cols = [['CARRID', 220], ['CARRNAME', 380], ['CURRCODE', CW - 640]]; let x = r[0] + 20;
  cols.forEach(([c, w], k) => { T(g, c, x + w / 2, r[1] + 40, 26, { fam: 'mono', wt: 700, color: PAL.dim, align: 'center' });
    const v = k === 0 ? 'LH' : k === 1 ? 'Lufthansa' : null;
    if (v) cell(g, x + 6, r[1] + 80, w - 12, 76, v);
    else { const fl = seg(t, tc, tc + 0.35), ch = t >= tc;
      cell(g, x + 6, r[1] + 80, w - 12, 76, ch ? (s.new || 'USD') : (s.old || 'EUR'), { ring: ch ? rgba(ACC, 0.9 * (1 - seg(t, tc + 1.2, tc + 2)) + 0.1) : null, alpha: fl > 0 && fl < 1 ? 0.4 + 0.6 * Math.abs(Math.cos(fl * Math.PI)) : 1 }); }
    x += w; });
  g.restore(); return y + 250;
}
const nolog = {
  plan(s) { s._c = Math.max(s.t0 + 0.5, cue(s, s.say_change || 'changed', 0.12, s.t0));
    s._q = [s.say_who || 'who', s.say_when || 'when', s.say_old || 'old'].reduce((acc, k, i) => { const last = acc.length ? acc[acc.length - 1] : s._c; acc.push(Math.max(last + 0.35, cue(s, k, 0.4 + i * 0.12, last))); return acc; }, []);
    s._x = Math.max(s._q[2] + 0.5, cue(s, s.say_bad || 'answer', 0.9, s._q[2]));
    return [['flip', s._c]].concat(s._q.map(q => ['pop', q]), [['error', s._x]]); },
  cam(s, t) { const u = seg(t, s._x, s._x + 0.3); return { zoom: lerp(1, 1.03, seg(t, s.t0, s._x)), sx: u > 0 && u < 1 ? Math.sin(t * 90) * 8 * (1 - u) : 0 }; },
  draw(g, s, t) {
    const y0 = head(g, s, t);
    const y1 = rowCard(g, s, t, y0, s._c) + 60;
    if (t >= s._c) T(g, (s.old || 'EUR') + ' → ' + (s.new || 'USD') + '  ·  no trace', 540, y1 - 20, 32, { fam: 'mono', wt: 600, align: 'center', color: PAL.dim, alpha: ss(seg(t, s._c, s._c + 0.3)) });
    const qs = s.questions || ['Who?', 'When?', 'Old value?'], w = (CW - 2 * 30) / 3;
    qs.forEach((q, i) => { const p = drop(t, s._q[i], 0.32); if (p <= 0) return; const x = X0 + i * (w + 30), y = y1 + 40 + (1 - p) * 50;
      g.save(); g.globalAlpha *= clamp(p * 2); E.panel(g, x, y, w, 220, { r: 24, fill: PAL.surf2, shadow: 0.8 });
      T(g, '?', x + w / 2, y + 80, 80, { fam: 'mono', wt: 700, align: 'center', color: t >= s._x ? PAL.red : PAL.mute });
      T(g, q, x + w / 2, y + 170, fitPx(g, q, 40, w - 30, 700), { wt: 700, align: 'center' }); g.restore(); });
    pill(g, s.bad_text || 'no log = no answer', y1 + 330, drop(t, s._x, 0.3), { red: true });
  },
};
const logbook = {
  plan(s) { s._c = Math.max(s.t0 + 0.45, cue(s, s.say_change || 'change', 0.1, s.t0)); s._in = s._c + 0.6;
    const keys = [s.say_who || 'who', s.say_when || 'when', s.say_old || 'old', s.say_new || 'new'];
    s._f = []; let last = s._in; keys.forEach((k, i) => { const c = Math.max(last + 0.3, cue(s, k, 0.45 + i * 0.1, last - 0.2)); s._f.push(c); last = c; });
    return [['flip', s._c], ['fly', s._in - 0.2], ['land', s._in + 0.15]].concat(s._f.map(f => ['key', f])); },
  draw(g, s, t) {
    const y0 = head(g, s, t);
    const y1 = rowCard(g, s, t, y0, s._c) + 50;
    // the log window
    const a = drop(t, s.t0 + 0.2, 0.35); g.save(); g.globalAlpha *= clamp(a * 2);
    const r = E.windowBox(g, X0, y1, CW, 430, { title: 'DBTABLOG · change log', app: 6, bar: 72 });
    g.restore();
    const lp = seg(t, s._in - 0.3, s._in + 0.15); if (lp <= 0) return;
    const ey = lerp(y0 + 100, r[1] + 70, eio(lp)), ex = r[0] + 24, ew = CW - 48;
    g.save(); g.globalAlpha *= clamp(lp * 3); const p = new Path2D(); p.roundRect(ex, ey, ew, 330, 18);
    E.panel(g, ex, ey, ew, 330, { r: 18, fill: PAL.surf3, shadow: 0.8 }); g.strokeStyle = rgba(ACC, 0.7); g.lineWidth = 3; g.stroke(p);
    const rows = [['User', s.user || 'USER01'], ['When', s.when || '27.11.2026 22:14'], ['Field', (s.field || 'CURRCODE') + '  old: ' + (s.old || 'EUR')], ['New', s.new || 'USD']];
    rows.forEach(([k, v], i) => { const fy = ey + 22 + i * 76, fa = ss(seg(t, s._f[i] - 0.1, s._f[i] + 0.2));
      T(g, k, ex + 30, fy + 36, 30, { fam: 'mono', wt: 700, color: PAL.dim });
      if (fa > 0) { const n = Math.ceil(v.length * seg(t, s._f[i] - 0.1, s._f[i] + 0.4));
        T(g, v.slice(0, n), ex + 210, fy + 36, fitPx(g, v, 36, ew - 240, 600, 'mono'), { fam: 'mono', wt: 600, color: i === 3 ? ACC : PAL.text, alpha: fa }); } });
    g.restore();
    if (t > s._f[3] + 0.5) pill(g, s.good_text || 'every change: who, when, old, new', r[1] + 455, drop(t, s._f[3] + 0.5, 0.3), { accent: true });
  },
};
export default { nolog, logbook };
