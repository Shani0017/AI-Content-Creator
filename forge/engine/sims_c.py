"""ASMR batch C."""
import math
from core import *
from sims_a import nearest
from sims_b import clamp


# ---------------------------------------------------------------- 22 POLYRHYTHM RINGS
class Polyrhythm(Sim):
    TITLE, SUB = "POLYRHYTHM", "EIGHT RINGS  -  EIGHT TEMPOS  -  ONE SONG"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 22, (120, 220, 255), "bell", 220.0
    BG = (6, 8, 16)
    CX, CY = 540, 1030
    COUNTER = "SONG PROGRESS"
    SCALE = PENT

    def setup(self):
        self.ph = [0.0] * 8
        self.lit = [0.0] * 8

    def physics(self, dt):
        sp = clamp(self.gain(), 0.4, 3.0)
        for k in range(8):
            old = self.ph[k]
            self.ph[k] += dt * (0.55 + 0.11 * k) * sp * 2 * math.pi * 0.5
            if int(old / (2 * math.pi)) != int(self.ph[k] / (2 * math.pi)):
                self.ev("hit", k / 8)
                self.lit[k] = 1.0
                self.burst(self.CX + (90 + k * 50) * math.cos(-math.pi / 2), self.CY - (90 + k * 50), hsv(k / 8), 8, 200, 0.5)
            self.lit[k] = max(0.0, self.lit[k] - dt * 2.5)
        if self.done_at is None:
            self.p = min(1.0, self.p + dt / self.T_END * clamp(self.gain(), 0.3, 3))

    def draw(self, d):
        for k in range(8):
            R = 90 + k * 50
            d.ellipse((self.CX - R, self.CY - R, self.CX + R, self.CY + R), outline=hsv(k / 8, 0.5, 0.45 + 0.55 * self.lit[k]), width=4 + int(5 * self.lit[k]))
            a = self.ph[k] - math.pi / 2
            x, y = self.CX + R * math.cos(a), self.CY + R * math.sin(a)
            d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=hsv(k / 8, 0.7, 1))
        d.line((self.CX, self.CY - 90, self.CX, self.CY - 90 - 7 * 50 - 30), fill=(70, 70, 100), width=2)


# ---------------------------------------------------------------- 23 DOMINO SPIRAL
class DominoSpiral(Sim):
    TITLE, SUB = "DOMINO SPIRAL", "ONE TAP  -  THE WHOLE SPIRAL FALLS"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 23, (255, 140, 90), "click", 262.0
    BG = (14, 9, 8)
    CX, CY = 540, 1030
    N = 620
    COUNTER = "DOMINOES FALLEN"

    def setup(self):
        self.dom = []
        a, r, i = 0.0, 40.0, 0
        while r < 480:
            self.dom.append((self.CX + r * math.cos(a), self.CY + r * math.sin(a), a, i))
            a += 21.0 / r
            r = 40 + 3.6 * a
            i += 1
        self.N = len(self.dom)
        self.front = 0.0
        self.last = 0

    def physics(self, dt):
        if self.done_at is None:
            self.front += dt * clamp(self.gain(), 0.1, 6) * self.N / self.T_END
            self.p = min(1.0, self.front / self.N)
        n = int(self.front)
        while self.last < n and self.last < self.N:
            self.last += 1
            if self.last % 2 == 0:
                self.ev("hit", (self.last % 24) / 24)
            x, y, a, i = self.dom[self.last - 1]
            if self.last % 5 == 0:
                self.burst(x, y, hsv(i / self.N), 3, 120, 0.3)

    def draw(self, d):
        for (x, y, a, i) in self.dom:
            f = clamp(self.front - i, 0, 1)
            col = hsv(i / self.N * 0.9, 0.7, 1.0 if f == 0 else 0.55)
            ln = 17 * (1 - 0.6 * f)
            tx, ty = math.cos(a), math.sin(a)
            bx, by = -math.sin(a) * 10 * f, math.cos(a) * 10 * f
            d.line((x - tx * ln / 2 + bx, y - ty * ln / 2 + by, x + tx * ln / 2 + bx, y + ty * ln / 2 + by), fill=col, width=9)


