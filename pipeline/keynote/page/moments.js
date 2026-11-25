// moments.js — story scenes from test reel C ("Lock objects", approved 25 Nov), made reusable.
// Use in a day file as a slide: {"kind": "scene", "scene": "<name>", ...params, "voiceover": "..."}.
// Every reel gets 2+ story moments that fit its topic: these built-ins with topic params, or a custom scene
// written for that reel in pipeline/keynote/page/scenes/<slug>.js (same API, see README "Story scenes").
//
// Coordinates: s.Y is the slide's world centre; sy(s, v) = world y for screen y v (camera at zoom 1).
import { H_ } from './reel.js';
const { E, T, measure, fitPx, rich, chip, drop, blink, plain, cue, seqCues, padlock, pointer, mark, X0, CW, ACC } = H_;
const { PAL, clamp, lerp, seg, ss, eo, eio, back, hash, TAU, rr, font, rgba } = E;
export const sy = (s, v) => s.Y - 1000 + v;
const glowDot = (g, x, y) => { E.glow(g, x, y, 26, ACC, 0.5); g.fillStyle = ACC; g.beginPath(); g.arc(x, y, 9, 0, TAU); g.fill(); };
export function title(g, s, t, v = 340) {        // optional hook title at the top of a scene
  if (!s.title) return; rich(g, s.title, X0, sy(s, v), 64, { wt: 700, maxLines: 2, reveal: k => seg(t, s.t0 - 0.2 + k * 0.05, s.t0 + 0.05 + k * 0.05) });
}
export function field(g, x, y, w, h, val, o = {}) {
  const { caret = false, t = 0, color = PAL.text, ring = null, px = 40 } = o;
  g.save(); g.fillStyle = 'rgba(255,255,255,.045)'; rr(g, x, y, w, h, 12); g.fill();
  g.strokeStyle = ring || 'rgba(255,255,255,.12)'; g.lineWidth = ring ? 3 : 1; rr(g, x + 0.5, y + 0.5, w - 1, h - 1, 12); g.stroke();
  const tw = T(g, val, x + 22, y + h / 2 + 1, fitPx(g, val, px, w - 50, 600, 'mono'), { wt: 600, fam: 'mono', color });
  if (caret) E.caret(g, x + 30 + tw, y + h / 2, h * 0.56, { color: '#F2F4F8', on: blink(t), glow: 0.3 });
  g.restore();
}
export function button(g, x, y, w, h, label, press = 0) {
  g.save(); const k = 1 - press * 0.06; g.translate(x + w / 2, y + h / 2); g.scale(k, k);
  E.panel(g, -w / 2, -h / 2, w, h, { r: 14, fill: press > 0.01 ? '#2A3040' : PAL.surf3, shadow: 0.6 });
  T(g, label, 0, 1, 30, { wt: 600, align: 'center' }); g.restore();
}
export function collapse(g, r, t, t0) {             // CRT-off: squash an element into a line, then a point
  const k = seg(t, t0, t0 + 0.28); if (k <= 0) return true; if (k >= 1) return false;
  const cx = r[0] + r[2] / 2, cy = r[1] + r[3] / 2, sy_ = Math.max(0.02, 1 - eo(k / 0.6)), sx = k < 0.6 ? 1 : 1 - eo((k - 0.6) / 0.4);
  g.translate(cx, cy); g.scale(Math.max(0.01, sx), sy_); g.translate(-cx, -cy); return true;
}
export function icon(g, kind, x, y, s, color) {
  g.save(); g.strokeStyle = color; g.fillStyle = color; g.lineWidth = s * 0.1; g.lineCap = 'round'; g.lineJoin = 'round';
  const u = s * 0.4;
  switch (kind) {
    case 'lock': padlock(g, x, y - s * 0.15, s, color); break;
    case 'open': padlock(g, x, y - s * 0.15, s, color, 1); break;
    case 'edit': g.beginPath(); g.moveTo(x - u, y + u); g.lineTo(x + s * 0.3, y - s * 0.3); g.stroke(); g.beginPath(); g.moveTo(x - s * 0.45, y + s * 0.45); g.lineTo(x - s * 0.3, y + s * 0.1); g.lineTo(x - s * 0.1, y + s * 0.3); g.closePath(); g.fill(); break;
    case 'save': rr(g, x - u, y - u, 2 * u, 2 * u, s * 0.1); g.stroke(); g.fillRect(x - s * 0.2, y - u, s * 0.4, s * 0.25); break;
    case 'send': g.beginPath(); g.moveTo(x - s * 0.5, y - s * 0.05); g.lineTo(x + s * 0.5, y - s * 0.45); g.lineTo(x + s * 0.15, y + s * 0.5); g.lineTo(x - s * 0.05, y + s * 0.1); g.closePath(); g.fill(); break;
    case 'check': mark(g, 'ok', x, y, s * 0.9, color); break;
    case 'cross': mark(g, 'no', x, y, s * 0.9, color); break;
    case 'key': g.beginPath(); g.arc(x - u * 0.6, y, u * 0.55, 0, TAU); g.stroke(); g.beginPath(); g.moveTo(x - u * 0.05, y); g.lineTo(x + u, y); g.lineTo(x + u, y + u * 0.45); g.moveTo(x + u * 0.55, y); g.lineTo(x + u * 0.55, y + u * 0.35); g.stroke(); break;
    case 'table': rr(g, x - u, y - u * 0.8, 2 * u, 1.6 * u, s * 0.06); g.stroke(); g.beginPath(); g.moveTo(x - u, y - u * 0.25); g.lineTo(x + u, y - u * 0.25); g.moveTo(x - u * 0.2, y - u * 0.8); g.lineTo(x - u * 0.2, y + u * 0.8); g.stroke(); break;
    case 'code': g.beginPath(); g.moveTo(x - u * 0.4, y - u * 0.6); g.lineTo(x - u, y); g.lineTo(x - u * 0.4, y + u * 0.6); g.moveTo(x + u * 0.4, y - u * 0.6); g.lineTo(x + u, y); g.lineTo(x + u * 0.4, y + u * 0.6); g.stroke(); break;
    case 'search': g.beginPath(); g.arc(x - u * 0.2, y - u * 0.2, u * 0.6, 0, TAU); g.moveTo(x + u * 0.25, y + u * 0.25); g.lineTo(x + u, y + u); g.stroke(); break;
    case 'warn': g.beginPath(); g.moveTo(x, y - u); g.lineTo(x + u, y + u * 0.8); g.lineTo(x - u, y + u * 0.8); g.closePath(); g.stroke(); g.fillRect(x - s * 0.04, y - u * 0.3, s * 0.08, u * 0.6); g.fillRect(x - s * 0.04, y + u * 0.45, s * 0.08, s * 0.08); break;
    case 'clock': g.beginPath(); g.arc(x, y, u, 0, TAU); g.moveTo(x, y - u * 0.6); g.lineTo(x, y); g.lineTo(x + u * 0.45, y + u * 0.3); g.stroke(); break;
    case 'user': g.beginPath(); g.arc(x, y - u * 0.4, u * 0.45, 0, TAU); g.fill(); g.beginPath(); g.arc(x, y + u * 0.9, u * 0.85, Math.PI, 0); g.fill(); break;
    case 'db': g.beginPath(); g.ellipse(x, y - u * 0.6, u, u * 0.35, 0, 0, TAU); g.stroke(); g.beginPath(); g.moveTo(x - u, y - u * 0.6); g.lineTo(x - u, y + u * 0.6); g.ellipse(x, y + u * 0.6, u, u * 0.35, 0, Math.PI, 0, true); g.lineTo(x + u, y - u * 0.6); g.stroke(); break;
    default: g.beginPath(); g.arc(x, y, u * 0.5, 0, TAU); g.fill();
  }
  g.restore();
}

