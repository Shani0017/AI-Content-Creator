"""Shared engine for the ASMR ball-simulation series: pacing governor, particles, audio synth, renderer."""
import math, os, random, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = Path(__file__).resolve().parent
FFMPEG = os.environ.get("FORGE_FFMPEG", "ffmpeg")
IMPACT, ARIAL = "C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"
PENT = [0, 2, 4, 7, 9]
MAJOR = [0, 2, 4, 5, 7, 9, 11]
_fc = {}


def font(sz, f=IMPACT):
    k = (sz, f)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(f, sz)
    return _fc[k]


def ctext(d, text, y, fnt, fill, shadow=True):
    w = d.textlength(text, font=fnt)
    if shadow:
        d.text(((W - w) / 2 + 3, y + 3), text, font=fnt, fill=(0, 0, 0))
    d.text(((W - w) / 2, y), text, font=fnt, fill=fill)


def hsv(h, s=0.8, v=1.0):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def reflect(vx, vy, nx, ny):
    dot = vx * nx + vy * ny
    return vx - 2 * dot * nx, vy - 2 * dot * ny


class Sim:
    TITLE, SUB = "SIM", "RULE"
    T_END = 68.0
    SEED = 1
    BG = (8, 10, 18)
    ACC = (120, 200, 255)
    SOUND = "pluck"
    SCALE = PENT
    BASE_NOTE = 220.0
    COUNTER = "PROGRESS"
    TIMESCALE = False
    FIN = 0.97
    TS = True   # False: constant real-time physics (batch 2)
    HONEST = False  # True: every contact counts, pacing via time-scale, p = rem/M

    def __init__(self):
        self.rng = random.Random(self.SEED)
        self.t = 0.0
        self.p = 0.0
        self.events = []
        self.parts = []
        self.done_at = None
        self.setup()

    # ---- pacing governor: damage scales so progress tracks a schedule, whatever the sim does
    def target(self):
        x = min(1.0, self.t / self.T_END)
        return x * x * (3 - 2 * x) * 0.55 + x * 0.45

    def gain(self):
        return max(0.04, min(7.0, 1.0 + 7.0 * (self.target() - self.p)))

    def add(self, w):
        if self.done_at is None:
            self.p = min(1.0, self.p + w * self.gain())

    def quota(self, total, removed):
        return int(self.p * total + 1e-9) - removed

    # ---- helpers
    def ev(self, kind="hit", v=0.5):
        self.events.append((self.t, kind, v))

    def burst(self, x, y, col, n=8, sp=240, life=0.55):
        for _ in range(n):
            a = self.rng.uniform(0, 6.283)
            s = self.rng.uniform(sp * 0.3, sp)
            self.parts.append([x, y, math.cos(a) * s, math.sin(a) * s, life, col])

    def tick_parts(self, dt):
        for q in self.parts:
            q[0] += q[2] * dt
            q[1] += q[3] * dt
            q[4] -= dt
        self.parts = [q for q in self.parts if q[4] > 0]

    def draw_parts(self, d):
        for q in self.parts:
            a = max(0.0, min(1.0, q[4] / 0.4))
            r = 3 + 2 * a
            d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=tuple(int(c * a) for c in q[5]))

    LIST, AIDX = None, 3

    def sweep(self):
        """finale: clear one leftover element with its normal effect; False when none left"""
        for it in getattr(self, self.LIST):
            if it[self.AIDX]:
                it[self.AIDX] = False
                self.rem += 1
                self.burst(it[0], it[1], hsv(self.rem / self.M), 6, 240, 0.5)
                self.ev("hit", (self.rem / self.M) % 1)
                self.p = min(0.999, self.rem / self.M)
                return True
        return False

    # ---- per-sim overrides
    def setup(self):
        pass

    def physics(self, dt):
        pass

    def draw(self, d):
        pass

    def stats(self):
        return []

    # ---- loop
    def step(self, dt):
        self.t += dt
        sdt = dt
        if (self.HONEST or self.TIMESCALE) and self.TS and self.done_at is None:
            sdt = dt * max(0.9, min(2.0, self.gain()))
        n = max(1, math.ceil(sdt / (1 / 180)))
        for _ in range(n):
            self.physics(sdt / n)
        if self.HONEST and self.done_at is None:
            self.p = min(1.0, self.rem / self.M)
            if self.p >= self.FIN:
                self.p = min(self.p, 0.999)
                self._sw = getattr(self, '_sw', 0) + 1
                if self._sw % 3 == 0 and not self.sweep():
                    self.p = 1.0
        self.tick_parts(dt)
        if self.p >= 1.0 and self.done_at is None:
            self.done_at = self.t
            self.ev("boom")
            for _ in range(10):
                self.burst(self.rng.uniform(150, 930), self.rng.uniform(500, 1500), hsv(self.rng.random()), 26, 420, 1.2)
        return self.done_at is not None and self.t > self.done_at + 3.5

    def hud(self, d):
        ctext(d, self.TITLE, 130, font(112), (255, 255, 255))
        ctext(d, self.SUB, 262, font(38, ARIAL), self.ACC)
        # progress bar + stats
        d.rounded_rectangle((90, 1760, W - 90, 1790), radius=15, fill=(32, 34, 44))
        if self.p > 0.003:
            d.rounded_rectangle((90, 1760, 90 + (W - 180) * self.p, 1790), radius=15, fill=self.ACC)
        ctext(d, f"{self.COUNTER}  {int(self.p * 100)}%", 1690, font(54), (255, 255, 255))
        s = self.stats()
        for i, line in enumerate(s):
            ctext(d, line, 1805 + i * 0, font(44), (230, 230, 230)) if i == 0 else None
        if self.done_at is not None:
            ctext(d, "COMPLETE!", 860, font(180), (255, 224, 90))