# ---------------------------------------------------------------- 24 SAND FALL
class SandFall(Sim):
    TITLE, SUB = "SAND FALL", "A RIVER OF GRAINS  -  BUILD THE DUNE"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 24, (255, 200, 110), "glass", 392.0
    BG = (14, 11, 8)
    COLS, CW, BASEY, UNIT = 135, 8, 1700, 4
    COUNTER = "DUNE BUILT"
    TARGET = 5200
    PLATES = [(380, 640, 700, 720), (1070, 800, 420, 890), (130, 1000, 600, 1090), (760, 1230, 380, 1320)]

    def setup(self):
        self.h = [0] * self.COLS
        self.grains = []
        self.acc_spawn = 0.0
        self.count = 0

    def top(self, x):
        return self.BASEY - self.h[min(self.COLS - 1, max(0, int(x // self.CW)))] * self.UNIT

    def physics(self, dt):
        self.acc_spawn += clamp(105 * self.gain(), 25, 420) * dt
        while self.acc_spawn >= 1:
            self.acc_spawn -= 1
            if len(self.grains) < 2200:
                self.grains.append([self.rng.uniform(505, 575), 440.0, self.rng.uniform(-40, 40), 120.0, self.rng.random()])
        keep = []
        for g in self.grains:
            g[3] += 1500 * dt
            g[0] += g[2] * dt
            g[1] += g[3] * dt
            for (x0, y0, x1, y1) in self.PLATES:
                dx, dy = x1 - x0, y1 - y0
                L2 = dx * dx + dy * dy
                u = clamp(((g[0] - x0) * dx + (g[1] - y0) * dy) / L2, 0, 1)
                px, py = x0 + u * dx, y0 + u * dy
                ex, ey = g[0] - px, g[1] - py
                dist = math.hypot(ex, ey)
                if dist < 9:
                    n = (-dy, dx)
                    nl = math.hypot(*n)
                    n = (n[0] / nl, n[1] / nl)
                    if n[1] > 0:
                        n = (-n[0], -n[1])  # upward-facing normal
                    vn = g[2] * n[0] + g[3] * n[1]
                    if vn < 0:
                        g[2] -= 1.25 * vn * n[0]
                        g[3] -= 1.25 * vn * n[1]
                        g[2] += self.rng.uniform(-70, 70)
                        if self.rng.random() < 0.02:
                            self.ev("hit", self.rng.random())
                    g[0] += n[0] * (9 - dist)
                    g[1] += n[1] * (9 - dist)
                    g[2] *= 0.965
                    g[3] *= 0.985
            if g[0] < 8 or g[0] > self.COLS * self.CW - 8:
                g[2] = -g[2] * 0.5
                g[0] = clamp(g[0], 8, self.COLS * self.CW - 8)
            col = min(self.COLS - 1, max(0, int(g[0] // self.CW)))
            if g[1] >= self.top(g[0]) - 3:
                self.h[col] += 1
                self.count += 1
                self.p = min(1.0, self.count / self.TARGET)
                if self.count % 25 == 0:
                    self.ev("hit", self.rng.random())
                continue
            keep.append(g)
        self.grains = keep
        for _ in range(4):
            for c in range(self.COLS):
                for nb in (c - 1, c + 1):
                    if 0 <= nb < self.COLS and self.h[c] - self.h[nb] > 2:
                        self.h[c] -= 1
                        self.h[nb] += 1
                        break

    def draw(self, d):
        for (x0, y0, x1, y1) in self.PLATES:
            d.line((x0, y0, x1, y1), fill=(170, 125, 80), width=14)
            d.ellipse((x0 - 7, y0 - 7, x0 + 7, y0 + 7), fill=(170, 125, 80))
            d.ellipse((x1 - 7, y1 - 7, x1 + 7, y1 + 7), fill=(170, 125, 80))
        d.rectangle((490, 400, 590, 410), fill=(120, 90, 60))
        for c in range(self.COLS):
            hh = self.h[c] * self.UNIT
            if hh > 0:
                x = c * self.CW
                d.rectangle((x, self.BASEY - hh, x + self.CW - 1, self.BASEY), fill=hsv(0.09 + 0.012 * math.sin(c * 0.4 + hh * 0.03), 0.62, 0.5 + 0.45 * min(1, hh / 450)))
        for g in self.grains:
            d.ellipse((g[0] - 3.5, g[1] - 3.5, g[0] + 3.5, g[1] + 3.5), fill=(255, 215, 130))


# ---------------------------------------------------------------- 25 CORNER HUNT
class CornerHunt(Sim):
    TITLE, SUB = "LIGHT THE FRAME", "EVERY WALL HIT LIGHTS A TILE"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 25, (255, 230, 90), "marimba", 294.0
    BG = (8, 8, 12)
    L, R, T, B = 110, 970, 480, 1620
    HONEST = True
    COUNTER = "FRAME LIT"
    SCALE = MAJOR

    def setup(self):
        per = 2 * (self.R - self.L + self.B - self.T)
        self.NT = 300
        self.tiles = [False] * self.NT
        self.balls = []
        for i in range(4):
            a = self.rng.uniform(0.3, 1.2) + (i % 4) * 1.57
            sp = 400 + 90 * i
            self.balls.append([self.rng.uniform(self.L + 60, self.R - 60), self.rng.uniform(self.T + 60, self.B - 60), math.cos(a) * sp, math.sin(a) * sp, 26 + 3 * i])
        self.rem = 0
        self.M = self.NT

    def tile_pos(self, k):
        """perimeter position for tile k"""
        w, h = self.R - self.L, self.B - self.T
        s = k / self.NT * 2 * (w + h)
        if s < w:
            return self.L + s, self.T
        s -= w
        if s < h:
            return self.R, self.T + s
        s -= h
        if s < w:
            return self.R - s, self.B
        s -= w
        return self.L, self.B - s

    def physics(self, dt):
        for b in self.balls:
            r = b[4]
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            hit = None
            if b[0] < self.L + r:
                b[0], b[2], hit = self.L + r, abs(b[2]), (self.L, b[1])
            elif b[0] > self.R - r:
                b[0], b[2], hit = self.R - r, -abs(b[2]), (self.R, b[1])
            if b[1] < self.T + r:
                b[1], b[3], hit = self.T + r, abs(b[3]), (b[0], self.T)
            elif b[1] > self.B - r:
                b[1], b[3], hit = self.B - r, -abs(b[3]), (b[0], self.B)
            if hit:
                self.ev("hit", self.rng.random())
                if True:
                    k = min((i for i in range(self.NT) if not self.tiles[i]), key=lambda i: (self.tile_pos(i)[0] - hit[0]) ** 2 + (self.tile_pos(i)[1] - hit[1]) ** 2, default=None)
                    if k is not None:
                        self.tiles[k] = True
                        self.rem += 1
                        self.burst(*hit, (255, 230, 90), 8, 240, 0.5)

    def sweep(self):
        for k in range(self.NT):
            if not self.tiles[k]:
                self.tiles[k] = True
                self.rem += 1
                x, y = self.tile_pos(k)
                self.burst(x, y, (255, 230, 90), 6, 240, 0.5)
                self.ev("hit", (self.rem / self.M) % 1)
                self.p = min(0.999, self.rem / self.M)
                return True
        return False

    def draw(self, d):
        for k in range(self.NT):
            x, y = self.tile_pos(k)
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=hsv(k / self.NT, 0.7, 1) if self.tiles[k] else (30, 30, 42))
        for i, b in enumerate(self.balls):
            d.ellipse((b[0] - b[4], b[1] - b[4], b[0] + b[4], b[1] + b[4]), fill=hsv(i / 10, 0.6, 1), outline=(255, 255, 255), width=3)


# ---------------------------------------------------------------- 26 MAGNET SWARM
class MagnetSwarm(Sim):
    TITLE, SUB = "MAGNET SWARM", "500 BALLS CHASE ONE MAGNET"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 26, (110, 255, 200), "glass", 330.0
    BG = (6, 12, 12)
    LIST, AIDX = "sparks", 3
    HONEST = True
    COUNTER = "SPARKS COLLECTED"
    FIN = 0.9

    def setup(self):
        self.sw = [[self.rng.uniform(100, 980), self.rng.uniform(500, 1600), 0.0, 0.0] for _ in range(500)]
        self.sparks = [[self.rng.uniform(100, 980), self.rng.uniform(480, 1640), self.rng.random(), True] for _ in range(900)]
        self.M, self.rem = 900, 0
        self.mx, self.my = 540, 1050

    def physics(self, dt):
        t = self.t
        self.mx = 540 + 380 * math.sin(t * 0.7) * math.cos(t * 0.21)
        self.my = 1060 + 520 * math.sin(t * 0.53 + 1)
        for s in self.sw:
            dx, dy = self.mx - s[0], self.my - s[1]
            dd = math.hypot(dx, dy) or 1
            f = 900 + 600 * min(1, dd / 400)
            s[2] += dx / dd * f * dt
            s[3] += dy / dd * f * dt
            s[2] *= 0.965
            s[3] *= 0.965
            s[0] += s[2] * dt
            s[1] += s[3] * dt
        rad = 54 + 88 * self.p
        for q in self.sparks:
            if q[3] and (q[0] - self.mx) ** 2 + (q[1] - self.my) ** 2 < rad ** 2:
                if True:
                    q[3] = False
                    self.rem += 1
                    self.burst(q[0], q[1], hsv(q[2] * 0.3 + 0.4), 6, 220, 0.5)
                    self.ev("hit", q[2])

    def draw(self, d):
        d.rectangle((40, 440, 1040, 1700), outline=(40, 90, 90), width=3)
        for q in self.sparks:
            if q[3]:
                d.ellipse((q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6), fill=hsv(q[2] * 0.3 + 0.4, 0.6, 1))
        for s in self.sw:
            d.ellipse((s[0] - 4, s[1] - 4, s[0] + 4, s[1] + 4), fill=(190, 255, 235))
        d.ellipse((self.mx - 20, self.my - 20, self.mx + 20, self.my + 20), fill=(255, 80, 100))


# ---------------------------------------------------------------- 27 PENDULUM WAVE
class PendulumWave(Sim):
    TITLE, SUB = "PENDULUM WAVE", "TINY LENGTH CHANGES  -  HYPNOTIC PATTERNS"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 27, (255, 130, 200), "bell", 196.0
    BG = (8, 6, 14)
    N = 22
    COUNTER = "WAVE CYCLE"
    SCALE = PENT

    def setup(self):
        self.last = [0] * self.N

    def phase(self, k):
        return 2 * math.pi * (36 + k) * self.t / 60.0

    def physics(self, dt):
        for k in range(self.N):
            s = math.sin(self.phase(k))
            side = 1 if math.cos(self.phase(k)) > 0 else -1
            cur = int(self.phase(k) / math.pi)
            if cur != self.last[k]:
                self.last[k] = cur
                self.ev("hit", k / self.N)
                x = 100 + k * 40.0
                self.burst(x, 1130 + 360 * math.sin(self.phase(k)), hsv(k / self.N), 4, 150, 0.4)
        if self.done_at is None:
            self.p = min(1.0, self.t / self.T_END)

    def draw(self, d):
        d.rectangle((60, 596, 1020, 610), fill=(90, 80, 120))
        pts = []
        for k in range(self.N):
            x = 100 + k * 40.0
            y = 1130 + 360 * math.sin(self.phase(k))
            pts.append((x, y))
            d.line((x, 610, x, y), fill=(95, 90, 140), width=2)
        d.line(pts, fill=(60, 55, 90), width=2)
        for k, (x, y) in enumerate(pts):
            d.ellipse((x - 17, y - 17, x + 17, y + 17), fill=hsv(k / self.N, 0.7, 1))


# ---------------------------------------------------------------- 28 BLACK HOLE
class BlackHole(Sim):
    TITLE, SUB = "BLACK HOLE", "BALLS SPIRAL IN  -  NOTHING ESCAPES"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 28, (255, 150, 60), "pluck", 147.0
    BG = (4, 4, 8)
    CX, CY = 540, 1050
    N = 620
    COUNTER = "CONSUMED"
    TIMESCALE = True

    def setup(self):
        self.balls = []
        for i in range(self.N):
            a = self.rng.uniform(0, 6.283)
            r = self.rng.uniform(120, 520)
            v = math.sqrt(1.2e7 / max(r, 80)) * self.rng.uniform(0.45, 0.97)
            self.balls.append([self.CX + math.cos(a) * r, self.CY + math.sin(a) * r, -math.sin(a) * v, math.cos(a) * v, self.rng.uniform(0.6, 1.8), []])
        self.eaten = 0

    def hole(self):
        return 22 + 40 * self.p

    def physics(self, dt):
        drag = 0.003 + 0.05 * clamp(self.gain() - 0.4, 0, 6) * 0.1 + (0.25 if self.t > self.T_END * 0.8 else 0)
        keep = []
        for b in self.balls:
            dx, dy = self.CX - b[0], self.CY - b[1]
            dd = math.hypot(dx, dy) or 1
            f = 1.2e7 / (dd * dd + 4000)
            b[2] += dx / dd * f * dt
            b[3] += dy / dd * f * dt
            b[2] *= 1 - drag * b[4] * dt
            b[3] *= 1 - drag * b[4] * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[5].append((b[0], b[1]))
            b[5] = b[5][-14:]
            if dd < self.hole():
                self.eaten += 1
                self.p = min(1.0, self.eaten / self.N)
                self.burst(b[0], b[1], (255, 170, 80), 4, 160, 0.35)
                if self.eaten % 2 == 0:
                    self.ev("hit", dd / 500 + b[4] * 0.1)
                continue
            keep.append(b)
        self.balls = keep

    def draw(self, d):
        for k in range(6, 0, -1):
            r = self.hole() + k * 14
            d.ellipse((self.CX - r, self.CY - r, self.CX + r, self.CY + r), outline=(int(255 / k ** 0.5), int(130 / k), int(40 / k)), width=3)
        for b in self.balls:
            for i, (x, y) in enumerate(b[5]):
                a = i / 14
                d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(int(255 * a * 0.7), int(140 * a * 0.7), int(50 * a * 0.7)))
            d.ellipse((b[0] - 5, b[1] - 5, b[0] + 5, b[1] + 5), fill=(255, 230, 190))
        r = self.hole()
        d.ellipse((self.CX - r, self.CY - r, self.CX + r, self.CY + r), fill=(0, 0, 0), outline=(255, 180, 90), width=4)


# ---------------------------------------------------------------- 29 CRUSHER WALLS
class CrusherWalls(Sim):
    TITLE, SUB = "CRUSHER WALLS", "THE WALLS CLOSE IN  -  THE BEAT GETS FASTER"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 29, (255, 100, 90), "pop", 175.0
    BG = (14, 7, 7)
    T, B = 460, 1640
    COUNTER = "SQUEEZE"

    def setup(self):
        self.balls = [[540 + self.rng.uniform(-300, 300), self.rng.uniform(600, 1500), self.rng.uniform(-1, 1) * 500, self.rng.uniform(-1, 1) * 500] for _ in range(140)]

    def left(self):
        return 60 + 440 * self.p

    def right(self):
        return 1020 - 440 * self.p

    def physics(self, dt):
        if self.done_at is None:
            self.p = min(0.995 if self.t < self.T_END else 1.0, self.p + dt * 0.0143 * clamp(self.gain(), 0.2, 4))
            if self.p > 0.99:
                self.p = 1.0
        L, R = self.left(), self.right()
        for b in self.balls:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < L + 7:
                b[0], b[2] = L + 7, abs(b[2]) + 20
                self.ev("hit", self.rng.random())
            if b[0] > R - 7:
                b[0], b[2] = R - 7, -abs(b[2]) - 20
                self.ev("hit", self.rng.random())
            sp = math.hypot(b[2], b[3])
            if sp > 1500:
                b[2], b[3] = b[2] * 1500 / sp, b[3] * 1500 / sp
            if b[1] < self.T + 7 or b[1] > self.B - 7:
                b[3] = -b[3]
                b[1] = clamp(b[1], self.T + 7, self.B - 7)
            if self.rng.random() < 0.01:
                b[2] *= 0.95

    def draw(self, d):
        L, R = self.left(), self.right()
        d.rectangle((0, self.T, L, self.B), fill=(150, 40, 40))
        d.rectangle((R, self.T, 1080, self.B), fill=(150, 40, 40))
        for k in range(0, int(self.B - self.T), 60):
            d.polygon([(L, self.T + k), (L + 30, self.T + k + 30), (L, self.T + k + 60)], fill=(220, 70, 60))
            d.polygon([(R, self.T + k), (R - 30, self.T + k + 30), (R, self.T + k + 60)], fill=(220, 70, 60))
        d.line((0, self.T, 1080, self.T), fill=(100, 40, 40), width=4)
        d.line((0, self.B, 1080, self.B), fill=(100, 40, 40), width=4)
        for b in self.balls:
            d.ellipse((b[0] - 7, b[1] - 7, b[0] + 7, b[1] + 7), fill=(255, 235, 220))


# ---------------------------------------------------------------- 30 MARBLE RUN
class MarbleRun(Sim):
    TITLE, SUB = "MARBLE RUN", "ROLL  -  CLICK  -  CLATTER  -  COLLECT"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 30, (100, 220, 255), "click", 523.0
    BG = (8, 10, 16)
    COUNTER = "MARBLES COLLECTED"
    TARGET = 650

    def setup(self):
        self.segs = []
        y = 520
        for i in range(8):
            if i % 2 == 0:
                self.segs.append((70, y, 900, y + 70))
            else:
                self.segs.append((1010, y, 180, y + 70))
            y += 135
        self.balls, self.acc_spawn, self.col = [], 0.0, 0

    def physics(self, dt):
        self.acc_spawn += clamp(5 * self.gain(), 1, 36) * dt
        while self.acc_spawn >= 1 and len(self.balls) < 260:
            self.acc_spawn -= 1
            self.balls.append([self.rng.uniform(80, 200), 470, self.rng.uniform(0, 80), 0.0, self.rng.random()])
        keep = []
        for b in self.balls:
            b[3] += 1500 * dt
            oy = b[1]
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            for (x0, y0, x1, y1) in self.segs:
                lo, hi = min(x0, x1), max(x0, x1)
                if lo <= b[0] <= hi:
                    ly = y0 + (y1 - y0) * (b[0] - x0) / (x1 - x0)
                    if oy - 14 <= ly <= b[1] + 12 and b[3] > 0:
                        b[1] = ly - 12
                        slope = (y1 - y0) / (x1 - x0)
                        b[3] = -b[3] * 0.25
                        b[2] += 90 * (1 if x1 > x0 else -1)
                        if abs(b[2]) > 420:
                            b[2] = 420 * (1 if b[2] > 0 else -1)
                        if self.rng.random() < 0.3:
                            self.ev("hit", self.rng.random())
            if b[0] < 40 or b[0] > 1040:
                b[2] = -b[2]
                b[0] = clamp(b[0], 40, 1040)
            if b[1] > 1700:
                self.col += 1
                self.p = min(1.0, self.col / self.TARGET)
                self.ev("special", self.rng.random())
                continue
            keep.append(b)
        self.balls = keep

    def draw(self, d):
        for (x0, y0, x1, y1) in self.segs:
            d.line((x0, y0, x1, y1), fill=(90, 150, 200), width=10)
        for b in self.balls:
            d.ellipse((b[0] - 10, b[1] - 10, b[0] + 10, b[1] + 10), fill=hsv(b[4], 0.6, 1))

    def stats(self):
        return [f"COLLECTED  {self.col}"]


BATCH_C = [Polyrhythm, DominoSpiral, SandFall, CornerHunt, MagnetSwarm, PendulumWave, BlackHole, CrusherWalls, MarbleRun]
