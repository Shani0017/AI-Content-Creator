"""Batch 2 - flows (7) and painters (5). Honest colliders (pegs, segments, moving pegs/bars), count-based progress."""
import math
from core import *
from eater import calib, clamp


# ================================================================== FLOW BASE
class Flow(Sim):
    TS = False
    SPAWN = 8.0
    TARGET = 900
    GRAV = 1300
    BR = 7
    REST = 0.55
    FRIC = 1.0
    JIT = 25.0
    SPX = (500, 580)
    SPY = 440
    CAPMAX = 420
    COLLECT_Y = 1440
    L, R = 60, 1020

    def __init__(self):
        c = type(self)
        self.K = calib(c.__name__, 1.0)
        self.SPAWN = c.SPAWN * self.K
        super().__init__()

    def setup(self):
        self.pegs = []          # [x, y, r, vx, vy]
        self.segs = []          # [x0, y0, x1, y1, w]
        self.balls = []         # [x, y, vx, vy, r, col, dead]
        self.acc = 0.0
        self.count = 0
        self.flash = {}
        self.build()
        # no peg may leave a gap to a side wall narrower than a ball (balls would wedge there)
        gap = 2 * self.BR + 6
        self.pegs = [p for p in self.pegs if (p[0] - p[2] - self.L) > gap and (self.R - p[0] - p[2]) > gap]
        self.hash_pegs()

    def build(self):
        pass

    def hash_pegs(self):
        self.ph = {}
        for p in self.pegs:
            for cx in range(int((p[0] - p[2]) // 40), int((p[0] + p[2]) // 40) + 1):
                for cy in range(int((p[1] - p[2]) // 40), int((p[1] + p[2]) // 40) + 1):
                    self.ph.setdefault((cx, cy), []).append(p)

    def ball_col(self):
        return (255, 255, 255)

    def spawn(self, dt):
        self.acc += self.SPAWN * dt
        while self.acc >= 1:
            self.acc -= 1
            if len(self.balls) < self.CAPMAX and self.count + len(self.balls) < self.TARGET:
                self.balls.append([self.rng.uniform(*self.SPX), self.SPY, self.rng.uniform(-30, 30), 0.0, self.BR, self.ball_col(), False])

    def collide_point(self, b, cx, cy, rad, svx=0.0, svy=0.0):
        dx, dy = b[0] - cx, b[1] - cy
        d2 = dx * dx + dy * dy
        rr = rad + b[4]
        if d2 >= rr * rr:
            return False
        d = math.sqrt(d2) or 0.01
        nx, ny = dx / d, dy / d
        rvx, rvy = b[2] - svx, b[3] - svy
        vn = rvx * nx + rvy * ny
        if vn < 0:
            rvx -= (1 + self.REST) * vn * nx
            rvy -= (1 + self.REST) * vn * ny
            if self.FRIC < 1.0:
                vt = rvx * -ny + rvy * nx
                rvx -= -ny * vt * (1 - self.FRIC)
                rvy -= nx * vt * (1 - self.FRIC)
            jit = self.rng.uniform(-self.JIT, self.JIT)
            rvx += -ny * jit
            rvy += nx * jit
            b[2], b[3] = rvx + svx, rvy + svy
            if -vn > 160:
                self.on_hit(b, cx, cy, -vn)
        b[0], b[1] = cx + nx * (rr + 0.2), cy + ny * (rr + 0.2)
        return True

    def collide_seg(self, b, s, svx=0.0, svy=0.0, pivot=None, omega=0.0):
        x0, y0, x1, y1, w = s[:5]
        ex, ey = x1 - x0, y1 - y0
        L2 = ex * ex + ey * ey
        u = clamp(((b[0] - x0) * ex + (b[1] - y0) * ey) / L2, 0, 1)
        px, py = x0 + u * ex, y0 + u * ey
        if pivot is not None:
            svx, svy = -omega * (py - pivot[1]), omega * (px - pivot[0])
        return self.collide_point(b, px, py, w / 2, svx, svy)

    def on_hit(self, b, x, y, speed):
        self.ev("hit", clamp((x - self.L) / (self.R - self.L), 0, 1))

    def moving(self, dt):
        pass

    def physics(self, dt):
        self.moving(dt)
        self.spawn(dt)
        for b in self.balls:
            b[3] += self.GRAV * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            for cx in range(int((b[0] - 20) // 40), int((b[0] + 20) // 40) + 1):
                for cy in range(int((b[1] - 20) // 40), int((b[1] + 20) // 40) + 1):
                    for p in self.ph.get((cx, cy), ()):
                        self.collide_point(b, p[0], p[1], p[2], p[3], p[4])
            for s in self.segs:
                self.collide_seg(b, s)
            self.collide_extra(b)
            if b[0] < self.L + b[4]:
                b[0], b[2] = self.L + b[4], abs(b[2]) * 0.6
            elif b[0] > self.R - b[4]:
                b[0], b[2] = self.R - b[4], -abs(b[2]) * 0.6
            sp = math.hypot(b[2], b[3])
            if sp > 2200:
                b[2], b[3] = b[2] * 2200 / sp, b[3] * 2200 / sp
            if self.reached(b):
                b[6] = True
                self.collect(b)
        self.balls = [b for b in self.balls if not b[6]]
        self.p = min(1.0, self.count / self.TARGET)

    def collide_extra(self, b):
        pass

    def reached(self, b):
        return b[1] > self.COLLECT_Y

    def collect(self, b):
        self.count += 1

    def audit_missed(self):
        n = 0
        for b in self.balls:
            for p in self.pegs:
                if (b[0] - p[0]) ** 2 + (b[1] - p[1]) ** 2 < (p[2] + b[4] - 1.5) ** 2:
                    n += 1
        return n

    def leftovers(self):
        return 0 if self.count >= self.TARGET else self.TARGET - self.count

    def draw_balls(self, d):
        for b in self.balls:
            d.ellipse((b[0] - b[4], b[1] - b[4], b[0] + b[4], b[1] + b[4]), fill=b[5])

    def draw_pegs(self, d, col=(90, 140, 190)):
        for p in self.pegs:
            d.ellipse((p[0] - p[2], p[1] - p[2], p[0] + p[2], p[1] + p[2]), fill=col)

    def draw_segs(self, d, col=(120, 150, 200)):
        for s in self.segs:
            d.line((s[0], s[1], s[2], s[3]), fill=col, width=int(s[4]))
            for (x, y) in ((s[0], s[1]), (s[2], s[3])):
                d.ellipse((x - s[4] / 2, y - s[4] / 2, x + s[4] / 2, y + s[4] / 2), fill=col)


class BinsMixin:
    """bins below COLLECT_Y that stack collected balls as dots"""
    NBINS = 8
    BIN_TOP, BIN_BOT = 1450, 1650
    DOT = 8

    def init_bins(self):
        self.bins = [0] * self.NBINS
        self.bw = (self.R - self.L) / self.NBINS

    def reached(self, b):
        if b[1] < self.BIN_TOP - 10:
            return False
        i = int(clamp((b[0] - self.L) // self.bw, 0, self.NBINS - 1))
        per_row = max(1, int((self.bw - 6) // self.DOT))
        rows = min(self.bins[i] // per_row, int((self.BIN_BOT - self.BIN_TOP) // self.DOT))
        return b[1] + b[4] >= self.BIN_BOT - rows * self.DOT - 2

    def collect(self, b):
        i = int(clamp((b[0] - self.L) // self.bw, 0, self.NBINS - 1))
        self.bins[i] += 1
        self.count += 1
        self.ev("special", i / self.NBINS)

    def draw_bins(self, d, hue0=0.5, hue1=0.9):
        per_row = max(1, int((self.bw - 6) // self.DOT))
        cap_rows = int((self.BIN_BOT - self.BIN_TOP) // self.DOT)
        for i, n in enumerate(self.bins):
            x0 = self.L + i * self.bw
            d.line((x0, self.BIN_TOP - 20, x0, self.BIN_BOT), fill=(70, 80, 110), width=3)
            shown = min(n, per_row * cap_rows)
            col = hsv(hue0 + (hue1 - hue0) * i / max(1, self.NBINS - 1), 0.7, 1.0)
            for k in range(shown):
                rr, cc = divmod(k, per_row)
                x = x0 + 3 + cc * self.DOT + self.DOT / 2
                y = self.BIN_BOT - rr * self.DOT - self.DOT / 2
                d.ellipse((x - self.DOT / 2 + 0.5, y - self.DOT / 2 + 0.5, x + self.DOT / 2 - 0.5, y + self.DOT / 2 - 0.5), fill=col)
        d.line((self.R, self.BIN_TOP - 20, self.R, self.BIN_BOT), fill=(70, 80, 110), width=3)
        d.line((self.L, self.BIN_BOT + 2, self.R, self.BIN_BOT + 2), fill=(70, 80, 110), width=3)


# ------------------------------------------------------------------ 1 PACHINKO HEX
class PachinkoHex(BinsMixin, Flow):
    TITLE, SUB = "PACHINKO", "A HONEYCOMB OF PEGS  -  WHERE WILL THEY LAND"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 201, (110, 220, 255), "pluck", 294.0, (6, 10, 18)
    COUNTER = "BALLS LANDED"
    TARGET, SPAWN, SPX = 1000, 15.0, (420, 660)
    SCALE = MAJOR

    def build(self):
        for r in range(12):
            y = 560 + r * 70
            off = 0 if r % 2 == 0 else 40
            for c in range(13):
                x = 80 + off + c * 80
                if x < 1005:
                    self.pegs.append([x, y, 9, 0.0, 0.0])
        self.init_bins()

    def draw(self, d):
        self.draw_pegs(d, (80, 150, 210))
        self.draw_bins(d, 0.5, 0.85)
        self.draw_balls(d)

    def stats(self):
        return [f"LANDED  {self.count}"]


# ------------------------------------------------------------------ 2 GALTON BOARD
class GaltonBoard(BinsMixin, Flow):
    TITLE, SUB = "GALTON BOARD", "RANDOM BOUNCES BUILD A BELL CURVE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 202, (255, 210, 90), "click", 392.0, (12, 10, 6)
    COUNTER = "BALLS DROPPED"
    TARGET, SPAWN, SPX, BR, REST, FRIC, JIT = 1300, 20.0, (532, 548), 5, 0.2, 0.8, 40.0
    NBINS, DOT = 15, 6
    SP, VS, PR, ROWS = 50, 43, 18, 14
    BIN_TOP = 1150
    COLLECT_Y = 99999

    def build(self):
        sp = self.SP
        self.L, self.R = 540 - 7.5 * sp, 540 + 7.5 * sp
        for r in range(self.ROWS):
            y = 520 + r * self.VS
            for c in range(17):
                self.pegs.append([540 + (c - 8 + (0.5 if r % 2 else 0)) * sp, y, self.PR, 0.0, 0.0])
        # funnel guides at the top
        self.segs.append([380, 440, 520, 480, 8])
        self.segs.append([700, 440, 560, 480, 8])
        self.init_bins()

    def draw(self, d):
        self.draw_segs(d, (150, 120, 70))
        self.draw_pegs(d, (200, 160, 80))
        d.line((self.L, 470, self.L, self.BIN_BOT), fill=(70, 80, 110), width=3)
        self.draw_bins(d, 0.08, 0.16)
        self.draw_balls(d)

    def ball_col(self):
        return (255, 230, 160)


# ------------------------------------------------------------------ 3 HOURGLASS
class Hourglass(Flow):
    TITLE, SUB = "HOURGLASS", "EVERY GRAIN SLIPS THROUGH THE NECK"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 203, (255, 200, 120), "glass", 440.0, (12, 9, 6)
    COUNTER = "SAND FALLEN"
    TARGET, SPAWN, SPX, SPY, BR, REST, GRAV = 3400, 52.0, (528, 552), 980, 4, 0.2, 1400
    CAPMAX = 900
    COLS, CW, UNIT = 85, 8, 3
    COLLECT_Y = 99999

    def build(self):
        w = 9
        self.segs += [[520, 1000, 210, 1330, w], [560, 1000, 870, 1330, w], [210, 1330, 210, 1650, w], [870, 1330, 870, 1650, w]]
        self.top = [[210, 470, 210, 650, w], [870, 470, 870, 650, w], [210, 650, 520, 990, w], [870, 650, 560, 990, w]]
        self.h = [0] * self.COLS
        self.x0 = 210

    def surface(self, x):
        c = int(clamp((x - self.x0) // self.CW, 0, self.COLS - 1))
        return 1650 - self.h[c] * self.UNIT, c

    def collide_extra(self, b):
        y, c = self.surface(b[0])
        if b[1] + b[4] >= y and b[0] > self.x0 and b[0] < self.x0 + self.COLS * self.CW:
            b[6] = True
            self.h[c] += 1
            self.count += 1
            if self.count % 12 == 0:
                self.ev("hit", self.rng.random())

    def physics(self, dt):
        super().physics(dt)
        for _ in range(2):
            for c in range(self.COLS):
                for nb in (c - 1, c + 1):
                    if 0 <= nb < self.COLS and self.h[c] - self.h[nb] > 2:
                        # repose, but sand cannot climb the bulb walls
                        xn = self.x0 + nb * self.CW + self.CW / 2
                        self.h[c] -= 1
                        self.h[nb] += 1
                        break

    def leftovers(self):
        return max(0, self.TARGET - self.count)

    def draw(self, d):
        rem = 1 - self.count / self.TARGET
        # top sand body: fills the funnel from the neck up, proportional to what remains
        if rem > 0:
            lvl = 990 - (990 - 520) * math.sqrt(rem) * 0.95
            pts = []
            for k in range(40):
                yy = lvl + (990 - lvl) * k / 39
                hw = 330 if yy < 650 else 330 - (yy - 650) / (990 - 650) * 310
                pts.append((540 - hw + 6, yy))
            for k in range(39, -1, -1):
                yy = lvl + (990 - lvl) * k / 39
                hw = 330 if yy < 650 else 330 - (yy - 650) / (990 - 650) * 310
                pts.append((540 + hw - 6, yy))
            d.polygon(pts, fill=(220, 170, 90))
        for c in range(self.COLS):
            hh = self.h[c] * self.UNIT
            if hh:
                x = self.x0 + c * self.CW
                d.rectangle((x, 1650 - hh, x + self.CW - 1, 1650), fill=hsv(0.09 + 0.01 * math.sin(c * 0.5), 0.6, 0.85))
        for s in self.segs + self.top:
            d.line((s[0], s[1], s[2], s[3]), fill=(200, 210, 230), width=s[4])
        d.line((210, 1650, 870, 1650), fill=(200, 210, 230), width=9)
        d.line((210, 470, 870, 470), fill=(200, 210, 230), width=9)
        for b in self.balls:
            d.ellipse((b[0] - 3.5, b[1] - 3.5, b[0] + 3.5, b[1] + 3.5), fill=(240, 195, 120))


# ------------------------------------------------------------------ 4 SPINNER PEGS
class SpinnerPegs(BinsMixin, Flow):
    TITLE, SUB = "SPINNERS", "ROTATING BARS FLING EVERY BALL"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 204, (255, 120, 200), "marimba", 262.0, (14, 6, 14)
    COUNTER = "BALLS LANDED"
    TARGET, SPAWN, SPX = 800, 12.0, (300, 780)
    NBINS = 6

    def build(self):
        self.rots = []
        for i, (x, y, om) in enumerate([(300, 700, 2.2), (780, 700, -2.6), (540, 940, 1.8), (260, 1180, -2.0), (820, 1180, 2.4)]):
            self.rots.append([x, y, 120, i * 0.7, om])
        for r in range(3):
            for c in range(9):
                self.pegs.append([110 + c * 107 + (50 if r % 2 else 0), 560 + r * 330, 8, 0.0, 0.0])
        self.init_bins()

    def bars(self):
        out = []
        for (x, y, L, a, om) in self.rots:
            out.append(([x - math.cos(a) * L, y - math.sin(a) * L, x + math.cos(a) * L, y + math.sin(a) * L, 12], (x, y), om))
        return out

    def moving(self, dt):
        for r in self.rots:
            r[3] += r[4] * dt
        self.cache = self.bars()

    def collide_extra(self, b):
        for s, pv, om in self.cache:
            self.collide_seg(b, s, pivot=pv, omega=om)

    def draw(self, d):
        self.draw_pegs(d, (160, 90, 160))
        for s, pv, om in self.bars():
            d.line((s[0], s[1], s[2], s[3]), fill=(255, 140, 210), width=12)
            d.ellipse((pv[0] - 12, pv[1] - 12, pv[0] + 12, pv[1] + 12), fill=(255, 220, 240))
        self.draw_bins(d, 0.8, 1.0)
        self.draw_balls(d)


# ------------------------------------------------------------------ 5 FUNNEL MAZE
class FunnelMaze(Flow):
    TITLE, SUB = "FUNNEL MAZE", "FOUR FUNNELS  -  ONE CUP"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 205, (120, 255, 200), "pluck", 330.0, (6, 14, 12)
    COUNTER = "BALLS IN THE CUP"
    TARGET, SPAWN, SPX = 700, 11.0, (120, 960)
    COLLECT_Y = 1600

    def build(self):
        for i, (cx, y) in enumerate([(540, 600), (330, 860), (750, 1120), (540, 1420)]):
            half = 300 if i < 3 else 500
            gap = 26
            self.segs.append([cx - half, y - 120, cx - gap, y, 10])
            self.segs.append([cx + half, y - 120, cx + gap, y, 10])
        # spout under the last funnel: guides every ball straight down into the cup
        self.segs.append([540 - 26, 1420, 540 - 26, 1585, 10])
        self.segs.append([540 + 26, 1420, 540 + 26, 1585, 10])
        self.cup = 0

    def collect(self, b):
        assert 400 <= b[0] <= 680, "ball reached the bottom outside the cup"
        self.count += 1
        self.ev("special", self.rng.random())

    def draw(self, d):
        self.draw_segs(d, (90, 210, 170))
        d.rectangle((400, 1600, 680, 1680), outline=(90, 210, 170), width=6)
        lvl = 76 * self.count / self.TARGET
        d.rectangle((406, 1676 - lvl, 674, 1676), fill=(80, 200, 160))
        self.draw_balls(d)

    def ball_col(self):
        return hsv(0.35 + 0.2 * self.rng.random(), 0.5, 1.0)


# ------------------------------------------------------------------ 6 WORD PEGS
class WordPegs(BinsMixin, Flow):
    TITLE, SUB = "WORD PEGS", "BALLS RAIN THROUGH A WORD MADE OF PEGS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 206, (255, 190, 90), "marimba", 262.0, (14, 10, 6)
    COUNTER = "BALLS LANDED"
    TARGET, SPAWN, SPX = 900, 14.0, (120, 960)
    NBINS = 8
    SCALE = MAJOR

    def build(self):
        from eater import m_text
        mask = m_text("ASMR")
        cols, rows = 30, 11
        for r in range(rows):
            for c in range(cols):
                u, v = (c + .5) / cols * 2 - 1, (r + .5) / rows * 2 - 1
                if mask(u, v, c, r):
                    self.pegs.append([90 + c * 30, 640 + r * 30, 8, 0.0, 0.0])
        for r in range(3):
            for c in range(12):
                self.pegs.append([100 + c * 80 + (40 if r % 2 else 0), 1080 + r * 100, 9, 0.0, 0.0])
        self.init_bins()

    def draw(self, d):
        for p in self.pegs:
            col = (255, 170, 80) if p[1] < 1000 else (120, 100, 80)
            d.ellipse((p[0] - p[2], p[1] - p[2], p[0] + p[2], p[1] + p[2]), fill=col)
        self.draw_bins(d, 0.05, 0.15)
        self.draw_balls(d)

    def ball_col(self):
        return (255, 240, 220)


# ------------------------------------------------------------------ 7 PEG WHEEL
class PegWheel(BinsMixin, Flow):
    TITLE, SUB = "PEG WHEEL", "A SPINNING WHEEL OF PEGS SCATTERS THE RAIN"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 207, (150, 200, 255), "glass", 330.0, (6, 8, 16)
    COUNTER = "BALLS LANDED"
    TARGET, SPAWN, SPX = 900, 14.0, (360, 720)
    NBINS = 7

    def build(self):
        self.wheel = []
        for ring, n in ((120, 10), (210, 18), (300, 26)):
            for i in range(n):
                self.wheel.append([ring, 2 * math.pi * i / n])
        self.om = 0.9
        self.init_bins()
        self.cx, self.cy = 540, 960

    def moving(self, dt):
        self.pegs = []
        for r, a in self.wheel:
            ang = a + self.om * self.t
            x, y = self.cx + r * math.cos(ang), self.cy + r * math.sin(ang)
            self.pegs.append([x, y, 9, -self.om * r * math.sin(ang), self.om * r * math.cos(ang)])
        self.hash_pegs()

    def draw(self, d):
        d.ellipse((self.cx - 320, self.cy - 320, self.cx + 320, self.cy + 320), outline=(40, 50, 80), width=3)
        self.draw_pegs(d, (120, 170, 255))
        self.draw_bins(d, 0.55, 0.75)
        self.draw_balls(d)


# ================================================================== PAINTER BASE
class Painter(Sim):
    TS = False
    N = 40
    OX, OY, S = 60, 520, 24
    NB, SPEED, BR = 3, 520, 12
    TURN = 3.0
    MOTION = "bounce"
    GRAV = 900
    FINP = 0.97

    def __init__(self):
        c = type(self)
        self.K = calib(c.__name__, 1.0)
        self.NBALL = c.NB
        self.SPEED = c.SPEED * clamp(self.K, 0.45, 1.9)
        super().__init__()

    def picture(self, u, v):
        return hsv(u, 0.7, 1.0)

    def setup(self):
        N = self.N
        self.col = [[self.picture((c + .5) / N, (r + .5) / N) for c in range(N)] for r in range(N)]
        self.painted = [[False] * N for _ in range(N)]
        self.count = 0
        self.balls = []
        for i in range(self.NBALL):
            a = self.rng.uniform(0, 6.283)
            self.balls.append([self.OX + self.rng.uniform(100, N * self.S - 100), self.OY + self.rng.uniform(100, N * self.S - 100),
                               math.cos(a) * self.SPEED, math.sin(a) * self.SPEED, i])
        self.unp = []
        self.tick = 0
        self.sw = 0

    def paint(self, b):
        N, S = self.N, self.S
        r = self.BR
        for cx in range(int((b[0] - r - self.OX) // S), int((b[0] + r - self.OX) // S) + 1):
            for cy in range(int((b[1] - r - self.OY) // S), int((b[1] + r - self.OY) // S) + 1):
                if 0 <= cx < N and 0 <= cy < N and not self.painted[cy][cx]:
                    # cell centre within ball radius + half cell -> touched
                    px, py = self.OX + (cx + .5) * S, self.OY + (cy + .5) * S
                    if abs(px - b[0]) <= r + S / 2 - 1 and abs(py - b[1]) <= r + S / 2 - 1:
                        self.painted[cy][cx] = True
                        self.count += 1
                        self.on_paint(b, cx, cy)

    def on_paint(self, b, cx, cy):
        if self.count % 3 == 0:
            self.ev("hit", (cx + cy) / (2 * self.N))
        if self.count % 2 == 0:
            self.burst(self.OX + (cx + .5) * self.S, self.OY + (cy + .5) * self.S, self.col[cy][cx], 3, 120, 0.3)

    def assist(self):
        return clamp((self.target() - self.p) * 10 - 0.3, 0.0, 1.0)

    def physics(self, dt):
        N, S = self.N, self.S
        self.tick += 1
        if self.tick % 20 == 1:
            self.unp = [(c, r) for r in range(N) for c in range(N) if not self.painted[r][c]]
        a = self.assist()
        lo_x, hi_x = self.OX + self.BR, self.OX + N * S - self.BR
        lo_y, hi_y = self.OY + self.BR, self.OY + N * S - self.BR
        for b in self.balls:
            if self.MOTION == "grav":
                b[3] += self.GRAV * dt
            elif a > 0.05 and self.unp:
                best = min(self.unp[::max(1, len(self.unp) // 60)], key=lambda q: (self.OX + (q[0] + .5) * S - b[0]) ** 2 + (self.OY + (q[1] + .5) * S - b[1]) ** 2)
                tx, ty = self.OX + (best[0] + .5) * S, self.OY + (best[1] + .5) * S
                ang = math.atan2(b[3], b[2])
                want = math.atan2(ty - b[1], tx - b[0])
                diff = math.atan2(math.sin(want - ang), math.cos(want - ang))
                dist = math.hypot(tx - b[0], ty - b[1])
                rate = max(self.TURN * a, self.SPEED / max(15, dist) * 1.3 * a)
                ang += clamp(diff, -rate * dt, rate * dt)
                b[2], b[3] = math.cos(ang) * self.SPEED, math.sin(ang) * self.SPEED
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < lo_x:
                b[0], b[2] = lo_x, abs(b[2])
            elif b[0] > hi_x:
                b[0], b[2] = hi_x, -abs(b[2])
            if b[1] < lo_y:
                b[1], b[3] = lo_y, abs(b[3])
            elif b[1] > hi_y:
                b[1] = hi_y
                b[3] = -abs(b[3]) if self.MOTION != "grav" else -math.sqrt(2 * self.GRAV * (N * S - 2 * self.BR)) * self.rng.uniform(0.9, 1.0)
                if self.MOTION == "grav":
                    b[2] = self.rng.uniform(-420, 420)
                    if a > 0.05 and self.unp:
                        q = self.unp[self.rng.randrange(len(self.unp))]
                        tx = self.OX + (q[0] + .5) * S
                        b[2] = clamp((tx - b[0]) / 1.2, -700, 700)
            self.paint(b)
        self.p = min(0.999, self.count / (N * N))
        if self.count >= self.FINP * N * N:
            self.sw += 1
            if self.sw % 3 == 0:
                for r in range(N):
                    for c in range(N):
                        if not self.painted[r][c]:
                            self.painted[r][c] = True
                            self.count += 1
                            self.burst(self.OX + (c + .5) * S, self.OY + (r + .5) * S, self.col[r][c], 5, 160, 0.4)
                            self.ev("hit", self.rng.random())
                            return
                self.p = 1.0
        if self.count >= N * N:
            self.p = 1.0

    def audit_missed(self):
        n = 0
        for b in self.balls:
            c, r = int((b[0] - self.OX) // self.S), int((b[1] - self.OY) // self.S)
            if 0 <= c < self.N and 0 <= r < self.N and not self.painted[r][c]:
                n += 1
        return n

    def leftovers(self):
        return sum(row.count(False) for row in self.painted)

    def ball_color(self, b):
        return (255, 255, 255)

    def draw(self, d):
        N, S = self.N, self.S
        d.rectangle((self.OX - 4, self.OY - 4, self.OX + N * S + 4, self.OY + N * S + 4), outline=(70, 70, 85), width=4)
        for r in range(N):
            for c in range(N):
                x, y = self.OX + c * S, self.OY + r * S
                d.rectangle((x, y, x + S - 1, y + S - 1), fill=self.col[r][c] if self.painted[r][c] else (24, 24, 30))
        for b in self.balls:
            d.ellipse((b[0] - self.BR, b[1] - self.BR, b[0] + self.BR, b[1] + self.BR), fill=self.ball_color(b), outline=(0, 0, 0), width=3)


class HeartReveal(Painter):
    TITLE, SUB = "HEART REVEAL", "BOUNCING BALLS UNCOVER A HIDDEN HEART"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 211, (255, 120, 170), "glass", 330.0, (12, 6, 12)
    COUNTER = "PICTURE REVEALED"
    NB = 2

    def picture(self, u, v):
        x, y = (u - 0.5) * 2.6, -(v - 0.5) * 2.6 + 0.25
        inside = (x * x + y * y - 1) ** 3 - x * x * y ** 3 < 0
        if inside:
            return hsv(0.95 + 0.05 * v, 0.75, 1.0 - 0.25 * v)
        return hsv(0.75 + 0.1 * u, 0.45, 0.35 + 0.3 * (1 - v))


class SunsetReveal(Painter):
    TITLE, SUB = "SUNSET", "BOUNCING BALLS PAINT THE EVENING SKY"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 212, (255, 160, 80), "marimba", 262.0, (10, 8, 14)
    COUNTER = "SUNSET PAINTED"
    NB = 2

    def picture(self, u, v):
        if (u - 0.5) ** 2 + (v - 0.55) ** 2 < 0.035 and v < 0.62:
            return (255, 220, 120)
        if v > 0.62:
            band = int((v - 0.62) * 60) % 2
            return hsv(0.58, 0.6, 0.45 + 0.15 * band) if abs(u - 0.5) > 0.12 * (1 - (v - 0.62) * 2) else (255, 190, 110)
        return hsv(0.02 + 0.12 * v, 0.75, 1.0 - 0.15 * (0.62 - v))


class RainbowSwirl(Painter):
    TITLE, SUB = "RAINBOW SWIRL", "THREE BALLS PAINT A HYPNOTIC SWIRL"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 213, (200, 140, 255), "bell", 262.0, (8, 6, 14)
    COUNTER = "SWIRL PAINTED"
    NB = 3
    SCALE = MAJOR

    def picture(self, u, v):
        x, y = u - 0.5, v - 0.5
        r = math.hypot(x, y)
        a = math.atan2(y, x)
        return hsv(a / (2 * math.pi) + r * 2.2, 0.75, 1.0)


class MosaicTiles(Painter):
    TITLE, SUB = "MOSAIC", "A SINGLE BALL LAYS EVERY TILE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 214, (120, 230, 200), "click", 392.0, (8, 12, 12)
    COUNTER = "MOSAIC LAID"
    NB, SPEED, BR = 1, 760, 14
    N, S = 32, 30

    def picture(self, u, v):
        k = int(u * 8) * 31 + int(v * 8) * 17
        base = [(250, 210, 120), (120, 210, 200), (240, 130, 120), (140, 170, 240), (240, 240, 230)]
        c = base[k % 5]
        shade = 0.85 + 0.15 * ((int(u * 32) + int(v * 32)) % 2)
        return tuple(int(x * shade) for x in c)

    def __init__(self):
        Sim.__init__(self) if False else None
        c = type(self)
        self.K = calib(c.__name__, 1.0)
        self.NBALL = 1
        self.SPEED = c.SPEED * clamp(self.K, 0.6, 1.7)
        Sim.__init__(self)


class ThreePainters(Painter):
    TITLE, SUB = "THREE PAINTERS", "RED  -  GREEN  -  BLUE  -  WHO PAINTS MORE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 215, (255, 255, 255), "pop", 262.0, (10, 10, 12)
    COUNTER = "CANVAS COVERED"
    NB = 3
    TEAM = [(255, 80, 90), (90, 220, 120), (90, 150, 255)]

    def setup(self):
        super().setup()
        self.owner = [[-1] * self.N for _ in range(self.N)]
        self.score = [0, 0, 0]

    def on_paint(self, b, cx, cy):
        team = b[4] % 3
        self.owner[cy][cx] = team
        self.score[team] += 1
        self.col[cy][cx] = tuple(int(v * (0.8 + 0.2 * ((cx + cy) % 2))) for v in self.TEAM[team])
        if self.count % 3 == 0:
            self.ev("hit", team / 3 + self.rng.random() * 0.2)

    def ball_color(self, b):
        return self.TEAM[b[4] % 3]

    def stats(self):
        return [f"R {self.score[0]}   G {self.score[1]}   B {self.score[2]}"]


BATCH_E = [PachinkoHex, GaltonBoard, Hourglass, SpinnerPegs, FunnelMaze, WordPegs, PegWheel,
           HeartReveal, SunsetReveal, RainbowSwirl, MosaicTiles, ThreePainters]
