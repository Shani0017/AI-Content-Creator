"""ASMR batch I: melody-ball videos with many looks. Builds on sims_h (XyloDrop, BrickRain, PadBalls) and adds glass bowls, bell tower and drums,
plus a theme layer (palette, background, ball shape, decoration) so every video looks different. Songs are public-domain / traditional only."""
import math, random
import sims_h
from sims_h import *   # noqa: F401,F403
from core import W, H

_h = sims_h._h
SONGS.update({
    "Row Row Row Your Boat": _h([(60, 4), (60, 4), (60, 3), (62, 1), (64, 4), (64, 3), (62, 1), (64, 3), (65, 1), (67, 8),
                                 (72, 4 / 3), (72, 4 / 3), (72, 4 / 3), (67, 4 / 3), (67, 4 / 3), (67, 4 / 3), (64, 4 / 3), (64, 4 / 3), (64, 4 / 3),
                                 (60, 4 / 3), (60, 4 / 3), (60, 4 / 3), (67, 3), (65, 1), (64, 3), (62, 1), (60, 8)]),
    "London Bridge": _h([(67, 3), (69, 1), (67, 2), (65, 2), (64, 2), (65, 2), (67, 4), (62, 4), (64, 4), (65, 8), (64, 4), (65, 4), (67, 8),
                         (67, 3), (69, 1), (67, 2), (65, 2), (64, 2), (65, 2), (67, 4), (62, 4), (67, 4), (64, 4), (60, 8)]),
    "Old MacDonald": _h([(60, 4), (60, 4), (60, 4), (55, 4), (57, 4), (57, 4), (55, 8), (64, 4), (64, 4), (62, 4), (62, 4), (60, 8)] * 2),
    "Hot Cross Buns": _h([(64, 4), (62, 4), (60, 8), (64, 4), (62, 4), (60, 8), (60, 2), (60, 2), (60, 2), (60, 2), (62, 2), (62, 2), (62, 2), (62, 2),
                          (64, 4), (62, 4), (60, 8)]),
    "Yankee Doodle": _h([(60, 2), (60, 2), (62, 2), (64, 2), (60, 2), (64, 2), (62, 4), (55, 2), (60, 2), (60, 2), (62, 2), (64, 2), (60, 4), (59, 4),
                         (60, 2), (60, 2), (62, 2), (64, 2), (65, 2), (64, 2), (62, 2), (60, 2), (59, 2), (55, 2), (57, 2), (59, 2), (60, 4), (60, 4)]),
    "Oh Susanna": _h([(60, 2), (62, 2), (64, 4), (67, 6), (67, 2), (69, 2), (67, 2), (64, 4), (60, 4), (62, 2), (64, 2), (64, 4), (62, 4), (60, 2), (62, 2), (60, 8)]),
    "Silent Night": _h([(67, 3), (69, 1), (67, 2), (64, 6), (67, 3), (69, 1), (67, 2), (64, 6), (74, 4), (74, 2), (71, 6), (72, 4), (72, 2), (67, 6),
                        (69, 4), (69, 2), (72, 3), (71, 1), (69, 2), (67, 3), (69, 1), (67, 2), (64, 6), (69, 4), (69, 2), (72, 3), (71, 1), (69, 2),
                        (67, 3), (69, 1), (67, 2), (64, 6), (74, 4), (74, 2), (77, 3), (74, 1), (71, 2), (72, 6), (76, 6), (72, 2), (67, 2), (64, 2), (67, 3), (65, 1), (62, 2), (60, 12)]),
    "Joy To The World": _h([(72, 4), (71, 3), (69, 1), (67, 6), (65, 2), (64, 4), (62, 4), (60, 8), (67, 4), (69, 6), (69, 2), (71, 6), (71, 2), (72, 12)]),
    "Auld Lang Syne": _h([(60, 4), (65, 6), (65, 2), (65, 4), (69, 4), (67, 6), (65, 2), (67, 4), (69, 2), (67, 2), (65, 6), (65, 2), (69, 4), (72, 4), (74, 12),
                          (74, 4), (72, 6), (69, 2), (69, 4), (65, 4), (67, 6), (65, 2), (67, 4), (69, 2), (67, 2), (65, 6), (62, 2), (62, 4), (60, 4), (65, 12)]),
    "Greensleeves": _h([(69, 2), (72, 4), (74, 2), (76, 3), (77, 1), (76, 2), (74, 4), (71, 2), (67, 3), (69, 1), (71, 2), (72, 4), (69, 2), (69, 3), (68, 1), (69, 2),
                        (71, 4), (68, 2), (64, 4), (69, 2), (72, 4), (74, 2), (76, 3), (77, 1), (76, 2), (74, 4), (71, 2), (67, 3), (69, 1), (71, 2), (72, 3), (71, 1),
                        (69, 2), (68, 3), (66, 1), (68, 2), (69, 6)]),
    "Brahms Lullaby": _h([(64, 2), (64, 2), (67, 4), (64, 2), (64, 2), (67, 4), (64, 2), (67, 2), (72, 4), (71, 4), (69, 4), (69, 4), (67, 8),
                          (62, 2), (64, 2), (65, 4), (62, 2), (64, 2), (65, 4), (62, 2), (65, 2), (71, 4), (69, 4), (67, 4), (71, 4), (72, 8)]),
    "Eine Kleine Nachtmusik": _h([(67, 3), (62, 1), (67, 2), (62, 2), (67, 1), (62, 1), (67, 1), (71, 1), (74, 6), (72, 3), (69, 1), (72, 2), (69, 2),
                                  (72, 1), (69, 1), (66, 1), (69, 1), (62, 6)]),
    "Canon In D": _h([(78, 8), (76, 8), (74, 8), (73, 8), (71, 8), (69, 8), (71, 8), (73, 8), (74, 4), (78, 4), (81, 4), (79, 4), (78, 4), (76, 4), (78, 4), (73, 4)]),
    "Deck The Halls": _h([(72, 6), (71, 2), (69, 4), (67, 4), (65, 4), (67, 4), (69, 4), (65, 4), (67, 2), (69, 2), (71, 2), (67, 2), (69, 6), (67, 2),
                          (65, 4), (64, 4), (62, 4), (64, 8)]),
})