# ================================================================ audio
def synth(kind, f, dur=0.35, amp=0.25):
    sr = 44100
    L = int(dur * sr)
    t = np.arange(L) / sr
    if kind == "pluck":
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 11) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 18)
    elif kind == "marimba":
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 9) + 0.5 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)
    elif kind == "bell":
        s = (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * 2.76 * f * t) + 0.3 * np.sin(2 * np.pi * 5.4 * f * t)) * np.exp(-t * 6)
    elif kind == "pop":
        s = np.sin(2 * np.pi * (f * 1.5 * np.exp(-t * 30) + f * 0.3) * t) * np.exp(-t * 28)
    elif kind == "click":
        s = np.sin(2 * np.pi * f * 3 * t) * np.exp(-t * 90) + (np.random.default_rng(2).random(L) * 2 - 1) * np.exp(-t * 200) * 0.3
    elif kind == "glass":
        s = (np.sin(2 * np.pi * f * 2 * t) + 0.5 * np.sin(2 * np.pi * f * 3.01 * t)) * np.exp(-t * 14)
    elif kind == "piano":
        s = np.zeros(L)
        for h, (a, dk) in enumerate(((1.0, 2.6), (0.55, 3.6), (0.28, 5.0), (0.15, 6.5), (0.08, 8.0), (0.04, 10.0)), 1):
            s += a * np.sin(2 * np.pi * h * f * (1 + 0.0004 * h * h) * t) * np.exp(-t * dk)
        s *= np.minimum(1.0, t / 0.004)
        s += (np.random.default_rng(5).random(L) * 2 - 1) * np.exp(-t * 400) * 0.08
    elif kind == "xylo":                              # bright wooden bar: fundamental + inharmonic overtone + tiny mallet click
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 6.5) + 0.45 * np.sin(2 * np.pi * 3.9 * f * t) * np.exp(-t * 22) + 0.15 * np.sin(2 * np.pi * 9.2 * f * t) * np.exp(-t * 45)
        s *= np.minimum(1.0, t / 0.002)
        s += (np.random.default_rng(7).random(L) * 2 - 1) * np.exp(-t * 600) * 0.12
    elif kind == "kick":
        s = np.sin(2 * np.pi * (45 + 120 * np.exp(-t * 22)) * t) * np.exp(-t * 7)
    else:
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 14)
    return (s * amp).astype(np.float32)


