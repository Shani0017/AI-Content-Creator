"""ASMR batch H: PIANO BALLS - a melody played by falling balls.
Every note of the song is one ball. Each ball is dropped from the top at the exact moment (computed from gravity) that makes it
land on its key on the beat: real constant gravity, no slow motion, every landing plays its note. The tempo speeds up each pass."""
import math
from core import *

# ---- songs: list of (midi note, length in 1/16 steps). Add new songs here.
SONGS = {
    "Fur Elise": [(76, 1), (75, 1), (76, 1), (75, 1), (76, 1), (71, 1), (74, 1), (72, 1), (69, 2), (60, 1), (64, 1), (69, 1),
                  (71, 2), (64, 1), (68, 1), (71, 1), (72, 2), (64, 1), (76, 1), (75, 1),
                  (76, 1), (75, 1), (76, 1), (71, 1), (74, 1), (72, 1), (69, 2), (60, 1), (64, 1), (69, 1),
                  (71, 2), (64, 1), (72, 1), (71, 1), (69, 4)],
    "Ode To Joy": [(64, 2), (64, 2), (65, 2), (67, 2), (67, 2), (65, 2), (64, 2), (62, 2), (60, 2), (60, 2), (62, 2), (64, 2),
                   (64, 3), (62, 1), (62, 4),
                   (64, 2), (64, 2), (65, 2), (67, 2), (67, 2), (65, 2), (64, 2), (62, 2), (60, 2), (60, 2), (62, 2), (64, 2),
                   (62, 3), (60, 1), (60, 4)],
    "Twinkle Twinkle": [(60, 2), (60, 2), (67, 2), (67, 2), (69, 2), (69, 2), (67, 4), (65, 2), (65, 2), (64, 2), (64, 2),
                        (62, 2), (62, 2), (60, 4),
                        (67, 2), (67, 2), (65, 2), (65, 2), (64, 2), (64, 2), (62, 4), (67, 2), (67, 2), (65, 2), (65, 2),
                        (64, 2), (64, 2), (62, 4),
                        (60, 2), (60, 2), (67, 2), (67, 2), (69, 2), (69, 2), (67, 4), (65, 2), (65, 2), (64, 2), (64, 2),
                        (62, 2), (62, 2), (60, 4)],
}
WHITE = {0, 2, 4, 5, 7, 9, 11}


def clamp(x, a, b):
    return max(a, min(b, x))


def _h(notes):
    """lengths written in quarter=4 units -> engine steps (quarter=2)"""
    return [(m, n / 2) for m, n in notes]


# more public-domain songs (traditional / pre-1929)
SONGS["Jingle Bells"] = _h([(64, 4), (64, 4), (64, 8), (64, 4), (64, 4), (64, 8), (64, 4), (67, 4), (60, 6), (62, 2), (64, 16),
                            (65, 4), (65, 4), (65, 6), (65, 2), (65, 4), (64, 4), (64, 4), (64, 2), (64, 2),
                            (64, 4), (62, 4), (62, 4), (64, 4), (62, 8), (67, 8)])
SONGS["Happy Birthday"] = _h([(67, 3), (67, 1), (69, 4), (67, 4), (72, 4), (71, 8), (67, 3), (67, 1), (69, 4), (67, 4), (74, 4), (72, 8),
                              (67, 3), (67, 1), (79, 4), (76, 4), (72, 4), (71, 4), (69, 8), (77, 3), (77, 1), (76, 4), (72, 4), (74, 4), (72, 8)])
SONGS["Frere Jacques"] = _h([(60, 4), (62, 4), (64, 4), (60, 4)] * 2 + [(64, 4), (65, 4), (67, 8)] * 2 +
                            [(67, 2), (69, 2), (67, 2), (65, 2), (64, 4), (60, 4)] * 2 + [(60, 4), (55, 4), (60, 8)] * 2)