// ───────── collision: two sides write to one target; the second silently overwrites the first ─────────
// {a: {who, label, from, value}, b: {...}, target: {title}, say_a, say_b, say_bad, zeros: true|false, say_zero, lost_label}
export const collision = {
  plan(s) {
    s._ta = s.t0 + 0.25; s._ty = s.t0 + 0.7;
    s._sb = Math.max(s.t0 + 1.4, cue(s, s.say_b || 'wipes', 0.35, s.t0)); s._sa = s._sb - 0.36;
    s._z = s.zeros === false ? null : cue(s, s.say_zero || 'error', 0.5, s._sb);
    s._bad = Math.max(s._sb + 0.9, cue(s, s.say_bad || 'wrong', 0.75, s._sb));
    return [['whoosh', s._ta], ['pop', s._ta + 0.3], ['key', s._ty], ['key', s._ty + 0.15], ['key', s._ty + 0.3], ['click', s._sa], ['fly', s._sa + 0.03], ['land', s._sa + 0.3],
      ['click', s._sb], ['fly', s._sb + 0.03], ['glitch', s._sb + 0.3]].concat(s._z ? [['pop', s._z], ['digit', s._z + 0.45]] : [], [['error', s._bad]]);
  },
  cam(s, t) { const u = seg(t, s._sb + 0.3, s._sb + 0.6); return { zoom: lerp(1.0, 1.05, seg(t, s.t0, s._sb)) - 0.08 * ss(seg(t, s._bad, s.t1)), sx: u > 0 && u < 1 ? Math.sin(t * 90) * 14 * (1 - u) : 0, rot: 0.012 * ss(seg(t, s._bad, s.t1)) }; },
  draw(g, s, t) {
    title(g, s, t, 345);
    const A = s.a || {}, B = s.b || {}, tg = s.target || {};
    const WA = [X0, sy(s, 440), CW, 230], WB = [X0, sy(s, 1050), CW, 230], DB = [X0 + 150, sy(s, 745), CW - 300, 230];
    const win = (r, o, tin, from, typing, val, saveAt, dimK) => {
      const p = drop(t, tin, 0.34); if (p <= 0) return; g.save(); g.translate(0, (1 - p) * from); g.globalAlpha *= clamp(p * 3);
      E.windowBox(g, r[0], r[1], r[2], r[3], { title: o.who || 'USER', app: 2, bar: 56 });
      T(g, o.label || 'Value', r[0] + 36, r[1] + 56 + 86, 34, { color: PAL.dim });
      field(g, r[0] + 280, r[1] + 56 + 40, 270, 92, val, { caret: typing, t });
      const pr = Math.max(0, 1 - Math.abs(t - saveAt) / 0.12); button(g, r[0] + 600, r[1] + 56 + 40, 270, 92, t > saveAt + 0.1 ? 'Saved ✓' : 'Save', pr);
      g.restore(); };
    const va = t < s._ty ? String(A.from ?? '') : String(A.value ?? '').slice(0, Math.round(String(A.value ?? '').length * clamp((t - s._ty) / 0.35)));
    const vb = t < s._ty + 0.25 ? String(B.from ?? '') : String(B.value ?? '').slice(0, Math.round(String(B.value ?? '').length * clamp((t - s._ty - 0.25) / 0.35)));
    win(WA, A, s._ta - 0.15, -260, t > s._ty - 0.05 && t < s._sa - 0.2, va, s._sa);
    win(WB, B, s._ta, 260, t > s._ty + 0.2 && t < s._sb - 0.2, vb, s._sb);
    const pd = drop(t, s._ta + 0.3, 0.3); const bad = ss(seg(t, s._bad - 0.1, s._bad + 0.25));
    if (pd > 0) { g.save(); const cx = DB[0] + DB[2] / 2, cy = DB[1] + DB[3] / 2; g.translate(cx, cy); g.scale(lerp(0.6, 1, pd), lerp(0.6, 1, pd)); g.translate(-cx, -cy); g.globalAlpha *= clamp(pd * 3);
      const path = new Path2D(); path.roundRect(...DB, 22); E.litShape(g, path, { bbox: DB });
      T(g, plain(tg.title || 'DATABASE').toUpperCase(), DB[0] + 34, DB[1] + 46, 26, { fam: 'mono', wt: 700, color: PAL.mute });
      const v = t < s._sa + 0.3 ? String(A.from ?? '') : t < s._sb + 0.3 ? String(A.value ?? '') : String(B.value ?? '');
      const pop = t > s._sa + 0.3 && t < s._sa + 0.55 ? 1.12 : t > s._sb + 0.3 && t < s._sb + 0.6 ? 1.18 : 1;
      g.save(); g.translate(cx, DB[1] + 145); g.scale(pop, pop); T(g, v, 0, 0, fitPx(g, v, 104, DB[2] - 60, 600, 'disp'), { wt: 600, fam: 'disp', align: 'center', color: bad > 0 ? E.mix('#E8EAF0', PAL.red, bad) : PAL.text }); g.restore();
      if (bad > 0) { g.strokeStyle = rgba(PAL.red, 0.9 * bad); g.lineWidth = 3; rr(g, DB[0] - 6, DB[1] - 6, DB[2] + 12, DB[3] + 12, 26); g.stroke(); }
      g.restore(); }
    const chipFly = (txt, fx, fy, t0) => { const p = seg(t, t0, t0 + 0.3); if (p <= 0 || p >= 1) return;
      const to = { x: DB[0] + DB[2] / 2, y: DB[1] + 145 }, fp = E.flyPose({ x: fx, y: fy }, to, p), bend = Math.sin(p * Math.PI) * (fy < to.y ? 120 : -120);
      const w = Math.max(140, measure(g, txt, 48, 600, 'mono') + 60); E.panel(g, fp.x + bend - w / 2, fp.y - 44, w, 88, { r: 44, fill: PAL.surf3, shadow: 0.6 });
      T(g, txt, fp.x + bend, fp.y + 2, 48, { wt: 600, fam: 'mono', align: 'center' }); };
    chipFly(String(A.value ?? ''), WA[0] + 415, WA[1] + 142, s._sa + 0.03); chipFly(String(B.value ?? ''), WB[0] + 415, WB[1] + 142, s._sb + 0.03);
    const ps = seg(t, s._sb + 0.3, s._sb + 0.9);
    if (ps > 0 && ps < 1) for (let k = 0; k < 7; k++) { const an = -Math.PI / 2 + (k - 3) * 0.42, d = eo(ps) * (160 + hash(k) * 120);
      g.save(); g.globalAlpha = 1 - ps; g.fillStyle = k % 2 ? PAL.red : PAL.dim; g.translate(DB[0] + DB[2] / 2 + Math.cos(an) * d * 1.6, DB[1] + 145 + Math.sin(an) * d + ps * ps * 260); g.rotate(ps * (k - 3)); g.fillRect(-14, -6, 28, 12); g.restore(); }
    if (t < s._sb + 0.6) { const ptr = (r, t1) => { const p = eio(seg(t, t1 - 0.4, t1)); if (t < t1 - 0.7) return; pointer(g, lerp(r[0] + 560, r[0] + 760, p), lerp(r[1] + 220, r[1] + 145, p), Math.max(0, 1 - Math.abs(t - t1) / 0.1)); };
      ptr(WA, s._sa); ptr(WB, s._sb); }
    if (s._z) { ['ERRORS', 'WARNINGS'].forEach((lb, k) => { const p = drop(t, s._z + k * 0.4, 0.26); if (p <= 0) return; const x = X0 + k * (CW / 2 + 10), y = sy(s, 1305) + (1 - p) * 30;
      g.save(); g.globalAlpha *= clamp(p * 2); E.panel(g, x, y, CW / 2 - 10, 84, { r: 42, fill: PAL.surf2, shadow: 0.6 });
      T(g, lb, x + 34, y + 43, 28, { fam: 'mono', wt: 700, color: PAL.dim }); E.scramble(g, '0', x + CW / 2 - 70, y + 62, t, [s._z + k * 0.4 + 0.45], { px: 56, start: s._z + k * 0.4, align: 'center' }); g.restore(); }); }
    if (bad > 0) { const x0 = WA[0] + 415, y0 = WA[1] + WA[3] + 6, y1 = DB[1] - 8;
      g.save(); g.strokeStyle = rgba(PAL.red, 0.85 * bad); g.lineWidth = 3; g.setLineDash([10, 9]); g.beginPath(); g.moveTo(x0, y0); g.lineTo(x0, lerp(y0, y1, bad)); g.stroke(); g.setLineDash([]);
      E.badge(g, x0 + 150, (y0 + y1) / 2, s.lost_label || `LOST: ${A.value}`, 2.2 * bad); g.restore(); }
  },
};