# ---------------------------------------------------------------- theme layer
_THEME = {"hue": 0.0, "sat": 1.0, "shape": "circle", "deco": "none", "seed": 0}
_core_hsv = sims_h.hsv


def hsv(h, s=0.8, v=1.0):
    return _core_hsv(h + _THEME["hue"], min(1.0, s * _THEME["sat"]), v)


sims_h.hsv = hsv          # the scenes in sims_h look up hsv in their own module, so they pick up the theme hue shift


def _ball(d, x, y, r, fill, outline=(255, 255, 255), width=3):
    sh = _THEME["shape"]
    if sh == "circle":
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=width)
    elif sh == "square":
        d.rounded_rectangle((x - r, y - r, x + r, y + r), radius=r * 0.3, fill=fill, outline=outline, width=width)
    elif sh == "diamond":
        d.polygon([(x, y - r * 1.25), (x + r * 1.05, y), (x, y + r * 1.25), (x - r * 1.05, y)], fill=fill, outline=outline, width=width)
    elif sh == "hex":
        d.polygon([(x + r * math.cos(math.pi / 3 * k + 0.5), y + r * math.sin(math.pi / 3 * k + 0.5)) for k in range(6)], fill=fill, outline=outline, width=width)
    else:  # star
        pts = []
        for k in range(10):
            rr = r * (1.25 if k % 2 == 0 else 0.55)
            a = math.pi / 5 * k - math.pi / 2
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, fill=fill, outline=outline, width=width)


def _deco(sim, d):
    kind = _THEME["deco"]
    rg = random.Random(_THEME["seed"])
    lift = lambda k: tuple(min(255, int(c + k)) for c in sim.BG)
    if kind == "orbs":
        for _ in range(7):
            x, y, r = rg.uniform(0, W), rg.uniform(300, 1650), rg.uniform(120, 340)
            d.ellipse((x - r, y - r, x + r, y + r), fill=lift(7))
    elif kind == "stripes":
        for i in range(-3, 14):
            x = i * 130 + 40
            d.polygon([(x, 300), (x + 60, 300), (x + 60 - 420, 1700), (x - 420, 1700)], fill=lift(5))
    elif kind == "grid":
        for x in range(0, W, 90):
            d.line((x, 300, x, 1700), fill=lift(8), width=2)
        for y in range(300, 1700, 90):
            d.line((0, y, W, y), fill=lift(8), width=2)
    elif kind == "rings":
        for r in range(160, 1000, 150):
            d.ellipse((W / 2 - r, 1000 - r, W / 2 + r, 1000 + r), outline=lift(10), width=3)