SONGS["Amazing Grace"] = _h([(62, 4), (67, 8), (71, 2), (67, 2), (71, 8), (69, 4), (67, 8), (64, 4), (62, 8), (62, 4), (67, 8), (71, 2), (67, 2),
                             (71, 8), (69, 4), (74, 12), (74, 12), (71, 4), (74, 4), (71, 4), (67, 4), (62, 4), (64, 4), (67, 12),
                             (62, 4), (67, 8), (71, 2), (67, 2), (71, 8), (69, 4), (67, 12)])
SONGS["Mary Had A Little Lamb"] = _h([(64, 4), (62, 4), (60, 4), (62, 4), (64, 4), (64, 4), (64, 8), (62, 4), (62, 4), (62, 8), (64, 4), (67, 4), (67, 8),
                                      (64, 4), (62, 4), (60, 4), (62, 4), (64, 4), (64, 4), (64, 4), (64, 4), (62, 4), (62, 4), (64, 4), (62, 4), (60, 16)])
SONGS["When The Saints"] = _h([(60, 4), (64, 4), (65, 4), (67, 12), (60, 4), (64, 4), (65, 4), (67, 12), (60, 4), (64, 4), (65, 4), (67, 8), (64, 8),
                               (60, 8), (64, 8), (62, 16), (64, 4), (64, 4), (62, 4), (60, 12), (60, 4), (64, 4), (67, 4), (67, 8), (65, 8), (64, 8), (62, 8), (60, 16)])


