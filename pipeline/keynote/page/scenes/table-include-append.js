// Custom scenes for "Tables part 15 · Include vs append structures" (28 Nov).
// "reuse": one structure ZS_ADDRESS flows into three Z tables; a new field added once appears in all three.
// "append": SAP table VBAK refuses a direct edit (modification); the append ZAVBAK docks at the end, VBAK stays untouched.
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
const reuse = {
  plan(s) { s._s = s.t0 + 0.2; s._inc = Math.max(s.t0 + 0.8, cue(s, s.say_inc || 'includes', 0.5, s.t0)); s._chg = Math.max(s._inc + 1.2, cue(s, s.say_chg || 'change', 0.8, s._inc));
    return [['pop', s._s], ['fly', s._inc], ['land', s._inc + 0.45], ['land', s._inc + 0.6], ['land', s._inc + 0.75], ['snap', s._chg], ['glint', s._chg + 0.5]]; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 10, st = s.structure || 'ZS_ADDRESS', F = s.fields || ['STREET', 'CITY', 'COUNTRY'], nf = s.new_field || 'POSTCODE';
    const tabs = s.tables || [['ZCUSTOMER', 'CUST_ID'], ['ZVENDOR', 'VENDOR_ID'], ['ZPLANT', 'PLANT_ID']];
    const chg = t >= s._chg, all = chg ? [...F, nf] : F;
    // structure card
    if (card(g, X0, y0, CW, 200, drop(t, s._s, 0.35), { ring: chg && t < s._chg + 1.2 ? rgba(ACC, 1 - seg(t, s._chg + 0.4, s._chg + 1.2)) : null })) {
      icon(g, 'table', X0 + 56, y0 + 50, 40, PAL.dim); T(g, st + ' · structure', X0 + 100, y0 + 50, 32, { fam: 'mono', wt: 700, color: PAL.dim });
      const w = (CW - 60 - (all.length - 1) * 16) / all.length;
      all.forEach((f, i) => { const isNew = f === nf; const a = isNew ? drop(t, s._chg, 0.3) : 1; if (a <= 0) return; g.save(); g.globalAlpha *= clamp(a * 2);
        cell(g, X0 + 30 + i * (w + 16), y0 + 100, w, 70, f, { px: 28, accent: isNew }); g.restore(); });
      g.restore(); }
    // three tables
    const ty = y0 + 300, tw = (CW - 40) / 3, rh = 56;
    tabs.forEach(([name, key], j) => { const x = X0 + j * (tw + 20), a = drop(t, s.t0 + 0.3 + j * 0.1, 0.35);
      if (!card(g, x, ty, tw, 70 + 5 * rh + 20, a, { fill: PAL.surf3 })) return;
      T(g, name, x + tw / 2, ty + 38, fitPx(g, name, 30, tw - 30, 700, 'mono'), { fam: 'mono', wt: 700, align: 'center' });
      const row = (txt, i, o = {}) => cell(g, x + 14, ty + 70 + i * rh, tw - 28, rh - 8, txt, { px: 26, ...o });
      row(key, 0, { color: PAL.dim });
      F.forEach((f, i) => { const tt = s._inc + 0.3 + j * 0.15 + i * 0.05, u = seg(t, tt, tt + 0.35); if (u <= 0) return;
        g.save(); g.globalAlpha *= clamp(u * 2); g.translate(0, (1 - eo(u)) * -120); row(f, i + 1); g.restore(); });
      if (chg) { const u = drop(t, s._chg + 0.35 + j * 0.12, 0.3); if (u > 0) { g.save(); g.globalAlpha *= clamp(u * 2); row(nf, F.length + 1, { accent: true }); g.restore(); } }
      g.restore(); });
    if (t > s._inc + 0.6) T(g, '.INCLUDE ' + st + ' in each table', X0, ty + 70 + 5 * rh + 80, 30, { fam: 'mono', wt: 600, color: PAL.dim, alpha: ss(seg(t, s._inc + 0.6, s._inc + 0.9)) });
    if (chg) pill(g, 'change it once → every table has it', ty + 70 + 5 * rh + 130, drop(t, s._chg + 0.8, 0.3), { accent: true });
  },
};
const append = {
  plan(s) { s._sap = Math.max(s.t0 + 0.3, cue(s, s.say_sap || 'belongs', 0.15, s.t0)); s._mod = Math.max(s._sap + 0.6, cue(s, s.say_mod || 'modification', 0.35, s._sap));
    s._app = Math.max(s._mod + 1.0, cue(s, s.say_app || 'append', 0.55, s._mod)); s._end = Math.max(s._app + 0.8, cue(s, s.say_end || 'end', 0.75, s._app));
    s._safe = Math.max(s._end + 0.6, cue(s, s.say_safe || 'untouched', 0.92, s._end));
    return [['glint', s._sap], ['bump', s._mod], ['error', s._mod + 0.1], ['fly', s._app], ['snap', s._end], ['ping', s._safe]]; },
  cam(s, t) { const u = seg(t, s._mod, s._mod + 0.3); return { sx: u > 0 && u < 1 ? Math.sin(t * 90) * 8 * (1 - u) : 0 }; },
  draw(g, s, t) {
    const y0 = head(g, s, t) + 10, tab = s.table || 'VBAK', R = s.rows || ['VBELN', 'ERDAT', 'NETWR', 'WAERK'], ap = s.append_name || 'ZAVBAK', nf = s.field || 'ZZPRIORITY';
    const rh = 60, docked = t >= s._end + 0.4, n = R.length + (docked ? 1 : 0), H = 90 + n * rh + 20;
    if (card(g, X0, y0, CW, H, drop(t, s.t0 + 0.1, 0.35), { ring: t >= s._safe ? rgba(ACC, 0.8) : null })) {
      icon(g, 'lock', X0 + 56, y0 + 48, 40, t >= s._sap ? ACC : PAL.dim);
      T(g, tab + ' · SAP table', X0 + 100, y0 + 48, 34, { fam: 'mono', wt: 700 });
      R.forEach((r, i) => cell(g, X0 + 30, y0 + 90 + i * rh, CW - 60, rh - 10, r, { px: 30, align: 'left', color: '#D5D9E3' }));
      if (docked) { const u = drop(t, s._end + 0.4, 0.3); g.save(); g.globalAlpha *= clamp(u * 2); cell(g, X0 + 30, y0 + 90 + R.length * rh, CW - 60, rh - 10, nf + '   ← from ' + ap, { px: 30, align: 'left', accent: true }); g.restore(); }
      g.restore(); }
    const by = y0 + 90 + R.length * rh + 60;
    // the direct edit attempt
    if (t >= s._mod && t < s._app + 0.4) { const fade = 1 - seg(t, s._app, s._app + 0.4); g.save(); g.globalAlpha *= fade;
      const u = seg(t, s._mod - 0.3, s._mod); cell(g, X0 + 30, y0 + 90 + 1.5 * rh - 25 + (1 - eo(u)) * -40, CW - 60, rh - 10, '+ PRIORITY (edit VBAK itself)', { px: 28, align: 'left', ring: PAL.red, fill: PAL.surf3, color: '#FFB3B5' });
      pill(g, 'modification of SAP’s own table', by, drop(t, s._mod + 0.1, 0.3), { red: true }); g.restore(); }
    // the append structure flies in and docks
    if (t >= s._app && !docked) { const a = drop(t, s._app, 0.35), d = seg(t, s._end, s._end + 0.4), yy = lerp(by + 20, y0 + 90 + R.length * rh - 70, eio(d));
      g.save(); g.globalAlpha *= clamp(a * 2) * (1 - seg(t, s._end + 0.3, s._end + 0.4));
      const p = new Path2D(); p.roundRect(X0 + 60, yy, CW - 120, 160, 22); E.panel(g, X0 + 60, yy, CW - 120, 160, { r: 22, fill: PAL.surf3, shadow: 0.8 }); g.strokeStyle = rgba(ACC, 0.9); g.lineWidth = 3; g.stroke(p);
      T(g, ap + ' · append structure', X0 + 100, yy + 44, 30, { fam: 'mono', wt: 700, color: ACC });
      cell(g, X0 + 90, yy + 80, CW - 180, 56, nf, { px: 30, align: 'left' }); g.restore(); }
    if (t >= s._safe) pill(g, tab + ' unchanged · your fields at the end', by + 40, drop(t, s._safe, 0.3), { accent: true });
  },
};
export default { reuse, append };