def _hue_of(self, m):
    return self.hue[m] if hasattr(self, "hue") else m / 12.0


def _draw_balls_generic(self, d):
    for b in self.balls:
        col = hsv(_hue_of(self, b[4]))
        a = 1.0 if b[5] == 0 else max(0.0, 1 - (self.t - b[6]) / 0.5)
        r = self.R * (0.4 + 0.6 * a)
        if b[5] == 0:
            for k in range(1, 5):
                _ball(d, b[0], b[1] - k * 30, self.R * (1 - k * 0.15), tuple(int(v * (0.30 - k * 0.05)) for v in col), outline=None, width=0)
        _ball(d, b[0], b[1], r, tuple(int(v * (0.3 + 0.7 * a)) for v in col))


class _Themed:
    """mixin: decoration under the scene and themed balls on top (the scene's own ball pass is skipped)"""
    def draw(self, d):
        _deco(self, d)
        held = self.balls
        self.balls = []
        super().draw(d)
        self.balls = held
        _draw_balls_generic(self, d)


class GlassBowls(PadBalls):
    TITLE, SUB = "GLASS BOWL DROP", "EVERY BOUNCE RINGS A NOTE"
    NOTE_SYNTH, NOTE_VOL = "glass", 1.3

    def draw(self, d):
        _deco(self, d)
        for (x, y, t0, col) in self.rip:
            a = (self.t - t0) / 0.7
            r = 50 + 160 * a
            d.ellipse((x - r, y - r * 0.3, x + r, y + r * 0.3), outline=tuple(int(v * (1 - a) * 0.8) for v in col), width=4)
        for m, x in self.px.items():
            y = self.py[m]
            lit = max(0.0, 1 - (self.t - self.press.get(m, -9)) / 0.5)
            col = hsv(m / 12.0, 0.55, 0.9)
            body = tuple(int(v * (0.18 + 0.45 * lit)) for v in col)
            w = self.PAD_W / 2 + 6
            d.polygon([(x - w, y), (x + w, y), (x + w * 0.55, y + 78), (x - w * 0.55, y + 78)], fill=body, outline=tuple(int(v * (0.5 + 0.5 * lit)) for v in col))
            d.ellipse((x - w, y - 11, x + w, y + 11), outline=(235, 240, 255), width=3, fill=tuple(int(v * 0.25) for v in col))
            d.rectangle((x - 5, y + 78, x + 5, y + 112), fill=body)
            d.ellipse((x - w * 0.7, y + 108, x + w * 0.7, y + 124), fill=body)
        _draw_balls_generic(self, d)


class BellTower(PadBalls):
    TITLE, SUB = "BELL TOWER DROP", "BALLS RING OUT THE MELODY"
    NOTE_SYNTH, NOTE_VOL = "bell", 0.9

    def draw(self, d):
        _deco(self, d)
        for (x, y, t0, col) in self.rip:
            a = (self.t - t0) / 0.7
            r = 40 + 170 * a
            d.ellipse((x - r, y - r * 0.5, x + r, y + r * 0.5), outline=tuple(int(v * (1 - a) * 0.7) for v in col), width=3)
        for m, x in self.px.items():
            y = self.py[m]
            age = self.t - self.press.get(m, -9)
            lit = max(0.0, 1 - age / 0.5)
            sw = 26 * lit * math.sin(age * 22)
            col = hsv(m / 12.0, 0.7, 0.55 + 0.4 * lit)
            d.line((x, 320, x, y), fill=(70, 64, 92), width=3)
            w = self.PAD_W / 2
            d.polygon([(x - w * 0.55, y), (x + w * 0.55, y), (x + w * 0.62 + sw, y + 52), (x + w * 1.05 + sw, y + 92), (x - w * 1.05 + sw, y + 92), (x - w * 0.62 + sw, y + 52)],
                      fill=col, outline=(255, 255, 255) if lit > 0.3 else (30, 24, 40), width=3)
            d.ellipse((x - 10 + sw, y + 88, x + 10 + sw, y + 108), fill=(235, 210, 150))
        _draw_balls_generic(self, d)