class PianoBalls(Sim):
    TITLE, SUB = "PIANO BALLS", "CAN YOU GUESS THE SONG?"
    T_END, SEED, SOUND, BASE_NOTE = 60, 3, "piano", 261.6
    BG = (10, 10, 18)
    ACC = (255, 214, 90)
    TS = False
    COUNTER = "MELODY"
    SONG = "Fur Elise"
    STEPS = [0.27, 0.23, 0.2, 0.175, 0.155, 0.14, 0.13]   # seconds per 1/16 step, per pass (speeds up)
    TARGET = 56.0                                          # keep adding passes until the melody is this long
    G = 2600.0                                             # px/s^2 constant gravity
    DROP_Y, KEY_TOP, KEY_H, R = 430.0, 1180.0, 430.0, 34.0

    def setup(self):
        mel = SONGS[self.SONG]
        # schedule: (landing time, midi)
        self.fall = math.sqrt(2 * (self.KEY_TOP - self.R - self.DROP_Y) / self.G)
        t = self.fall + 0.6
        self.sched = []
        k = 0
        while True:
            dt = self.STEPS[min(k, len(self.STEPS) - 1)]
            for m, n in mel:
                self.sched.append([t, m, False])
                t += n * dt
            k += 1
            if t > self.TARGET:
                break
        self.total = len(self.sched)
        self.played = 0
        # keyboard layout from the song's range
        lo = min(m for m, _ in mel)
        hi = max(m for m, _ in mel)
        while lo % 12 not in WHITE:
            lo -= 1
        while hi % 12 not in WHITE:
            hi += 1
        self.lo, self.hi = lo, hi
        whites = [m for m in range(lo, hi + 1) if m % 12 in WHITE]
        self.kw = min(112.0, (W - 60.0) / len(whites))
        self.kx0 = (W - self.kw * len(whites)) / 2
        self.wx = {m: self.kx0 + i * self.kw for i, m in enumerate(whites)}
        self.bx = {}
        for m in range(lo, hi + 1):
            if m % 12 not in WHITE:
                self.bx[m] = self.wx[m - 1] + self.kw          # boundary between the two neighbouring white keys
        self.balls = []      # x, y, vx, vy, midi, state(0 falling,1 landed), t_land
        self.press = {}
        self.nxt = 0

    def key_cx(self, m):
        return self.wx[m] + self.kw / 2 if m in self.wx else self.bx[m]

    def physics(self, dt):
        # spawn each ball exactly 'fall' seconds before its landing time
        while self.nxt < self.total and self.sched[self.nxt][0] - self.fall <= self.t + 1e-9:
            t_land, m, _ = self.sched[self.nxt]
            self.balls.append([self.key_cx(m), self.DROP_Y, 0.0, 0.0, m, 0, 0.0, self.nxt])
            self.nxt += 1
        for b in self.balls:
            b[3] += self.G * dt
            b[1] += b[3] * dt
            if b[1] >= self.KEY_TOP - self.R and b[3] > 0:
                b[1] = self.KEY_TOP - self.R
                if b[5] == 0:
                    b[5] = 1
                    b[6] = self.t
                    self.sched[b[7]][2] = True
                    self.played += 1
                    self.ev("note", b[4])
                    self.press[b[4]] = self.t
                    self.burst(b[0], self.KEY_TOP - 6, hsv(b[4] / 12.0), 6, 220, 0.4)
                b[3] = -b[3] * 0.32
                if abs(b[3]) < 60:
                    b[3] = 0.0
        self.balls = [b for b in self.balls if not (b[5] == 1 and self.t - b[6] > 0.9)]
        self.p = min(1.0, self.played / self.total) if self.total else 0.0

    def audit_missed(self):
        return sum(1 for t, m, ok in self.sched if not ok and t + 0.15 < self.t)

    def leftovers(self):
        return 0

    def draw(self, d):
        top, kh, kw = self.KEY_TOP, self.KEY_H, self.kw
        for m, x in self.wx.items():
            age = self.t - self.press.get(m, -9)
            lit = age < 0.35
            dy = 8 if age < 0.12 else 0
            col = tuple(int(255 - (255 - c) * 0.55 * (1 - age / 0.35)) for c in hsv(m / 12.0)) if lit else (246, 246, 250)
            d.rectangle((x + 2, top + dy, x + kw - 2, top + kh), fill=col, outline=(40, 40, 52), width=3)
        for m, cx in self.bx.items():
            age = self.t - self.press.get(m, -9)
            lit = age < 0.35
            col = tuple(int(c * (0.5 + 0.5 * (1 - age / 0.35))) for c in hsv(m / 12.0, .8, .9)) if lit else (24, 24, 32)
            d.rectangle((cx - kw * 0.3, top, cx + kw * 0.3, top + kh * 0.62), fill=col, outline=(0, 0, 0), width=3)
        # falling guide: faint lane lines under each upcoming ball
        for b in self.balls:
            if b[5] == 0:
                d.line((b[0], b[1] + self.R, b[0], top), fill=(60, 64, 90), width=3)
        for b in self.balls:
            col = hsv(b[4] / 12.0)
            a = 1.0 if b[5] == 0 else max(0.0, 1 - (self.t - b[6]) / 0.9)
            c = tuple(int(v * (0.25 + 0.75 * a)) for v in col)
            d.ellipse((b[0] - self.R, b[1] - self.R, b[0] + self.R, b[1] + self.R), fill=c, outline=(255, 255, 255), width=3)

    def hud(self, d):
        super().hud(d)
        if self.done_at is not None:
            ctext(d, "SONG: " + self.SONG.upper(), 980, font(76), (255, 255, 255))


def song(name, seed=3):
    return type("PianoBalls_" + name.replace(" ", ""), (PianoBalls,), {"SONG": name, "SEED": seed})


BATCH_H = [song(n) for n in SONGS]


