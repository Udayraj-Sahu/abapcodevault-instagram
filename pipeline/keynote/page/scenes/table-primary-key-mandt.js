// Custom scenes for "Tables part 8 · Primary key and MANDT" (25 Nov).
// "duplicate": a new row flies into the table, its key cells hit the existing row's key, it bounces off; sy-subrc = 4, no dump.
// "clients":   the same key LH lives once in client 100 and once in client 200, because MANDT is part of the key.
import { H_ } from '../reel.js';
import { sy } from '../moments.js';
const { E, T, fitPx, rich, chip, drop, cue, plain, mark, X0, CW, ACC } = H_;
const { PAL, clamp, lerp, seg, ss, eo, eio, back, rr, rgba } = E;

function table(g, x, y, w, cols, rows, o = {}) {      // header + rows; o.keys = number of key columns, o.hl = row index to flash red
  const { keys = 2, hl = -1, red = 0, cw = null, title = '' } = o, ch = 84, W = cw || cols.map(() => w / cols.length);
  if (title) T(g, title, x, y - 26, 26, { fam: 'mono', wt: 700, color: PAL.dim });
  const xs = []; let xx = x; W.forEach(v => { xs.push(xx); xx += v; });
  cols.forEach((c, k) => { const p = new Path2D(); p.roundRect(xs[k] + 3, y, W[k] - 6, ch - 10, 12);
    E.litShape(g, p, { accent: k < keys, glowR: k < keys ? 18 : 0, bbox: [xs[k], y, W[k], ch] });
    T(g, c, xs[k] + W[k] / 2, y + (ch - 10) / 2, fitPx(g, c, 28, W[k] - 18, 700, 'mono'), { fam: 'mono', wt: 700, align: 'center', color: k < keys ? '#0A0B0F' : PAL.text }); });
  rows.forEach((r, i) => r.forEach((v, k) => { const yy = y + (i + 1) * ch, bad = i === hl && k < keys ? red : 0;
    g.fillStyle = bad > 0 ? rgba(PAL.red, 0.22 * bad) : 'rgba(255,255,255,.045)'; rr(g, xs[k] + 3, yy, W[k] - 6, ch - 10, 10); g.fill();
    if (bad > 0) { g.strokeStyle = rgba(PAL.red, 0.9 * bad); g.lineWidth = 3; rr(g, xs[k] + 3.5, yy + 0.5, W[k] - 7, ch - 11, 10); g.stroke(); }
    T(g, String(v), xs[k] + W[k] / 2, yy + (ch - 10) / 2, fitPx(g, String(v), 32, W[k] - 18, 600, 'mono'), { fam: 'mono', wt: 600, align: 'center', color: bad > 0 ? '#FFB3B5' : '#D5D9E3' }); }));
  return { xs, W, ch };
}