// ───────── sign: a freeze, a push-in, and an accent sign drops and swings onto the target; flips at a word ─────────
// {target: {title, value}, texts: ["LOCKED", "OCCUPIED"], say, flip_say, door: true, note, note_say}
export const sign = {
  plan(s) {
    s._d = Math.max(s.t0 + 0.6, cue(s, s.say || 'lock', 0.2, s.t0)); s._f = (s.texts || []).length > 1 ? Math.max(s._d + 0.6, cue(s, s.flip_say, 0.55, s._d)) : null;
    s._door = s.door ? Math.max((s._f || s._d) + 0.3, s._d + 0.8) : null; s._n = s.note ? Math.max(s._d + 0.8, cue(s, s.note_say, 0.8, s._d)) : null;
    return [['zero', s.t0 - 0.05, { d: Math.min(0.5, s._d - s.t0) }], ['press', s._d]].concat(s._f ? [['flip', s._f - 0.1]] : [], s._door ? [['draw', s._door]] : [], s._n ? [['notify', s._n]] : []);
  },
  cam(s, t) { return { zoom: lerp(0.94, 1.12, eio(seg(t, s.t0, s._d))) }; },
  draw(g, s, t) {
    title(g, s, t, 290);
    const tg = s.target || {}; const DB = [X0 + 150, sy(s, 740), CW - 300, 240];
    const path = new Path2D(); path.roundRect(...DB, 22); E.litShape(g, path, { bbox: DB });
    T(g, plain(tg.title || '').toUpperCase(), DB[0] + 34, DB[1] + 46, 26, { fam: 'mono', wt: 700, color: PAL.mute });
    T(g, String(tg.value ?? ''), DB[0] + DB[2] / 2, DB[1] + 150, fitPx(g, String(tg.value ?? ''), 104, DB[2] - 60, 600, 'disp'), { wt: 600, fam: 'disp', align: 'center' });
    if (s._door) { const pf = eo(seg(t, s._door, s._door + 0.8)); const D = [X0 + 90, sy(s, 560), CW - 180, 760], per = 2 * (D[2] + D[3]);
      g.save(); g.strokeStyle = 'rgba(232,234,240,.55)'; g.lineWidth = 4; g.setLineDash([per * pf, per]); rr(g, ...D, 26); g.stroke(); g.setLineDash([]);
      const ph = drop(t, s._door + 0.8, 0.3); if (ph > 0) { g.fillStyle = 'rgba(232,234,240,.7)'; rr(g, D[0] + D[2] - 60, D[1] + D[3] / 2 + 60, 20 * ph, 84 * ph, 10); g.fill(); } g.restore(); }
    const pl = seg(t, s._d, s._d + 0.32); if (pl <= 0) return;
    const land = back(pl, 1.3), tt = t - s._d - 0.32;
    let swing = tt > 0 ? 0.16 * Math.exp(-tt * 2.2) * Math.sin(tt * 9) : 0;
    if (s._f && t > s._f - 0.1 && t < s._f + 0.7) swing += 0.1 * Math.sin((t - s._f) * 14) * (1 - seg(t, s._f - 0.1, s._f + 0.7));
    g.save(); g.translate(540, lerp(sy(s, 260), sy(s, 650), land)); g.rotate(swing);
    g.strokeStyle = 'rgba(232,234,240,.6)'; g.lineWidth = 3; g.beginPath(); g.moveTo(-110, 56); g.lineTo(0, 0); g.lineTo(110, 56); g.stroke();
    g.fillStyle = '#E8EAF0'; g.beginPath(); g.arc(0, 0, 7, 0, TAU); g.fill();
    const fl = s._f ? seg(t, s._f - 0.12, s._f + 0.14) : 0, scy = fl > 0 && fl < 1 ? Math.abs(Math.cos(fl * Math.PI)) : 1;
    g.translate(0, 98); g.scale(1, Math.max(0.04, scy));
    const txt = (s.texts || ['LOCKED'])[fl >= 0.5 ? 1 : 0] || ''; const w = Math.max(400, measure(g, txt, 42, 700, 'mono') + 170);
    const sg = new Path2D(); sg.roundRect(-w / 2, -46, w, 92, 46);
    E.litShape(g, sg, { accent: true, glowR: 40, bbox: [-w / 2, -46, w, 92], sweep: s._door ? seg(t, s._door + 1.0, s._door + 1.6) : null });
    padlock(g, -w / 2 + 62, -6, 54, '#0A0B0F'); T(g, txt, 28, 2, 42, { wt: 700, fam: 'mono', color: '#0A0B0F', align: 'center' });
    g.restore();
    if (s._n) { const p = drop(t, s._n, 0.3); if (p > 0) { g.save(); g.globalAlpha *= clamp(p * 2); const ny = sy(s, 1350) + (1 - p) * 20;
      E.panel(g, X0, ny, CW, 100, { r: 50, fill: PAL.surf2 }); glowDot(g, X0 + 50, ny + 50); T(g, plain(s.note), X0 + 86, ny + 51, fitPx(g, plain(s.note), 40, CW - 120)); g.restore(); } }
  },
};