class PadBalls(PianoBalls):
    """Same melody engine, different look: no keyboard. Balls drop onto glowing pads scattered across the screen
    (one pad per pitch, staggered heights). Each landing lights the pad, sends out a ripple and plays the note."""
    TITLE, SUB = "GUESS THE SONG", "EVERY BOUNCE IS A NOTE"
    BG = (8, 8, 20)
    PAD_W, PAD_H = 130.0, 26.0
    R = 38.0

    def setup(self):
        mel = SONGS[self.SONG]
        notes = sorted({m for m, _ in mel})
        n = len(notes)
        self.px = {}
        self.py = {}
        sp = (W - 260.0) / max(1, n - 1) if n > 1 else 0
        sp = min(sp, 230.0)
        self.PAD_W = min(130.0, sp * 0.8) if n > 1 else 130.0
        x0 = (W - sp * (n - 1)) / 2
        for i, m in enumerate(notes):
            self.px[m] = x0 + i * sp
            self.py[m] = 760.0 + ((i * 5) % 7) * 142.0
        t = self.fall_time(notes[0]) + 0.6
        self.sched = []
        k = 0
        while True:
            dt = self.STEPS[min(k, len(self.STEPS) - 1)]
            for m, ln in mel:
                self.sched.append([t, m, False, False])        # land time, midi, played, spawned
                t += ln * dt
            k += 1
            if t > self.TARGET:
                break
        self.total = len(self.sched)
        self.played = 0
        self.balls = []
        self.press = {}
        self.rip = []        # x, y, t0, color

    def fall_time(self, m):
        return math.sqrt(2 * (self.py[m] - self.R - self.DROP_Y) / self.G)

    def physics(self, dt):
        for i, s in enumerate(self.sched):
            if not s[3] and s[0] - self.fall_time(s[1]) <= self.t + 1e-9:
                s[3] = True
                self.balls.append([self.px[s[1]], self.DROP_Y, 0.0, 0.0, s[1], 0, 0.0, i])
        for b in self.balls:
            b[3] += self.G * dt
            b[1] += b[3] * dt
            top = self.py[b[4]] - self.R
            if b[5] == 0 and b[1] >= top:
                b[1], b[5], b[6] = top, 1, self.t
                self.sched[b[7]][2] = True
                self.played += 1
                self.ev("note", b[4])
                self.press[b[4]] = self.t
                col = hsv(b[4] / 12.0)
                self.rip.append((b[0], self.py[b[4]], self.t, col))
                self.burst(b[0], self.py[b[4]] - 4, col, 7, 240, 0.45)
                b[3] = -420.0                                   # hop off the pad, then fade
            elif b[5] == 1:
                b[1] = min(b[1], top)
        self.balls = [b for b in self.balls if not (b[5] == 1 and self.t - b[6] > 0.55)]
        self.rip = [r for r in self.rip if self.t - r[2] < 0.7]
        self.p = min(1.0, self.played / self.total) if self.total else 0.0

    def audit_missed(self):
        return sum(1 for s in self.sched if not s[2] and s[0] + 0.15 < self.t)

    def draw(self, d):
        for (x, y, t0, col) in self.rip:
            a = (self.t - t0) / 0.7
            gr = 120 + 260 * a
            d.ellipse((x - gr, y - gr, x + gr, y + gr), fill=tuple(int(v * 0.10 * (1 - a)) + self.BG[i] for i, v in enumerate(col)))
            r = 40 + 190 * a
            c = tuple(int(v * (1 - a) * 0.8) for v in col)
            d.ellipse((x - r, y - r * 0.35, x + r, y + r * 0.35), outline=c, width=4)
        for m, x in self.px.items():
            y = self.py[m]
            age = self.t - self.press.get(m, -9)
            lit = max(0.0, 1 - age / 0.4)
            col = hsv(m / 12.0)
            base = tuple(int(v * (0.28 + 0.72 * lit)) for v in col)
            dy = 6 * lit
            if lit > 0:
                g = tuple(int(v * 0.35 * lit) for v in col)
                d.rounded_rectangle((x - self.PAD_W / 2 - 14, y - 12 + dy, x + self.PAD_W / 2 + 14, y + self.PAD_H + 10 + dy), radius=18, fill=g)
            d.rounded_rectangle((x - self.PAD_W / 2, y + dy, x + self.PAD_W / 2, y + self.PAD_H + dy), radius=10, fill=base, outline=(255, 255, 255) if lit > 0.3 else None, width=3)
        for b in self.balls:
            col = hsv(b[4] / 12.0)
            a = 1.0 if b[5] == 0 else max(0.0, 1 - (self.t - b[6]) / 0.55)
            c = tuple(int(v * (0.3 + 0.7 * a)) for v in col)
            if b[5] == 0:
                for k in range(1, 6):                                   # fading trail
                    tr = self.R * (1 - k * 0.14)
                    ty = b[1] - k * 34
                    d.ellipse((b[0] - tr, ty - tr, b[0] + tr, ty + tr), fill=tuple(int(v * (0.30 - k * 0.05)) for v in col))
            d.ellipse((b[0] - self.R, b[1] - self.R, b[0] + self.R, b[1] + self.R), fill=c, outline=(255, 255, 255), width=3)

    def hud(self, d):
        super().hud(d)