const duplicate = {
  plan(s) { s._in = Math.max(s.t0 + 0.6, cue(s, s.say_insert || 'insert', 0.15, s.t0)); s._hit = s._in + 0.55;
    s._rc = Math.max(s._hit + 0.6, cue(s, s.say_rc || 'four', 0.6, s._hit)); s._nd = Math.max(s._hit + 0.3, cue(s, s.say_nodump || 'dump', 0.45, s._in));
    return [['whoosh', s._in], ['bump', s._hit], ['glitch', s._hit + 0.02], ['pop', s._nd], ['digit', s._rc]]; },
  cam(s, t) { const u = seg(t, s._hit, s._hit + 0.3); return { zoom: lerp(1, 1.025, seg(t, s.t0, s._hit)), sx: u > 0 && u < 1 ? Math.sin(t * 90) * 12 * (1 - u) : 0 }; },
  draw(g, s, t) {
    let y = sy(s, 330);
    if (s.label) { chip(g, plain(s.label), X0, y, { alpha: ss(seg(t, s.t0 - 0.1, s.t0 + 0.15)) }); y += 70; }
    if (s.heading) y += rich(g, s.heading, X0, y + 10, 72, { wt: 700, maxLines: 2, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22) }) + 60;
    const cols = s.columns || ['MANDT', 'CARRID', 'CARRNAME'], cw = [220, 220, CW - 440], rows = s.rows || [];
    const hit = seg(t, s._hit, s._hit + 0.5), red = hit > 0 ? 1 - seg(t, s._hit + 1.6, s._hit + 2.2) * 0.6 : 0;
    const a = drop(t, s.t0 + 0.05, 0.35); g.save(); g.globalAlpha *= clamp(a * 2);
    const tb = table(g, X0, y + 40, CW, cols, rows, { keys: s.keys || 2, hl: s.dup_row ?? rows.length - 1, red: red * (t >= s._hit ? 1 : 0), cw, title: s.table || 'ZTAIRLINE' });
    g.restore();
    // the new row: flies in from the right, hits, bounces back below the table
    const nr = s.new_row || [], rowY = y + 40 + (rows.length + 1) * tb.ch;
    if (t > s._in - 0.05) {
      const pin = eio(seg(t, s._in, s._hit)), back_ = seg(t, s._hit, s._hit + 0.6);
      const targetY = y + 40 + ((s.dup_row ?? rows.length - 1) + 1) * tb.ch;
      const yy = t < s._hit ? lerp(rowY + 260, targetY + 30, pin) : lerp(targetY + 30, rowY + 70, eo(back_)) + Math.sin(back_ * Math.PI) * 30;
      const xo = t < s._hit ? lerp(600, 0, pin) : 0;
      g.save(); g.translate(xo, 0); g.rotate(t >= s._hit ? (1 - eo(back_)) * 0.03 : 0);
      nr.forEach((v, k) => { const x = tb.xs[k] + 3, w = tb.W[k] - 6, p = new Path2D(); p.roundRect(x, yy, w, tb.ch - 10, 10);
        E.litShape(g, p, { bbox: [x, yy, w, tb.ch - 10] }); g.strokeStyle = k < (s.keys || 2) && t >= s._hit ? rgba(PAL.red, 0.9) : rgba(ACC, 0.6); g.lineWidth = 3; g.stroke(p);
        T(g, String(v), x + w / 2, yy + (tb.ch - 10) / 2, fitPx(g, String(v), 32, w - 18, 600, 'mono'), { fam: 'mono', wt: 600, align: 'center' }); });
      T(g, 'INSERT', X0, yy - 30, 26, { fam: 'mono', wt: 700, color: ACC, alpha: 1 - seg(t, s._hit + 0.6, s._hit + 1) });
      g.restore();
    }
    // results: "no dump" and sy-subrc = 4
    const by = rowY + 230;
    const nd = drop(t, s._nd, 0.3); if (nd > 0) { g.save(); g.globalAlpha *= clamp(nd * 2); E.panel(g, X0, by, CW / 2 - 15, 110, { r: 55, fill: PAL.surf2, shadow: 0.6 });
      mark(g, 'ok', X0 + 62, by + 55, 52, ACC); T(g, 'no dump', X0 + 110, by + 56, 42, { wt: 700 }); g.restore(); }
    const rc = drop(t, s._rc - 0.45, 0.3); if (rc > 0) { g.save(); g.globalAlpha *= clamp(rc * 2); const x = X0 + CW / 2 + 15;
      E.panel(g, x, by, CW / 2 - 15, 110, { r: 55, fill: PAL.surf3, shadow: 0.6 }); T(g, 'sy-subrc =', x + 36, by + 56, 34, { fam: 'mono', color: PAL.dim });
      E.scramble(g, '4', x + CW / 2 - 90, by + 82, t, [s._rc], { px: 72, start: s._rc - 0.45, color: ACC, align: 'center' }); g.restore(); }
  },
};

const clients = {
  plan(s) { s._a = s.t0 + 0.3; s._b = Math.max(s._a + 0.5, cue(s, s.say_b || '200', 0.55, s._a));
    s._k = Math.max(s._b + 0.4, cue(s, s.say_key || 'key', 0.75, s._b)); return [['snap', s._a], ['snap', s._b], ['glint', s._k]]; },
  draw(g, s, t) {
    let y = sy(s, 330);
    if (s.label) { chip(g, plain(s.label), X0, y, { alpha: ss(seg(t, s.t0 - 0.1, s.t0 + 0.15)) }); y += 70; }
    if (s.heading) y += rich(g, s.heading, X0, y + 10, 72, { wt: 700, maxLines: 2, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22) }) + 70;
    const cw = [200, 200, CW - 400];
    [[s._a, s.rows_a || [], 'CLIENT 100'], [s._b, s.rows_b || [], 'CLIENT 200']].forEach(([t0, rows, lb], k) => {
      const p = drop(t, t0, 0.34); if (p <= 0) return; const yy = y + k * (110 + (rows.length + 1) * 84) + (1 - p) * 40;
      g.save(); g.globalAlpha *= clamp(p * 2); g.translate((k ? 1 : -1) * (1 - p) * 80, 0);
      table(g, X0, yy + 30, CW, s.columns || ['MANDT', 'CARRID', 'CARRNAME'], rows, { keys: 2, cw, title: lb });
      g.restore(); });
    const kp = ss(seg(t, s._k, s._k + 0.4)); if (kp > 0) { g.save(); g.globalAlpha *= kp; const hy = sy(s, 1350);
      const p = new Path2D(); p.roundRect(X0, hy, CW, 96, 48); E.litShape(g, p, { accent: true, glowR: 30, bbox: [X0, hy, CW, 96] });
      T(g, plain(s.key_line || 'key = MANDT + CARRID'), 540, hy + 49, fitPx(g, plain(s.key_line || 'key = MANDT + CARRID'), 40, CW - 60, 700, 'mono'), { fam: 'mono', wt: 700, color: '#0A0B0F', align: 'center' }); g.restore(); }
  },
};
export default { duplicate, clients };