// ───────── grid: 2–4 tiles fly in and snap to a grid, one per spoken word; a light trail loops through them ─────────
// {label, heading, tiles: [{title, icon, say}], loop_say: "every", accent: 0}
export const grid = {
  plan(s) {
    const tl = s.tiles || []; s._c = seqCues(s, tl.map(x => x.say || x.title), 0.1, 0.6);
    s._loop = s.loop_say ? Math.max(s._c[s._c.length - 1] + 0.35, cue(s, s.loop_say, 0.8, s._c[s._c.length - 1])) : null;
    return [['whoosh', s.t0]].concat(s._c.map(c => ['snap', c]), s._loop ? [['loop', s._loop]] : []);
  },
  draw(g, s, t) {
    let y0 = sy(s, 330);
    if (s.label) { chip(g, plain(s.label), X0, y0, { alpha: ss(seg(t, s.t0 - 0.1, s.t0 + 0.15)) }); y0 += 70; }
    if (s.heading) y0 += rich(g, s.heading, X0, y0 + 10, 72, { wt: 700, maxLines: 2, reveal: k => seg(t, s.t0 + k * 0.05, s.t0 + k * 0.05 + 0.22) }) + 50;
    const tl = s.tiles || [], n = tl.length, cols = n <= 2 ? 1 : 2, rows = Math.ceil(n / cols);
    const gap = 36, tw = (CW - gap * (cols - 1)) / cols, th = Math.min(n <= 2 ? 300 : 330, (sy(s, 1420) - y0 - gap * (rows - 1)) / rows);
    const R = i => [X0 + (i % cols) * (tw + gap), y0 + Math.floor(i / cols) * (th + gap), tw, th];
    tl.forEach((x, i) => { const r = R(i), a = ss(seg(t, s.t0 + i * 0.06, s.t0 + 0.25 + i * 0.06)) * (1 - ss(seg(t, s._c[i] - 0.05, s._c[i])));
      if (a > 0) { g.save(); g.globalAlpha *= a; g.strokeStyle = 'rgba(232,234,240,.22)'; g.lineWidth = 2; g.setLineDash([12, 10]); rr(g, ...r, 28); g.stroke(); g.setLineDash([]);
        T(g, String(i + 1).padStart(2, '0'), r[0] + r[2] / 2, r[1] + r[3] / 2, 64, { fam: 'mono', wt: 700, color: 'rgba(232,234,240,.18)', align: 'center' }); g.restore(); } });
    tl.forEach((x, i) => { const r = R(i), p = seg(t, s._c[i] - 0.3, s._c[i]); if (p <= 0) return;
      const from = { x: i % 2 ? 1500 : -500, y: r[1] + (i < 2 ? -500 : 700), rot: i % 2 ? 0.4 : -0.4 }, fp = E.flyPose(from, { x: r[0], y: r[1], rot: 0 }, p);
      const acc = i === (s.accent ?? 0), lit = s._loop && Math.abs(t - (s._loop + 0.08 + i * 0.16)) < 0.12;
      g.save(); g.translate(fp.x + r[2] / 2, fp.y + r[3] / 2); g.rotate(fp.rot);
      const path = new Path2D(); path.roundRect(-r[2] / 2, -r[3] / 2, r[2], r[3], 28);
      E.litShape(g, path, { accent: acc, glowR: acc ? 36 : 0, bbox: [-r[2] / 2, -r[3] / 2, r[2], r[3]] });
      if (lit && !acc) { g.strokeStyle = rgba(ACC, 0.8); g.lineWidth = 3; g.stroke(path); }
      const col = acc ? '#0A0B0F' : PAL.text;
      T(g, String(i + 1).padStart(2, '0'), -r[2] / 2 + 30, -r[3] / 2 + 40, 26, { fam: 'mono', wt: 700, color: acc ? 'rgba(10,11,15,.6)' : PAL.mute });
      icon(g, x.icon || 'dot', 0, -r[3] * 0.1, Math.min(96, r[3] * 0.3), col);
      rich(g, x.title, 0, r[3] * 0.28, fitPx(g, plain(x.title), 50, r[2] - 40, 700), { wt: 700, align: 'center', maxw: r[2] - 40, color: col, hi: acc ? '#0A0B0F' : ACC, maxLines: 1 });
      g.restore(); });
    if (s._loop) { const pt = seg(t, s._loop, s._loop + 0.8); if (pt > 0 && pt < 1 && n > 1) {
      const order = n === 4 ? [0, 1, 3, 2, 0] : n === 3 ? [0, 1, 2, 0] : [0, 1, 0]; const C = order.map(i => { const r = R(i); return [r[0] + r[2] / 2, r[1] + r[3] / 2]; });
      const L = C.length - 1, pts = [], head = pt * L;
      for (let j = 0; j <= 60; j++) { const u = Math.max(0, head - 1.2 + 1.2 * j / 60), q = Math.min(L - 0.001, u), a = Math.floor(q), f = q - a; pts.push([lerp(C[a][0], C[a + 1][0], f), lerp(C[a][1], C[a + 1][1], f)]); }
      E.trail(g, pts, { width: 10, caretH: 46 }); } }
  },
};