def pads(name, seed=3):
    return type("PadBalls_" + name.replace(" ", ""), (PadBalls,), {"SONG": name, "SEED": seed})


class BrickRain(PianoBalls):
    """Towers of bricks (one tower per pitch, as tall as that pitch is played). Every ball falls on the top brick of its tower and
    smashes it - the crash is the beat, the melody plays softly underneath. Every note = one ball = one brick; the last ball clears the last brick."""
    TITLE, SUB = "BRICK RAIN", "EVERY BALL BREAKS A BRICK"
    COUNTER = "BRICKS BROKEN"
    BG = (14, 10, 24)
    NOTE_VOL = 0.8
    CRACK_VOL = 0.22
    FLOOR = 1640.0

    def setup(self):
        mel = SONGS[self.SONG]
        t = 1.7
        seq = []
        k = 0
        while True:
            dt = self.STEPS[min(k, len(self.STEPS) - 1)]
            for m, ln in mel:
                seq.append([t, m])
                t += ln * dt
            k += 1
            if t > self.TARGET:
                break
        notes = sorted({m for _, m in seq})
        n = len(notes)
        cnt = {m: sum(1 for _, x in seq if x == m) for m in notes}
        self.bh = max(14.0, min(34.0, 930.0 / max(cnt.values())))
        sp = (W - 110.0) / n
        self.bw = min(150.0, sp - 8)
        self.cx = {m: 55 + sp * (i + 0.5) for i, m in enumerate(notes)}
        self.hue = {m: i / n for i, m in enumerate(notes)}
        self.rem = dict(cnt)
        self.cnt = dict(cnt)
        run = dict(cnt)
        self.sched = []
        for tl, m in seq:                                              # per-ball fall time from the tower height at the moment it lands
            top = self.FLOOR - run[m] * self.bh
            fall = math.sqrt(2 * (top - self.R - self.DROP_Y) / self.G)
            run[m] -= 1
            self.sched.append([tl, m, False, False, fall])
        self.total = len(self.sched)
        self.played = 0
        self.balls = []
        self.chips = []
        self.press = {}
        self.nxt = 0

    def physics(self, dt):
        for i, s in enumerate(self.sched):
            if not s[3] and s[0] - s[4] <= self.t + 1e-9:
                s[3] = True
                self.balls.append([self.cx[s[1]], self.DROP_Y, 0.0, 0.0, s[1], 0, 0.0, i])
        keep = []
        for b in self.balls:
            b[3] += self.G * dt
            b[1] += b[3] * dt
            top = self.FLOOR - self.rem[b[4]] * self.bh
            if b[1] + self.R >= top and self.rem[b[4]] > 0:
                self.sched[b[7]][2] = True
                self.rem[b[4]] -= 1
                self.played += 1
                self.ev("note", b[4])
                self.ev("crack", self.rng.random())
                col = hsv(self.hue[b[4]])
                for _ in range(9):
                    self.chips.append([b[0] + self.rng.uniform(-self.bw / 2, self.bw / 2), top + self.bh / 2, self.rng.uniform(-330, 330),
                                       self.rng.uniform(-620, -150), col, self.rng.uniform(7, 15), self.t])
                self.burst(b[0], top, (255, 240, 200), 6, 260, 0.35)
                self.press[b[4]] = self.t
                continue
            keep.append(b)
        self.balls = keep
        for c in self.chips:
            c[3] += 2300 * dt
            c[0] += c[2] * dt
            c[1] += c[3] * dt
        self.chips = [c for c in self.chips if self.t - c[6] < 0.9]
        self.p = min(1.0, self.played / self.total) if self.total else 0.0

    def leftovers(self):
        return sum(self.rem.values())

    def audit_missed(self):
        return sum(1 for s in self.sched if not s[2] and s[0] + 0.15 < self.t)

    def draw(self, d):
        d.rectangle((40, self.FLOOR, W - 40, self.FLOOR + 16), fill=(70, 66, 92))
        for m, x in self.cx.items():
            hue = self.hue[m]
            flash = max(0.0, 1 - (self.t - self.press.get(m, -9)) / 0.18)
            for r in range(self.rem[m]):
                y = self.FLOOR - (r + 1) * self.bh
                base = hsv(hue, 0.75, 0.62 + 0.18 * (r % 2))
                top = r == self.rem[m] - 1
                if top and flash > 0:
                    base = tuple(min(255, int(v + 140 * flash)) for v in base)
                d.rectangle((x - self.bw / 2, y, x + self.bw / 2, y + self.bh - 2), fill=base, outline=(20, 14, 30), width=2)
        for c in self.chips:
            a = 1 - (self.t - c[6]) / 0.9
            col = tuple(int(v * a) for v in c[4])
            d.rectangle((c[0] - c[5] / 2, c[1] - c[5] / 2, c[0] + c[5] / 2, c[1] + c[5] / 2), fill=col)
        for b in self.balls:
            col = hsv(self.hue[b[4]])
            for k in range(1, 5):
                tr = self.R * (1 - k * 0.15)
                ty = b[1] - k * 30
                d.ellipse((b[0] - tr, ty - tr, b[0] + tr, ty + tr), fill=tuple(int(v * (0.30 - k * 0.05)) for v in col))
            d.ellipse((b[0] - self.R, b[1] - self.R, b[0] + self.R, b[1] + self.R), fill=col, outline=(255, 255, 255), width=3)


