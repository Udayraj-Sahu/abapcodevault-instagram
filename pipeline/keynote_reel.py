"""Keynote engine (approved 25 Nov): reels in the Dark Tech Keynote style.

generate.py makes the narration (Kokoro, am_michael) exactly as before; this module turns the slides + timings into
a spec, renders the picture with the canvas page in pipeline/keynote/page (headless Chrome via playwright-core),
writes an original score + foley from the page's events, and muxes reel.mp4 at -14 LUFS.

Setup once per machine: cd pipeline/keynote && npm install   (playwright-core pinned to the preinstalled browser;
if no browser is found set PLAYWRIGHT_CHROME=/usr/bin/google-chrome).
"""
import json
import os
import re
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "keynote")
FPS = 30
SR = 48000


def _node(args, cwd=KEY):
    env = dict(os.environ)
    if not os.path.isdir(env.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")) and os.path.exists("/usr/bin/google-chrome"):
        env.setdefault("PLAYWRIGHT_CHROME", "/usr/bin/google-chrome")
    r = subprocess.run(["node"] + args, cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("keynote render failed: " + (r.stderr or r.stdout)[-2000:])
    return r.stdout


def ensure_setup():
    if not os.path.isdir(os.path.join(KEY, "node_modules", "playwright-core")):
        subprocess.run(["npm", "install", "--silent"], cwd=KEY, check=True)


# ───────── captions ─────────
def caption_chunks(slides, max_chars=28):
    caps = []
    for s in slides:
        if s.get("kind") == "cta":
            continue                                   # the end card already shows its text
        cur = None
        ws = s["words"]
        for i, (w, a, b) in enumerate(ws):
            if cur is None:
                cur = {"t0": a, "text": w, "t1": b, "w": [[round(a, 3), round(b, 3)]]}
            elif len(cur["text"]) + 1 + len(w) > max_chars:
                caps.append(cur); cur = {"t0": a, "text": w, "t1": b, "w": [[round(a, 3), round(b, 3)]]}
            else:
                cur["text"] += " " + w; cur["t1"] = b; cur["w"].append([round(a, 3), round(b, 3)])
            if re.search(r"[.?!:]$", w) and len(cur["text"]) > 10 or i == len(ws) - 1:
                caps.append(cur); cur = None
    for i, c in enumerate(caps):
        n = caps[i + 1] if i + 1 < len(caps) else None
        c["t1"] = n["t0"] - 0.02 if n and n["t0"] - c["t1"] < 0.7 else c["t1"] + 0.45
        c["text"] = c["text"].rstrip(",.;")
    return caps


# ───────── sound (numpy only) ─────────
def _t(d): return np.arange(int(d * SR)) / SR
def _env(d, tau): return np.exp(-_t(d) / tau)
_rng = np.random.default_rng(11)
def _noise(d): return _rng.standard_normal(int(d * SR))
def _hp(x): y = np.diff(x, prepend=0); return y
def _lp(x, a=0.15):
    y = np.empty_like(x); acc = 0.0
    for i in range(0, len(x), 1):
        acc += a * (x[i] - acc); y[i] = acc
    return y
def hz(m): return 440 * 2 ** ((m - 69) / 12)

def marimba(f, d=0.9, v=1.0, det=0.0):
    tt = _t(d); f *= 2 ** (det / 1200)
    x = np.sin(2*np.pi*f*tt)*_env(d, .3) + .35*np.sin(2*np.pi*f*4*tt)*_env(d, .05) + .1*np.sin(2*np.pi*f*10*tt)*_env(d, .012)
    n = int(.002*SR); x[:n] *= np.linspace(0, 1, n); return x * v
def glock(f, d=1.4, v=1.0):
    tt = _t(d); return (np.sin(2*np.pi*f*tt)*_env(d, .5) + .4*np.sin(2*np.pi*f*2.76*tt)*_env(d, .16) + .15*np.sin(2*np.pi*f*5.4*tt)*_env(d, .05)) * v
def pad(fs, d, v=1.0, att=.8, rel=1.2):
    tt = _t(d); x = sum(np.sin(2*np.pi*f*tt + i) + .25*np.sin(2*np.pi*2.003*f*tt) for i, f in enumerate(fs))
    e = np.minimum(1, tt/att) * np.clip((d - tt)/rel, 0, 1); return x * e * v / len(fs)
def click(p=1.0, v=1.0):
    d = .05; tt = _t(d); return (_hp(_noise(d))*_env(d, .0015)*.6 + np.sin(2*np.pi*2900*p*tt)*_env(d, .01)*.5 + np.sin(2*np.pi*190*p*tt)*_env(d, .01)*.4) * v
def thump(v=1.0, f=70):
    d = .35; tt = _t(d); fr = f * (1 + 1.5*np.exp(-tt*30)); return np.sin(2*np.pi*np.cumsum(fr)/SR) * _env(d, .09) * v
def whoosh(d=.4, v=1.0):
    tt = _t(d); x = _noise(d); x = x - _lp(x, .08); return x * np.sin(np.pi*tt/d)**2 * .35 * v
def sine_drop(v=1.0):
    d = .45; tt = _t(d); f = 180*np.exp(-tt*5) + 55; return np.sin(2*np.pi*np.cumsum(f)/SR) * _env(d, .15) * v
def buzz(v=1.0):
    d = .32; tt = _t(d); x = np.sign(np.sin(2*np.pi*110*tt)) * .4 * ((tt < .12) | (tt > .18)) * _env(d, .2); return x * v
def shimmer(v=1.0):
    d = .9; tt = _t(d); x = _hp(_hp(_noise(d))) * .25 * np.sin(np.pi*tt/d)**2
    for f in (hz(93), hz(97), hz(100)): x = x + .2*np.sin(2*np.pi*f*tt)*np.sin(np.pi*tt/d)
    return x * v

def glitch(v=1.0):
    d = .32; x = _noise(d) * (_rng.random(int(d*SR)) > .5); x = _hp(x) * _env(d, .09); tt = _t(d)
    x = x + .5*np.sign(np.sin(2*np.pi*90*tt)) * _env(d, .05); return x / max(1e-6, np.abs(x).max()) * v

def _add(buf, x, at, g=1.0, pan=0.0):
    s = int(at * SR)
    if s >= len(buf) or s + len(x) <= 0: return
    if s < 0: x = x[-s:]; s = 0
    e = min(len(buf), s + len(x)); l, r = np.cos((pan+1)*np.pi/4), np.sin((pan+1)*np.pi/4)
    buf[s:e, 0] += x[:e-s] * g * l * 1.41; buf[s:e, 1] += x[:e-s] * g * r * 1.41


def build_mix(dur, voice, vsr, slides, events, seed):
    from math import gcd
    N = int(dur * SR) + SR
    music, fol, vo = (np.zeros((N, 2), np.float32) for _ in range(3))
    rng = np.random.default_rng(seed)
    # voice (already polished by generate.py) → 48 kHz by linear interpolation
    if vsr != SR:
        xi = np.arange(int(len(voice) * SR / vsr)) * vsr / SR
        voice = np.interp(xi, np.arange(len(voice)), voice).astype(np.float32)
    _add(vo, voice, 0.0, 1.0)
    # score: a key per reel, 96 bpm; marimba pulse under the hook, pad + additive glockenspiel after, one chord on the end card
    keys = [[62, 65, 69, 72, 74], [60, 63, 67, 70, 72], [64, 67, 71, 74, 76], [57, 60, 64, 67, 69]]
    sc = keys[seed % len(keys)]; root = sc[0]; beat = 60 / 96
    end_t = slides[-1]["t0"] if slides[-1].get("kind") == "cta" else dur
    hook_end = slides[1]["t0"] if len(slides) > 1 else dur
    t = 0.0; i = 0
    while t < hook_end - 0.1:
        _add(music, marimba(hz(sc[[0, 3, 2, 4, 3, 2, 1, 2][i % 8]]), v=.5), t, 1.0, -.3 if i % 2 else .3)
        if i % 4 == 0: _add(music, marimba(hz(root - 24), d=1.2, v=.5), t, .8)
        t += beat / 2; i += 1
    if end_t - hook_end > 1:
        _add(music, pad([hz(root - 12), hz(root - 5), hz(root), hz(sc[1])], end_t - hook_end + .4, v=.45), hook_end, .55)
        bar = beat * 4; b = 0
        while hook_end + b * bar < end_t - .5:
            for k in range(min(b % 8 + 1, 6)):
                tt = hook_end + b * bar + k * beat / 2
                if tt < end_t - .45: _add(music, glock(hz(sc[k % 5] + 12), v=.2), tt, 1.0, (k % 2 - .5) * .5)
            _add(music, marimba(hz(root - 24), d=1.3, v=.55), hook_end + b * bar, .7)
            b += 1
    if end_t < dur:
        _add(music, pad([hz(root - 12), hz(root - 5), hz(root), hz(sc[2]), hz(sc[4])], dur - end_t + .5, v=.55, att=.3, rel=1.0), end_t, .6)
        for k, m in enumerate([sc[0], sc[2], sc[4], sc[0] + 12]): _add(music, glock(hz(m + 12), d=2.0, v=.3), end_t + .3 + k * beat / 2, 1.0)
    # foley from the picture's events
    S = {"pop": lambda: (thump(.4, 140) * .5, .35), "soft": lambda: (whoosh(.3, .5), .25), "glint": lambda: (glock(hz(93), .7, .5), .22),
         "row": lambda: (marimba(hz(sc[3] + 12), .35, .5), .28), "snap": lambda: (thump(.8, 70), .45), "click": lambda: (click(1.0, 1), .45),
         "type": lambda: (click(1.4, .6), .3), "notify": lambda: (glock(hz(sc[2] + 24), 1.0, .6), .3), "error": lambda: (buzz(1), .3),
         "key": lambda: (click(rng.uniform(1.1, 1.6), .5), .16), "tick": lambda: (glock(hz(sc[4] + 12), .4, .5), .3), "digit": lambda: (click(2.2, .5), .3),
         "move": lambda: (whoosh(.45, .6), .25), "whoosh": lambda: (whoosh(.35, .7), .35), "fly": lambda: (whoosh(.25, .5), .3),
         "land": lambda: (thump(.6, 110), .5), "glitch": lambda: (glitch(1), .5), "press": lambda: (marimba(hz(sc[0]), 1.2, .9) + np.pad(sine_drop(.8), (0, int(1.2*SR) - int(.45*SR))), .6),
         "flip": lambda: (whoosh(.2, .5), .3), "draw": lambda: (_hp(_noise(.8)) * _env(.8, .3) * .25, .2), "bump": lambda: (thump(.9, 80), .6),
         "crt": lambda: (sine_drop(.6), .35), "loop": lambda: (shimmer(.7), .3), "shimmer": lambda: (shimmer(.6), .25), "zero": lambda: (np.zeros(10), 0),
         "ping": lambda: (marimba(hz(rng.choice([sc[3] + 12, sc[4] + 12, sc[1] + 12])), .4, .45, rng.uniform(-45, 45)), .25)}
    for e in events:
        f = S.get(e["type"])
        if f:
            x, g = f(); _add(fol, np.asarray(x, np.float32), e["t"], g, rng.uniform(-.25, .25))
    # duck music under the voice, a breath of silence before the end card, then master
    k = int(.12 * SR); env = np.convolve(np.abs(vo[:, 0]), np.ones(k) / k, "same")
    duck = 1 - .6 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
    music *= duck[:, None]; fol *= (1 - .3 * (1 - duck))[:, None]
    if end_t < dur:
        a, b = int((end_t - .35) * SR), int(end_t * SR); music[a:b] = 0
    for e in events:
        if e["type"] == "zero":
            a, b = int(e["t"] * SR), int((e["t"] + e.get("d", .45)) * SR); music[a:b] = 0; fol[a:b] = 0
    mix = vo + music * .24 + fol * .5
    mix = mix[:int(dur * SR)]
    return mix / max(1e-6, np.abs(mix).max()) * .89


def make_keynote_reel(p, slides, durations, speech, vo_wav, folder, handle, word_timeline):
    import soundfile as sf
    ensure_setup()
    t, spec_slides = 0.0, []
    for s, d, (st, ln) in zip(slides, durations, speech):
        x = {k: v for k, v in s.items() if k not in ("voiceover",)}
        x.update({"t0": round(t, 3), "t1": round(t + d, 3), "st": round(t + st, 3), "ln": round(ln, 3)})
        sub = s.get("spoken") or s.get("voiceover") or ""
        tl = word_timeline(sub, t + st, ln) if (sub and ln > 0) else []
        x["words"] = [[w, round(a, 3), round(b, 3)] for c in tl for (w, a, b) in c]
        spec_slides.append(x); t += d
    dur = round(t + 0.1, 3)
    tag = p.get("tag", "")
    scenes = p.get("scenes") or f"scenes/{p.get('slug', 'reel')}.js"
    spec = {"scenes": scenes if os.path.exists(os.path.join(KEY, "page", scenes)) else None, "dur": dur, "slides": spec_slides, "caps": caption_chunks(spec_slides), "handle": handle,
            "tag": tag.upper() if tag else "", "comment": p.get("comment_word", "")}
    os.makedirs(os.path.join(KEY, "page", "jobs"), exist_ok=True)
    job = f"jobs/{p.get('slug', 'reel')}.json"
    json.dump(spec, open(os.path.join(KEY, "page", job), "w"), ensure_ascii=False)
    json.dump(spec, open(os.path.join(folder, "keynote_spec.json"), "w"), ensure_ascii=False, indent=1)
    q = f"spec={job}"
    ev_path = os.path.join(folder, "events.json")
    _node(["core/render/events.mjs", "page", "--size", "1080x1920", "--q", q, "--out", ev_path])
    events = json.load(open(ev_path))["ev"]
    vid = os.path.join(folder, "_video.mp4")
    _node(["core/render/video.mjs", "page", "--fps", str(FPS), "--workers", "4", "--size", "1080x1920", "--q", q, "--out", vid])
    voice, vsr = sf.read(vo_wav, dtype="float32") if vo_wav else (np.zeros(1, np.float32), 24000)
    if voice.ndim > 1: voice = voice.mean(1)
    seed = sum(map(ord, p.get("slug", "x")))
    mix = build_mix(dur, voice, vsr, spec_slides, events, seed)
    mix_wav = os.path.join(folder, "_mix.wav"); sf.write(mix_wav, mix, SR)
    # two-pass loudness to -14 LUFS
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix_wav, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    out = os.path.join(folder, "reel.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", mix_wav, "-af", ln, "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], check=True)
    cover_t = min(1.2, max(0.5, spec_slides[0]["t1"] - 0.3))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(cover_t), "-i", out, "-frames:v", "1", os.path.join(folder, "frame_01.png")], check=True)
    for f in (vid, mix_wav):
        os.remove(f)
    print(f"keynote reel {dur:.1f}s -> {out}")
    return out
