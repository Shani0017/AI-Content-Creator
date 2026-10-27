"""RAYS IN A CONTAINER: parallel rays fall into a flared vessel and are reflected by its walls (true specular reflection on a
polyline approximation of the curve, up to 60 bounces each). Nothing is scripted: every line you see is a traced ray.
Sets of 1 -> 2 -> 5 -> ... -> 100 rays, each ray its own colour, marimba/bell plinks on the bounces."""
import colorsys
import io
import math
import os
import random
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
FFMPEG = os.environ.get("FORGE_FFMPEG", "ffmpeg")
_FONT = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "Poppins-SemiBold.ttf"
PENT = [0, 2, 4, 7, 9]


def pent(i, base=57):
    return base + 12 * (i // 5) + PENT[i % 5]


def fnt(size, bold=True):
    """loaded from memory, so the font file is never locked (the updater must be able to replace it)"""
    try:
        return ImageFont.truetype(io.BytesIO(_FONT.read_bytes()), size)
    except Exception:
        return ImageFont.truetype("arialbd.ttf", size)


def hsv(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (r * 255, g * 255, b * 255)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class VideoOut:
    def __init__(self, tmp_path):
        self.tmp = str(tmp_path)
        self.p = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                   "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "30", self.tmp],
                                  stdin=subprocess.PIPE, creationflags=0x08000000 if os.name == "nt" else 0)

    def write(self, buf):
        self.p.stdin.write(np.clip(buf, 0, 255).astype(np.uint8).tobytes())

    def finish(self, wav_path, out_path):
        self.p.stdin.close()
        self.p.wait()
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", self.tmp, "-i", str(wav_path), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-movflags", "+faststart", str(out_path)], check=True, creationflags=0x08000000 if os.name == "nt" else 0)
        Path(self.tmp).unlink(missing_ok=True)


class Audio:
    def __init__(self, seconds):
        self.n = int((seconds + 1.5) * SR)
        self.L = np.zeros(self.n, np.float32)
        self.R = np.zeros(self.n, np.float32)

    def _put(self, t, s, pan=0.0, vol=1.0):
        i = int(t * SR)
        if i < 0 or i >= self.n:
            return
        s = s[: self.n - i] * vol
        self.L[i:i + len(s)] += s * (1 - max(pan, 0) * 0.6)
        self.R[i:i + len(s)] += s * (1 + min(pan, 0) * 0.6)

    def note(self, t, freq, vol=0.35, dur=1.6, timbre="bell", pan=0.0):
        n = int(dur * SR)
        x = np.arange(n) / SR
        if timbre == "bell":
            s = (np.sin(2 * np.pi * freq * x) + 0.5 * np.sin(2 * np.pi * freq * 2.76 * x) * np.exp(-x * 5) + 0.25 * np.sin(2 * np.pi * freq * 5.4 * x) * np.exp(-x * 9))
            env = np.exp(-x * 3.2)
        else:
            s = np.sin(2 * np.pi * freq * x) + 0.45 * np.sin(2 * np.pi * freq * 4 * x) * np.exp(-x * 14)
            env = np.exp(-x * 5.5)
        a = np.minimum(x / 0.004, 1)
        self._put(t, (s * env * a).astype(np.float32), pan, vol)

    def save(self, path):
        m = max(np.abs(self.L).max(), np.abs(self.R).max(), 1e-6)
        sf.write(str(path), np.stack([self.L, self.R], 1) / m * 0.85, SR)


CX = 540.0
STOPS = [(0.0, (40, 200, 255)), (0.33, (120, 70, 255)), (0.66, (255, 60, 170)), (1.0, (255, 160, 40))]


def grad(f, stops=STOPS):
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if f <= b:
            u = (f - a) / (b - a)
            return tuple(int(ca[k] * (1 - u) + cb[k] * u) for k in range(3))
    return stops[-1][1]


def boundary(Wt, rb, p, ytop, yc):
    ys = np.linspace(ytop, yc, 160)
    w = rb + (Wt - rb) * ((yc - ys) / (yc - ytop)) ** p
    left = np.c_[CX - w, ys]
    th = np.linspace(math.pi, 0, 40)
    bulb = np.c_[CX + rb * np.cos(th), yc + rb * np.sin(th)]
    right = np.c_[CX + w[::-1], ys[::-1]]
    return np.vstack([left, bulb[1:-1], right])