def bricks(name, seed=3):
    return type("BrickRain_" + name.replace(" ", ""), (BrickRain,), {"SONG": name, "SEED": seed})


class XyloDrop(PadBalls):
    """A wooden xylophone: coloured bars (long = low note, short = high note) on two rails. Balls drop onto the top end of their bar,
    the bar dips and rings, and the ball bounces away. One ball per note, landing exactly on the beat."""
    TITLE, SUB = "XYLOPHONE DROP", "BALLS BOUNCE OUT A MELODY"
    BG = (16, 12, 26)
    NOTE_SYNTH = "xylo"
    NOTE_VOL = 1.0
    YC = 1180.0

    def setup(self):
        mel = SONGS[self.SONG]
        notes = sorted({m for m, _ in mel})
        n = len(notes)
        sp = (W - 110.0) / n
        self.bw = min(124.0, sp - 10)
        self.px, self.py, self.bl = {}, {}, {}
        for i, m in enumerate(notes):
            L = 600.0 - (330.0 * i / (n - 1) if n > 1 else 0)         # low = long bar
            self.px[m] = 55 + sp * (i + 0.5)
            self.bl[m] = L
            self.py[m] = self.YC - L / 2                              # top end of the bar
        self.hue = {m: i / n for i, m in enumerate(notes)}
        t = self.fall_time(notes[0]) + 0.6
        self.sched = []
        k = 0
        while True:
            dt = self.STEPS[min(k, len(self.STEPS) - 1)]
            for m, ln in mel:
                self.sched.append([t, m, False, False])
                t += ln * dt
            k += 1
            if t > self.TARGET:
                break
        self.total = len(self.sched)
        self.played = 0
        self.balls = []
        self.press = {}
        self.rip = []

    def physics(self, dt):
        for i, s in enumerate(self.sched):
            if not s[3] and s[0] - self.fall_time(s[1]) <= self.t + 1e-9:
                s[3] = True
                self.balls.append([self.px[s[1]], self.DROP_Y, 0.0, 0.0, s[1], 0, 0.0, i])
        for b in self.balls:
            b[3] += self.G * dt
            b[1] += b[3] * dt
            b[0] += b[2] * dt
            top = self.py[b[4]] - self.R
            if b[5] == 0 and b[1] >= top:
                b[1], b[5], b[6] = top, 1, self.t
                self.sched[b[7]][2] = True
                self.played += 1
                self.ev("note", b[4])
                self.press[b[4]] = self.t
                col = hsv(self.hue[b[4]])
                self.burst(b[0], self.py[b[4]] - 6, col, 6, 220, 0.4)
                b[3] = -b[3] * 0.34                              # bounce away, sideways
                b[2] = self.rng.choice((-1, 1)) * self.rng.uniform(130, 240)
        self.balls = [b for b in self.balls if not (b[5] == 1 and self.t - b[6] > 0.5)]
        self.p = min(1.0, self.played / self.total) if self.total else 0.0

    def draw(self, d):
        yc = self.YC
        xs = list(self.px.values())
        for ry in (yc - 175, yc + 175):                          # the two rails the bars rest on
            d.rounded_rectangle((min(xs) - 90, ry - 16, max(xs) + 90, ry + 16), radius=14, fill=(92, 58, 34), outline=(40, 24, 14), width=3)
        for m, x in self.px.items():
            L, hue = self.bl[m], self.hue[m]
            age = self.t - self.press.get(m, -9)
            lit = max(0.0, 1 - age / 0.45)
            dip = 9 * lit * math.cos(age * 55)
            base = hsv(hue, 0.78, 0.78 + 0.22 * lit)
            top = yc - L / 2 + dip
            d.rounded_rectangle((x - self.bw / 2, top, x + self.bw / 2, yc + L / 2 + dip), radius=16, fill=base, outline=(255, 255, 255) if lit > 0.3 else (28, 18, 36), width=4)
            d.rounded_rectangle((x - self.bw / 2 + 12, top + 12, x - self.bw / 2 + 24, yc + L / 2 - 12 + dip), radius=6, fill=tuple(min(255, v + 70) for v in base))
            for ry in (yc - 175, yc + 175):                      # rubber mounts
                d.ellipse((x - 9, ry - 9, x + 9, ry + 9), fill=(30, 20, 30))
        for b in self.balls:
            col = hsv(self.hue[b[4]])
            a = 1.0 if b[5] == 0 else max(0.0, 1 - (self.t - b[6]) / 0.5)
            r = self.R * (0.4 + 0.6 * a)
            if b[5] == 0:
                for k in range(1, 5):
                    tr = self.R * (1 - k * 0.15)
                    ty = b[1] - k * 30
                    d.ellipse((b[0] - tr, ty - tr, b[0] + tr, ty + tr), fill=tuple(int(v * (0.30 - k * 0.05)) for v in col))
            d.ellipse((b[0] - r, b[1] - r, b[0] + r, b[1] + r), fill=tuple(int(v * (0.3 + 0.7 * a)) for v in col), outline=(255, 255, 255), width=3)


def xylo(name, seed=3):
    return type("XyloDrop_" + name.replace(" ", ""), (XyloDrop,), {"SONG": name, "SEED": seed})
