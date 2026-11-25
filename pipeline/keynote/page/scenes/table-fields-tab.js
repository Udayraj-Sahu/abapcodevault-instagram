// Custom scenes for "Tables part 7 · The Fields tab" (25 Nov).
// "columns": each line of the SE11 Fields tab flies down and becomes one column of the real table SCARR.
import { H_ } from '../reel.js';
import { sy } from '../moments.js';
const { E, T, fitPx, rich, chip, drop, seqCues, plain, X0, CW, ACC } = H_;
const { PAL, clamp, lerp, seg, ss, eo, rr, rgba } = E;

const columns = {
  plan(s) { const f = s.fields || []; s._c = seqCues(s, f.map(x => x.say || x.name), 0.12, 0.8); return s._c.flatMap(c => [['row', c], ['snap', c + 0.42]]); },
  draw(g, s, t) {
    const f = s.fields || [], n = f.length;
    let y = sy(s, 330);
    if (s.label) { chip(g, plain(s.label), X0, y, { alpha: ss(seg(t, s.t0 - 0.1, s.t0 + 0.15)) }); y += 70; }
    if (s.heading) y += rich(g, s.heading, X0, y + 10, 72, { wt: 700, maxLines: 2, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22) }) + 40;
    // top: the Fields tab (one line per field)
    const tabH = 60 + 52 + n * 62 + 16, a = drop(t, s.t0 + 0.05, 0.35);
    g.save(); g.globalAlpha *= clamp(a * 2);
    const c = E.windowBox(g, X0, y, CW, tabH, { title: `SE11 · ${s.table || 'SCARR'} · Fields tab`, app: 6, bar: 60 });
    const cx = [X0 + 30, X0 + 300, X0 + 400, X0 + 680];
    ['FIELD', 'KEY', 'DATA ELEMENT', 'TYPE'].forEach((h, k) => T(g, h, cx[k], c[1] + 30, 24, { fam: 'mono', wt: 700, color: PAL.mute }));
    f.forEach((x, i) => { const yy = c[1] + 78 + i * 62, on = t >= s._c[i] && (i === n - 1 || t < s._c[i + 1]), done = t >= s._c[i];
      if (on) { g.fillStyle = 'rgba(183,243,74,.08)'; rr(g, X0 + 12, yy - 27, CW - 24, 54, 10); g.fill(); g.fillStyle = ACC; rr(g, X0 + 12, yy - 27, 6, 54, 3); g.fill(); }
      const col = done ? PAL.text : PAL.dim;
      T(g, x.name, cx[0], yy, 32, { fam: 'mono', wt: 700, color: col }); T(g, x.key ? '✓' : '', cx[1] + 10, yy, 32, { fam: 'mono', wt: 700, color: x.key ? ACC : col });
      T(g, x.de || '', cx[2], yy, 30, { fam: 'mono', color: col }); T(g, x.type || '', cx[3], yy, 30, { fam: 'mono', color: col }); });
    g.restore();
    // bottom: the table SCARR builds itself, one column per line
    const ty = y + tabH + 60, rows = s.rows || [], colW = CW / n, cellH = 74;
    const tb = ss(seg(t, s.t0 + 0.2, s.t0 + 0.5));
    if (tb > 0) { g.save(); g.globalAlpha *= tb; T(g, `${s.table || 'SCARR'} · database table`, X0, ty - 24, 26, { fam: 'mono', wt: 700, color: PAL.dim });
      g.strokeStyle = 'rgba(232,234,240,.18)'; g.setLineDash([10, 9]); g.lineWidth = 2; rr(g, X0, ty, CW, cellH * (rows.length + 1) + 10, 18); g.stroke(); g.setLineDash([]); g.restore(); }
    f.forEach((x, i) => {
      const p = seg(t, s._c[i], s._c[i] + 0.45); if (p <= 0) return;
      const fromY = y + 60 + 78 + i * 62, toX = X0 + i * colW, q = eo(p), land = drop(t, s._c[i] + 0.25, 0.3);
      // the line flies down and becomes the header cell
      const hx = lerp(cx[0] - 10, toX + 4, q), hy = lerp(fromY - 26, ty + 6, q), hw = lerp(260, colW - 8, q);
      g.save(); const head = new Path2D(); head.roundRect(hx, hy, hw, cellH - 8, 12);
      E.litShape(g, head, { accent: !!x.key, glowR: x.key ? 24 : 0, bbox: [hx, hy, hw, cellH - 8] });
      T(g, x.name, hx + hw / 2, hy + (cellH - 8) / 2, fitPx(g, x.name, 30, hw - 16, 700, 'mono'), { fam: 'mono', wt: 700, align: 'center', color: x.key ? '#0A0B0F' : PAL.text });
      g.restore();
      if (land > 0) rows.forEach((r, k) => { const v = String(r[i] ?? ''), yy = ty + 6 + (k + 1) * cellH + (1 - land) * 20;
        g.save(); g.globalAlpha *= clamp(land * 2 - k * 0.3); g.fillStyle = 'rgba(255,255,255,.04)'; rr(g, toX + 4, yy, colW - 8, cellH - 8, 10); g.fill();
        T(g, v, toX + colW / 2, yy + (cellH - 8) / 2, fitPx(g, v, 30, colW - 20, 500, 'mono'), { fam: 'mono', align: 'center', color: '#C9CEDA' }); g.restore(); });
    });
  },
};
export default { columns };