def trace(poly, starts, maxlen=4200.0, maxb=60):
    a, b = poly[:-1], poly[1:]
    e = b - a
    R = len(starts)
    p = starts.copy()
    d = np.tile([0.0, 1.0], (R, 1))
    pts = [[tuple(p[i])] for i in range(R)]
    tot = np.zeros(R)
    exited = np.zeros(R, bool)
    alive = np.ones(R, bool)
    for _ in range(maxb):
        if not alive.any():
            break
        idx = np.where(alive)[0]
        P, D = p[idx], d[idx]
        # intersect P + tD with a + u e
        den = D[:, 0:1] * e[None, :, 1] - D[:, 1:2] * e[None, :, 0]
        wx, wy = a[None, :, 0] - P[:, 0:1], a[None, :, 1] - P[:, 1:2]
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (wx * e[None, :, 1] - wy * e[None, :, 0]) / den
            u = (wx * D[:, 1:2] - wy * D[:, 0:1]) / den
        ok = (t > 1e-3) & (u >= -1e-6) & (u <= 1 + 1e-6) & (np.abs(den) > 1e-9)
        t = np.where(ok, t, np.inf)
        j = np.argmin(t, 1)
        tt = t[np.arange(len(idx)), j]
        hit = np.isfinite(tt)
        for q, i in enumerate(idx):
            if not hit[q]:
                pts[i].append(tuple(P[q] + D[q] * 1300.0))      # it left through the open top: keep flying
                tot[i] += 1300.0
                exited[i] = True
                alive[i] = False
                continue
            newp = P[q] + D[q] * tt[q]
            tot[i] += tt[q]
            pts[i].append(tuple(newp))
            ex, ey = e[j[q]]
            n = np.array([-ey, ex]) / math.hypot(ex, ey)
            nd = D[q] - 2 * (D[q] @ n) * n
            p[i] = newp + nd * 0.05
            d[i] = nd
            if tot[i] > maxlen:
                alive[i] = False
    return [np.array(x) for x in pts], exited