class DrumRings(PadBalls):
    TITLE, SUB = "DRUM DROP", "BALLS BOUNCE OUT THE BEAT"
    NOTE_SYNTH, NOTE_VOL = "marimba", 1.4
    PAD_W = 150.0

    def draw(self, d):
        _deco(self, d)
        for (x, y, t0, col) in self.rip:
            a = (self.t - t0) / 0.7
            r = 60 + 190 * a
            d.ellipse((x - r, y - r * 0.28, x + r, y + r * 0.28), outline=tuple(int(v * (1 - a) * 0.8) for v in col), width=4)
        for m, x in self.px.items():
            y = self.py[m]
            lit = max(0.0, 1 - (self.t - self.press.get(m, -9)) / 0.4)
            col = hsv(m / 12.0, 0.8, 0.5 + 0.5 * lit)
            w = self.PAD_W / 2
            d.rectangle((x - w, y + 6, x + w, y + 46), fill=tuple(int(v * 0.55) for v in col))
            d.ellipse((x - w, y + 26, x + w, y + 66), fill=tuple(int(v * 0.55) for v in col))
            d.ellipse((x - w, y - 18 + 5 * lit, x + w, y + 26 + 5 * lit), fill=tuple(int(min(255, v + 90 * lit)) for v in col), outline=(240, 240, 250), width=4)
            d.ellipse((x - w * 0.55, y - 8 + 5 * lit, x + w * 0.55, y + 16 + 5 * lit), outline=(255, 255, 255), width=2)
        _draw_balls_generic(self, d)


CLASSES = {
    "xylo": (sims_h.XyloDrop, "Xylophone Drop - Balls Bounce Out {s}"),
    "brick": (sims_h.BrickRain, "Falling Balls Break Every Brick - Brick Rain {s}"),
    "pads": (sims_h.PadBalls, "Neon Pad Bounce - Balls Play {s}"),
    "glass": (GlassBowls, "Glass Bowl Drop - Falling Balls Ring Out {s}"),
    "bell": (BellTower, "Bell Tower Drop - Balls Ring Out {s}"),
    "drum": (DrumRings, "Drum Drop - Balls Bounce Out {s}"),
}
ORDER = ["xylo", "brick", "pads", "glass", "bell", "drum"]
BGS = [(16, 12, 26), (8, 14, 24), (22, 10, 14), (10, 20, 18), (24, 18, 8), (12, 8, 30), (18, 18, 22), (6, 6, 12), (26, 8, 26), (8, 22, 30), (20, 14, 10), (10, 12, 16)]
SHAPES = ["circle", "square", "diamond", "hex", "star"]
DECOS = ["none", "orbs", "stripes", "grid", "rings"]
SUFFIX = " - Satisfying ASMR #shorts"


def themed(kind, song, k):
    """video #k of the batch: a base scene plus its own palette / background / ball shape / decoration"""
    base, title = CLASSES[kind]
    rg = random.Random(k * 7919 + 13)
    th = {"hue": (k * 0.137 + rg.random() * 0.05) % 1.0, "sat": rg.choice((0.55, 0.8, 1.0, 1.2)), "shape": SHAPES[(k * 3 + k // 5) % 5],
          "deco": DECOS[(k * 2 + k // 7) % 5], "seed": k}
    attrs = {"SONG": song, "SEED": 3 + k % 5, "BG": BGS[(k * 5 + k // 12) % len(BGS)], "ACC": _core_hsv(th["hue"] + 0.12, 0.7, 1.0)}
    if base in (sims_h.XyloDrop, sims_h.BrickRain, sims_h.PadBalls):
        cls = type(f"T{k}_{kind}", (_Themed, base), attrs)
    else:
        cls = type(f"T{k}_{kind}", (base,), attrs)
    return cls, (title.format(s=song) + SUFFIX), th


def activate(th):
    _THEME.update(th)