def make_audio(sim, dur, path):
    sr = 44100
    buf = np.zeros(int((dur + 1.5) * sr), dtype=np.float32)
    last = {}
    cache = {}
    scale = sim.SCALE
    for (t, k, v) in sim.events:
        i0 = int(t * sr)
        if k == "boom":
            L = int(1.8 * sr)
            tt = np.arange(L) / sr
            s = np.sin(2 * np.pi * (55 + 100 * np.exp(-tt * 5)) * tt) * np.exp(-tt * 2.4) * 0.85
            s += (np.random.default_rng(1).random(L) * 2 - 1) * np.exp(-tt * 8) * 0.4
            for j, fq in enumerate((523, 659, 784, 1047)):
                o = int(0.12 * j * sr)
                b = synth("bell", fq, 1.4, 0.18)
                if i0 + o + len(b) < len(buf):
                    buf[i0 + o:i0 + o + len(b)] += b
            buf[i0:i0 + L] += s[:len(buf) - i0]
            continue
        if k == "crack":                                  # brick breaking: noise crunch + low thump (v = 0..1 variation)
            L = int(0.22 * sr)
            tt = np.arange(L) / sr
            rg = np.random.default_rng(i0 % 100003)
            nz = rg.random(L) * 2 - 1
            nz = np.diff(np.concatenate([[0], nz]))                       # crude high-pass
            s = nz * np.exp(-tt * (28 + 20 * v)) * 0.55 + np.sin(2 * np.pi * (150 + 90 * v) * tt) * np.exp(-tt * 30) * 0.5
            s = (s * 0.8 * getattr(sim, "CRACK_VOL", 1.0)).astype(np.float32)
            if i0 + L < len(buf):
                buf[i0:i0 + L] += s
            continue
        if k == "note":                                   # explicit MIDI note (v = MIDI number), no debounce, chords allowed
            f = 440.0 * 2 ** ((v - 69) / 12)
            ns = getattr(sim, "NOTE_SYNTH", "piano")
            ck = (ns, round(f, 2))
            if ck not in cache:
                cache[ck] = synth(ns, f, 1.7, 0.2 * getattr(sim, "NOTE_VOL", 1.0))
            nb = cache[ck]
            if i0 + len(nb) < len(buf):
                buf[i0:i0 + len(nb)] += nb
            continue
        key = (k, int(v * 20))
        if t - last.get(k, -1) < 0.035:
            continue
        last[k] = t
        idx = int(v * 24)
        note = scale[idx % len(scale)] + 12 * (idx // len(scale) % 3)
        f = sim.BASE_NOTE * 2 ** (note / 12)
        kind = sim.SOUND if k == "hit" else ("bell" if k == "special" else ("pop" if k == "pop" else sim.SOUND))
        ck = (kind, round(f, 1))
        if ck not in cache:
            cache[ck] = synth(kind, f, 0.3, 0.16)
        s = cache[ck]
        if i0 + len(s) < len(buf):
            buf[i0:i0 + len(s)] += s
    tt = np.arange(len(buf)) / sr
    buf += (np.sin(2 * np.pi * (60 + 35 * tt / dur) * tt) * 0.035 * np.minimum(1, tt / 3)).astype(np.float32)
    buf /= max(1.0, float(np.abs(buf).max()) / 0.9)
    buf *= np.clip((len(buf) / sr - tt) / 1.2, 0, 1).astype(np.float32)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())


# ================================================================ run
def run(cls, out_path, dry=False):
    sim = cls()
    if dry:
        while True:
            if sim.step(1 / 60) or sim.t > 120:
                break
        print(cls.__name__, "done_at", sim.done_at and round(sim.done_at, 1), "ends", round(sim.t, 1), "events", len(sim.events))
        return sim.t
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_v = out_path.with_suffix(".v.mp4")
    wav = out_path.with_suffix(".wav")
    ff = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(tmp_v)], stdin=subprocess.PIPE)
    frames = 0
    while True:
        end = False
        for _ in range(2):
            end = sim.step(1 / 60)
        img = Image.new("RGB", (W, H), sim.BG)
        d = ImageDraw.Draw(img)
        sim.draw(d)
        sim.draw_parts(d)
        sim.hud(d)
        ff.stdin.write(img.tobytes())
        frames += 1
        if end or sim.t > 88:
            break
    ff.stdin.close()
    ff.wait()
    dur = frames / FPS
    make_audio(sim, dur, wav)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(tmp_v), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path)], check=True)
    tmp_v.unlink()
    wav.unlink()
    print(cls.__name__, "rendered", round(dur, 1), "s ->", out_path.name)
    return dur