def render(v, out):
    poly = boundary(v["Wt"], v["rb"], v["p"], 520.0, 1330.0)
    counts = v["counts"]
    gap = 0.35
    FT = 960.0
    raw = []
    for n in counts:
        y0 = 560.0
        w_y0 = v["rb"] + (v["Wt"] - v["rb"]) * ((1330 - y0) / (1330 - 520)) ** v["p"]
        xs = np.linspace(CX - w_y0 + 6, CX + w_y0 - 6, n) if n > 1 else np.array([CX - w_y0 * 0.37])
        starts = np.c_[xs, np.full(n, y0)]
        paths_, exited = trace(poly, starts)
        cum = [np.r_[0, np.cumsum(np.hypot(*np.diff(pp, axis=0).T))] for pp in paths_]
        cutmax = max((c[-2] if e_ else c[-1]) for c, e_ in zip(cum, exited))     # when the last ray has left the funnel
        raw.append((n, paths_, exited, cum, cutmax))
    # one common ray speed: the whole reel lasts about target_len seconds (sets overlap: the next starts as the last ray of the previous left)
    tl = float(v.get("target_len", 66.0))
    sp = (sum(r[4] for r in raw) + raw[-1][4] * 0 + FT) / max(1.0, tl - gap * len(raw) - 0.6)
    sp = max(sp, float(v.get("min_speed", 180.0)))
    phases = []
    t0 = 0.5
    for n, paths_, exited, cum, cutmax in raw:
        L = max(c[-1] for c in cum)
        phases.append(dict(n=n, paths=paths_, cum=cum, exit=exited, sp=sp, t0=t0, t1=t0 + L / sp, cutmax=cutmax,
                           cols=[tuple(int(c) for c in hsv((i * 0.61803398875 + 0.11 * len(phases) + v.get("hue0", 0.0)) % 1.0, v.get("sat", 0.8), 1.0)) for i in range(n)]))   # every ray has its own colour
        t0 += cutmax / sp + gap                 # the next set starts as soon as this one has left: it overlaps the fade-out
    total = max(ph["t0"] + (ph["cutmax"] + FT) / ph["sp"] for ph in phases) + 0.6
    nF = int(total * FPS)
    ev = []
    for ph in phases:
        keep = max(1, ph["n"] // 18)
        for i, (pp, cc) in enumerate(zip(ph["paths"], ph["cum"])):
            if i % keep:
                continue
            for k in range(1, len(pp) - 1):
                ev.append((ph["t0"] + cc[k] / ph["sp"], float(pp[k, 0]), i))
    au = Audio(total)
    bins = {}
    for tt, x, i in ev:
        b = int(tt * 40)
        bins[b] = bins.get(b, 0) + 1
        if bins[b] > 2:
            continue
        q = min(14, max(0, int((x - (CX - v["Wt"])) / (2 * v["Wt"]) * 15)))
        au.note(tt, midi_hz(pent(q, 62) + 12), 0.03, 0.3, "marimba" if i % 3 else "bell", pan=(x - CX) / v["Wt"] * 0.5)
    wav = out.with_suffix(".wav")
    au.save(wav)
    vid = VideoOut(out.with_suffix(".tmp.mp4"))
    f_t = fnt(44)
    base = Image.new("RGB", (W, H), v["bg"])
    bd = ImageDraw.Draw(base)
    bd.line([tuple(p) for p in poly[:200]] , fill=(255, 255, 255), width=4)
    bd.line([tuple(p) for p in poly[199:]], fill=(255, 255, 255), width=4)
    cur = -1
    canvas = None
    lastd = None

    def at(cc, pp, dist):
        k = int(np.searchsorted(cc, dist, "right")) - 1
        k = min(max(k, 0), len(pp) - 2)
        u = (dist - cc[k]) / max(cc[k + 1] - cc[k], 1e-6)
        return pp[k] * (1 - u) + pp[k + 1] * u, k

    base_rgba = base.convert("RGBA")
    for f in range(nF):
        t = f / FPS
        started = [ph for ph in phases if ph["t0"] <= t]
        ph_cur = started[-1] if started else phases[0]
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for ph in started:                                        # all sets that are still on screen (older ones are fading out)
            dnow = max(0.0, (t - ph["t0"]) * ph["sp"])
            if dnow > ph["cutmax"] + FT:
                continue
            wid = 4 if ph["n"] <= 3 else (3 if ph["n"] <= 30 else (2 if ph["n"] <= 120 else 1))
            for i, (pp, cc) in enumerate(zip(ph["paths"], ph["cum"])):
                cut = cc[-2] if ph["exit"][i] else cc[-1]            # where the ray leaves the funnel (or where it ends)
                fade = 1.0 if dnow <= cut else max(0.0, 1.0 - (dnow - cut) / FT)
                if fade <= 0.0:
                    continue
                c = ph["cols"][i]
                d1 = min(dnow, cc[-1])
                d1c = min(d1, cut)
                if d1c > 0:
                    b_, k1 = at(cc, pp, d1c)
                    pts = [tuple(pp[k]) for k in range(0, k1 + 1)] + [tuple(b_)]
                    od.line(pts, fill=c + (int(255 * fade),), width=wid)
                if ph["exit"][i] and d1 > cut:
                    qs = np.linspace(cut, d1, 10)
                    for q0, q1 in zip(qs[:-1], qs[1:]):
                        al = max(0.0, 1.0 - (0.5 * (q0 + q1) - cut) / 800.0) * fade
                        pa, _ = at(cc, pp, q0)
                        pb, _ = at(cc, pp, q1)
                        od.line((pa[0], pa[1], pb[0], pb[1]), fill=c + (int(255 * al),), width=wid)
                if ph["n"] <= 30 and d1 < cc[-1]:
                    hp, _ = at(cc, pp, d1)
                    od.ellipse((hp[0] - 7, hp[1] - 7, hp[0] + 7, hp[1] + 7), fill=c + (int(255 * (fade if d1 > cut else 1.0)),))
        img = Image.alpha_composite(base_rgba, ov).convert("RGB")
        d = ImageDraw.Draw(img)
        d.text((W / 2, 150), f"RAYS: {ph_cur['n']}", font=f_t, fill=(255, 255, 255), anchor="mm")
        vid.write(np.asarray(img))
    vid.finish(wav, out)
    wav.unlink(missing_ok=True)
    return sum(counts)


# ------------------------------------------------------------------ random variants (the app never makes the same one twice)
SHAPES = [("Funnel", 360, 82, 2.2), ("Vase", 400, 110, 1.5), ("Tulip", 330, 70, 2.6), ("Goblet", 420, 95, 1.9), ("Trumpet", 380, 60, 2.9),
          ("Bell", 340, 120, 1.4), ("Flask", 300, 130, 1.7), ("Horn", 410, 75, 2.4), ("Chalice", 330, 100, 2.0), ("Urn", 390, 115, 1.6),
          ("Cup", 310, 90, 1.8), ("Jar", 350, 125, 1.3), ("Cone", 430, 55, 3.0), ("Bowl", 440, 130, 1.2), ("Lantern", 320, 85, 2.3), ("Pitcher", 370, 105, 1.7)]
SEQS = [[1, 2, 5, 10, 15, 20, 30, 50, 100], [2, 4, 8, 15, 25, 40, 70, 120, 200], [1, 3, 6, 12, 24, 48, 96], [1, 5, 10, 25, 50, 100, 150],
        [3, 6, 12, 20, 35, 60, 100, 160], [1, 2, 4, 8, 16, 32, 64, 128], [1, 2, 3, 5, 8, 13, 21, 34, 55, 89], [5, 10, 20, 40, 80, 160, 320],
        [1, 4, 9, 16, 25, 36, 49, 64, 81, 100], [2, 3, 5, 7, 11, 13, 17, 19, 23], [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], [1, 10, 50, 100, 200, 300]]
BGS = [(14, 14, 14), (8, 10, 22), (20, 8, 24), (6, 18, 22), (22, 12, 8), (10, 10, 30), (4, 20, 14), (24, 6, 12), (12, 12, 26), (18, 14, 6)]


def variant(rng, shape=None):
    name, wt, rb, p = next((s for s in SHAPES if s[0] == shape), None) or rng.choice(SHAPES)
    seq = rng.choice(SEQS)
    return dict(name=name, Wt=wt + rng.randint(-25, 25), rb=rb + rng.randint(-10, 10), p=round(p + rng.uniform(-0.25, 0.25), 2), counts=seq,
                target_len=rng.choice([60, 64, 68, 72, 76]), bg=rng.choice(BGS), hue0=round(rng.random(), 2), sat=rng.choice([0.65, 0.75, 0.85, 0.95]),
                title=f"{seq[0]} To {seq[-1]}")


def key(v):
    return f"{v['name']}:{v['Wt']}:{v['rb']}:{v['p']}:{v['counts'][0]}-{v['counts'][-1]}:{v['hue0']}"