// ───────── bump: an actor runs into a blocker and bounces back; a message slides in ─────────
// {title, actor, blocker, blocker_icon: "lock", say, message, msg_say}
export const bump = {
  plan(s) { s._b = Math.max(s.t0 + 0.8, cue(s, s.say || 'holds', 0.3, s.t0)); s._m = s.message ? Math.max(s._b + 0.6, cue(s, s.msg_say || 'tell', 0.75, s._b)) : null;
    return [['whoosh', s.t0 + 0.1], ['bump', s._b]].concat(s._m ? [['notify', s._m]] : []); },
  cam(s, t) { const u = seg(t, s._b, s._b + 0.25); return { sx: u > 0 && u < 1 ? Math.sin(t * 90) * 7 * (1 - u) : 0 }; },
  draw(g, s, t) {
    title(g, s, t, 320);
    const y = sy(s, 760), a = ss(seg(t, s.t0, s.t0 + 0.3));
    const pb = seg(t, s.t0 + 0.2, s._b), bk = seg(t, s._b, s._b + 0.4);
    const aw = Math.max(260, measure(g, s.actor || 'USER_B', 38, 600, 'mono') + 80), bw = Math.max(380, measure(g, s.blocker || 'LOCKED', 38, 700, 'mono') + 150);
    const bx = X0 + CW - bw, ax = lerp(X0, bx - aw - 6, eio(pb)) - 90 * Math.sin(bk * Math.PI) * (1 - bk * 0.4);
    g.save(); g.globalAlpha *= a;
    E.panel(g, ax, y, aw, 104, { r: 52, fill: PAL.surf3, shadow: 0.7 }); T(g, s.actor || 'USER_B', ax + aw / 2, y + 53, 38, { fam: 'mono', wt: 600, align: 'center' });
    const lk = new Path2D(); lk.roundRect(bx, y, bw, 104, 52); E.litShape(g, lk, { accent: true, glowR: 30, bbox: [bx, y, bw, 104] });
    icon(g, s.blocker_icon || 'lock', bx + 62, y + 52, 52, '#0A0B0F'); T(g, s.blocker || 'LOCKED', bx + bw / 2 + 34, y + 53, 38, { fam: 'mono', wt: 700, color: '#0A0B0F', align: 'center' });
    g.restore();
    if (s._m) { const p = drop(t, s._m, 0.3); if (p > 0) { g.save(); g.globalAlpha *= clamp(p * 2); const my = sy(s, 980) + (1 - p) * 40;
      const lines = H_.tokens(plain(s.message)); const L = (() => { g.save(); g.font = font(38, 500); const w = g.measureText(plain(s.message)).width; g.restore(); return w > CW - 140 ? 2 : 1; })();
      const mh = 60 + L * 48; E.panel(g, X0, my, CW, mh, { r: 22, fill: PAL.surf2, shadow: 0.8 }); glowDot(g, X0 + 50, my + mh / 2);
      rich(g, s.message, X0 + 86, my + 52, 38, { wt: 500, maxw: CW - 130, lh: 48, maxLines: 2 }); g.restore(); } }
  },
};

// ───────── pileup: generated cards pile up faster and faster (the problem), then freeze and get swept away ─────────
// {title, item: "Short dump", sub: "COMPUTE_INT_ZERODIVIDE", count: 40, say_stop: "fix", keep: "One fix"}
export const pileup = {
  plan(s) { s._s = Math.max(s.t0 + 1.5, cue(s, s.say_stop || 'fix', 0.6, s.t0 + 1)); const n = s.count || 36; s._sp = [];
    for (let i = 0; i < n; i++) { const u = i / n; s._sp.push(s.t0 + 0.15 + (s._s - s.t0 - 0.5) * Math.sqrt(u)); }
    return s._sp.filter((_, i) => i % 3 === 0).map(t => ['ping', t]).concat([['zero', s._s - 0.35, { d: 0.35 }], ['crt', s._s], ['press', s._s + 0.45]]); },
  cam(s, t) { return { zoom: lerp(1, 0.92, seg(t, s.t0, s._s)), rot: (t < s._s ? 0.012 * seg(t, s.t0 + 0.5, s._s) : 0) }; },
  draw(g, s, t) {
    title(g, s, t, 300);
    const away = seg(t, s._s, s._s + 0.35);
    s._sp.forEach((t0, i) => { const p = drop(t, t0, 0.22); if (p <= 0 || away >= 1) return;
      const x = X0 + hash(i * 3.1) * (CW - 560), y = sy(s, 470) + hash(i * 7.7) * 760 - (1 - p) * 60;
      g.save(); g.globalAlpha *= clamp(p * 2) * (1 - away); g.translate(x + 280, y + 50); g.rotate((hash(i) - 0.5) * 0.12); g.scale(1, 1 - away * 0.95);
      E.notif(g, -280, -50, 560, 100, { app: i, title: plain(s.item || 'Item'), body: plain(s.sub || ''), time: 'now', badge: i % 5 === 0 ? '!' : null }); g.restore(); });
    if (s.keep) { const p = drop(t, s._s + 0.45, 0.32); if (p > 0) { g.save(); g.globalAlpha *= clamp(p * 2); const w = 760, x = 540 - w / 2, y = sy(s, 800);
      g.translate(540, y + 70); g.scale(lerp(0.7, 1, p), lerp(0.7, 1, p)); g.translate(-540, -(y + 70));
      const pth = new Path2D(); pth.roundRect(x, y, w, 140, 70); E.litShape(g, pth, { accent: true, glowR: 40, bbox: [x, y, w, 140] });
      T(g, plain(s.keep), 540, y + 72, fitPx(g, plain(s.keep), 52, w - 80, 700), { wt: 700, color: '#0A0B0F', align: 'center' }); g.restore(); } }
  },
};

export default { collision, sign, grid, bump, pileup };
