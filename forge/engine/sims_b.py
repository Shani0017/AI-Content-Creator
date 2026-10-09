"""ASMR batch B."""
import math
from core import *
from sims_a import nearest


def clamp(x, a, b):
    return max(a, min(b, x))


# ---------------------------------------------------------------- 13 FOUR KINGDOMS
class FourKingdoms(Sim):
    TITLE, SUB = "FOUR KINGDOMS", "BALLS CONQUER TILES  -  ONE COLOUR RULES ALL"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 62, 13, (255, 255, 255), "marimba", 262.0
    BG = (10, 10, 12)
    COLS, ROWS, S, OX, OY = 24, 30, 40, 60, 440
    TEAMS = [(255, 90, 90), (90, 170, 255), (110, 230, 140), (255, 210, 80)]
    COUNTER = "RED CONQUEST"
    TIMESCALE = True

    def setup(self):
        C, R = self.COLS, self.ROWS
        self.grid = [[(0 if c < C // 2 else 1) if r < R // 2 else (2 if c < C // 2 else 3) for c in range(C)] for r in range(R)]
        self.balls = []
        for team in range(4):
            for i in range(4):
                a = self.rng.uniform(0, 6.28)
                self.balls.append([self.OX + (0.25 + 0.5 * (team % 2)) * C * self.S + self.rng.uniform(-60, 60),
                                   self.OY + (0.25 + 0.5 * (team // 2)) * R * self.S + self.rng.uniform(-60, 60),
                                   math.cos(a) * 420, math.sin(a) * 420, team])
        self.ACC = self.TEAMS[0]

    def physics(self, dt):
        C, R, S = self.COLS, self.ROWS, self.S
        g = self.gain()
        for b in self.balls:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < self.OX + 8 or b[0] > self.OX + C * S - 8:
                b[2] = -b[2]
                b[0] = clamp(b[0], self.OX + 8, self.OX + C * S - 8)
            if b[1] < self.OY + 8 or b[1] > self.OY + R * S - 8:
                b[3] = -b[3]
                b[1] = clamp(b[1], self.OY + 8, self.OY + R * S - 8)
            c, r = int((b[0] - self.OX) // S), int((b[1] - self.OY) // S)
            if 0 <= c < C and 0 <= r < R and b[4] != 0 and self.grid[r][c] == 0 and g > 1.3 and self.rng.random() < 0.05 * (g - 1.0):
                b[4] = 0
            if 0 <= c < C and 0 <= r < R and self.grid[r][c] != b[4]:
                k = 1.0 if b[4] == 0 else clamp(0.6 / g, 0.15, 1.0)
                if self.rng.random() < k:
                    self.grid[r][c] = b[4]
                    self.burst(b[0], b[1], self.TEAMS[b[4]], 3, 150, 0.3)
                    self.ev("hit", (c + r) / 54)
                if self.rng.random() < 0.5:
                    b[2], b[3] = -b[2], b[3]
                else:
                    b[2], b[3] = b[2], -b[3]
        n0 = sum(row.count(0) for row in self.grid)
        self.p = min(0.999, n0 / (C * R))
        if n0 >= 0.9 * C * R:
            self._sw = getattr(self, '_sw', 0) + 1
            if self._sw % 3 == 0:
                for r in range(R):
                    for c in range(C):
                        if self.grid[r][c] != 0:
                            self.grid[r][c] = 0
                            self.burst(self.OX + c * S + S / 2, self.OY + r * S + S / 2, self.TEAMS[0], 4, 140, 0.35)
                            self.ev("hit", (c + r) / 54)
                            return
                self.p = 1.0

    def draw(self, d):
        S = self.S
        for r in range(self.ROWS):
            for c in range(self.COLS):
                x, y = self.OX + c * S, self.OY + r * S
                d.rectangle((x, y, x + S - 2, y + S - 2), fill=tuple(int(v * 0.55) for v in self.TEAMS[self.grid[r][c]]))
        for b in self.balls:
            d.ellipse((b[0] - 11, b[1] - 11, b[0] + 11, b[1] + 11), fill=self.TEAMS[b[4]], outline=(255, 255, 255), width=3)


# ---------------------------------------------------------------- 14 CONTAGION
class Contagion(Sim):
    TITLE, SUB = "CONTAGION", "ONE INFECTED BALL  -  TOUCH SPREADS IT"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 14, (255, 70, 90), "pop", 196.0
    BG = (8, 14, 12)
    L, R, T, B = 60, 1020, 420, 1650
    N = 80
    COUNTER = "INFECTED"
    TIMESCALE = True

    def setup(self):
        self.balls = []
        for i in range(self.N):
            a = self.rng.uniform(0, 6.28)
            self.balls.append([self.rng.uniform(self.L + 20, self.R - 20), self.rng.uniform(self.T + 20, self.B - 20), math.cos(a) * 65, math.sin(a) * 65, i == 0])

    def physics(self, dt):
        k = 1.0
        cell = {}
        for i, b in enumerate(self.balls):
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < self.L + 8 or b[0] > self.R - 8:
                b[2] = -b[2]
                b[0] = clamp(b[0], self.L + 8, self.R - 8)
            if b[1] < self.T + 8 or b[1] > self.B - 8:
                b[3] = -b[3]
                b[1] = clamp(b[1], self.T + 8, self.B - 8)
            cell.setdefault((int(b[0] // 40), int(b[1] // 40)), []).append(i)
        for (cx, cy), ids in cell.items():
            for dx in (0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy < 0:
                        continue
                    other = cell.get((cx + dx, cy + dy), [])
                    for i in ids:
                        for j in other:
                            if j <= i and dx == 0 and dy == 0:
                                continue
                            a, b = self.balls[i], self.balls[j]
                            if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < 11 ** 2 and a[4] != b[4]:
                                if self.rng.random() < k:
                                    a[4] = b[4] = True
                                    self.burst(a[0], a[1], (255, 70, 90), 4, 140, 0.35)
                                    self.ev("hit", self.rng.random())
        self.p = min(0.999, sum(1 for b in self.balls if b[4]) / self.N)
        if self.p >= 0.9:
            self._sw = getattr(self, '_sw', 0) + 1
            if self._sw % 4 == 0:
                for b in self.balls:
                    if not b[4]:
                        b[4] = True
                        self.burst(b[0], b[1], (255, 70, 90), 4, 140, 0.35)
                        self.ev("hit", self.rng.random())
                        return
                self.p = 1.0

    def draw(self, d):
        d.rectangle((self.L, self.T, self.R, self.B), outline=(50, 90, 80), width=4)
        for b in self.balls:
            col = (255, 70, 90) if b[4] else (110, 230, 210)
            d.ellipse((b[0] - 8, b[1] - 8, b[0] + 8, b[1] + 8), fill=col)


# ---------------------------------------------------------------- 15 MERGE MANIA
class MergeMania(Sim):
    TITLE, SUB = "MERGE MANIA", "SAME COLOUR TOUCH  -  MERGE AND GROW"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 15, (255, 160, 90), "marimba", 247.0
    BG = (14, 10, 8)
    L, R, T, B = 80, 1000, 460, 1640
    COUNTER = "SCORE"
    TARGET = 1500

    def setup(self):
        self.balls = []
        self.score = 0
        self.acc_spawn = 0.0

    @staticmethod
    def rad(l):
        return 15 + l * 7.5

    def physics(self, dt):
        self.acc_spawn += clamp(2.5 * self.gain(), 0.8, 14) * dt
        if self.acc_spawn >= 1 and len(self.balls) < 90:
            self.acc_spawn -= 1
            self.balls.append([self.rng.uniform(self.L + 60, self.R - 60), self.T + 30, self.rng.uniform(-80, 80), 0.0, 0])
        for b in self.balls:
            b[3] += 900 * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            r = self.rad(b[4])
            if b[0] < self.L + r:
                b[0], b[2] = self.L + r, abs(b[2]) * 0.6
            if b[0] > self.R - r:
                b[0], b[2] = self.R - r, -abs(b[2]) * 0.6
            if b[1] > self.B - r:
                b[1], b[3] = self.B - r, -abs(b[3]) * 0.35
        gone, new = set(), []
        n = len(self.balls)
        for i in range(n):
            if i in gone:
                continue
            a = self.balls[i]
            for j in range(i + 1, n):
                if j in gone:
                    continue
                b = self.balls[j]
                dx, dy = b[0] - a[0], b[1] - a[1]
                ra, rb = self.rad(a[4]), self.rad(b[4])
                dd = math.hypot(dx, dy) or 0.01
                if dd < ra + rb:
                    if a[4] == b[4] and a[4] < 8:
                        gone.add(i)
                        gone.add(j)
                        lv = a[4] + 1
                        new.append([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.0, -150.0, lv])
                        self.score += 2 ** lv
                        self.p = min(1.0, self.score / self.TARGET)
                        self.burst((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, hsv(lv / 9), 10, 260)
                        self.ev("hit", lv / 9)
                        break
                    if a[4] == 8 and b[4] == 8:
                        pass
                    nx, ny = dx / dd, dy / dd
                    ov = (ra + rb - dd) / 2
                    a[0] -= nx * ov
                    a[1] -= ny * ov
                    b[0] += nx * ov
                    b[1] += ny * ov
                    rv = (b[2] - a[2]) * nx + (b[3] - a[3]) * ny
                    if rv < 0:
                        a[2] += nx * rv * 0.5
                        a[3] += ny * rv * 0.5
                        b[2] -= nx * rv * 0.5
                        b[3] -= ny * rv * 0.5
        self.balls = [b for k, b in enumerate(self.balls) if k not in gone] + new
        self.balls = [b for b in self.balls if b[4] < 8 or self.rng.random() > 0.002]

    def draw(self, d):
        d.rectangle((self.L, self.T, self.R, self.B), outline=(110, 80, 50), width=4)
        for b in self.balls:
            r = self.rad(b[4])
            d.ellipse((b[0] - r, b[1] - r, b[0] + r, b[1] + r), fill=hsv(b[4] / 9, 0.75, 1))
            if b[4] >= 1:
                ctext_small(d, str(2 ** b[4]), b[0], b[1], r)

    def stats(self):
        return [f"SCORE  {self.score}"]


def ctext_small(d, text, x, y, r):
    f = font(int(r * 0.9), ARIAL)
    w = d.textlength(text, font=f)
    d.text((x - w / 2, y - r * 0.55), text, font=f, fill=(20, 20, 20))


# ---------------------------------------------------------------- 16 SNOWBALL DOTS
class SnowballDots(Sim):
    TITLE, SUB = "SNOWBALL", "ROLL OVER DOTS  -  GET BIGGER"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 16, (150, 220, 255), "glass", 330.0
    BG = (8, 12, 20)
    L, R, T, B = 60, 1020, 420, 1680
    LIST, AIDX = "dots", 3
    HONEST = True
    COUNTER = "DOTS COLLECTED"

    def setup(self):
        self.dots = [[self.rng.uniform(self.L + 20, self.R - 20), self.rng.uniform(self.T + 20, self.B - 20), self.rng.random(), True] for _ in range(1000)]
        self.M, self.rem = len(self.dots), 0
        self.ball = [540.0, 1000.0, 300.0, 200.0]

    def rad(self):
        return 10 + 70 * self.p ** 0.8

    def physics(self, dt):
        b = self.ball
        r = self.rad()
        al = [q for q in self.dots if q[3]]
        ang = math.atan2(b[3], b[2])
        if al:
            q = nearest(al, b[0], b[1])
            want = math.atan2(q[1] - b[1], q[0] - b[0])
            diff = math.atan2(math.sin(want - ang), math.cos(want - ang))
            ang += max(-9.0 * dt, min(9.0 * dt, diff))
        b[2], b[3] = math.cos(ang) * 330, math.sin(ang) * 330
        b[0] += b[2] * dt
        b[1] += b[3] * dt
        if b[0] < self.L + r or b[0] > self.R - r:
            b[2] = -b[2]
            b[0] = clamp(b[0], self.L + r, self.R - r)
        if b[1] < self.T + r or b[1] > self.B - r:
            b[3] = -b[3]
            b[1] = clamp(b[1], self.T + r, self.B - r)
        for q in al:
            if (q[0] - b[0]) ** 2 + (q[1] - b[1]) ** 2 < (r + 6) ** 2:
                if True:
                    q[3] = False
                    self.rem += 1
                    self.burst(q[0], q[1], hsv(q[2]), 4, 160, 0.4)
                    self.ev("hit", q[2])

    def draw(self, d):
        d.rectangle((self.L, self.T, self.R, self.B), outline=(50, 80, 120), width=4)
        for q in self.dots:
            if q[3]:
                d.ellipse((q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6), fill=hsv(q[2], 0.6, 1))
        r = self.rad()
        d.ellipse((self.ball[0] - r, self.ball[1] - r, self.ball[0] + r, self.ball[1] + r), fill=(240, 248, 255))

    def stats(self):
        return [f"SIZE  {int(self.rad())}"]


# ---------------------------------------------------------------- 17 BUBBLE POP
class BubblePop(Sim):
    TITLE, SUB = "BUBBLE POP", "EVERY POP RELEASES A BOUNCING BALL"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 17, (130, 255, 230), "pop", 294.0
    BG = (6, 14, 18)
    L, R, T, B = 60, 1020, 420, 1680
    LIST, AIDX = "bub", 4
    HONEST = True
    COUNTER = "BUBBLES POPPED"

    def setup(self):
        self.bub = []
        for _ in range(130):
            self.bub.append([self.rng.uniform(self.L + 40, self.R - 40), self.rng.uniform(self.T + 40, self.B - 40), self.rng.uniform(16, 42), self.rng.random(), True, self.rng.uniform(0, 6.28)])
        self.M, self.rem = len(self.bub), 0
        self.balls = [[540, 1500, 200.0, -500.0] for _ in range(3)]

    def physics(self, dt):
        cap = int(6 + 1.5 * self.t)
        new = []
        for q in self.bub:
            q[5] += dt
            q[1] -= 6 * dt
            q[0] += math.sin(q[5] * 1.3) * 10 * dt
            if q[1] < self.T + q[2]:
                q[1] = self.B - q[2]
        for b in self.balls:
            b[3] += 500 * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < self.L + 7 or b[0] > self.R - 7:
                b[2] = -b[2]
                b[0] = clamp(b[0], self.L + 7, self.R - 7)
            if b[1] > self.B - 7:
                b[3] = -self.rng.uniform(850, 950)
                b[1] = self.B - 7
            if b[1] < self.T + 7:
                b[3] = abs(b[3])
            for q in self.bub:
                if q[4] and (q[0] - b[0]) ** 2 + (q[1] - b[1]) ** 2 < (q[2] + 7) ** 2:
                    if True:
                        q[4] = False
                        self.rem += 1
                        self.burst(q[0], q[1], hsv(q[3] * 0.3 + 0.4, 0.5), 10, 260, 0.5)
                        self.ev("hit", q[2] / 42)
                        if len(self.balls) + len(new) < cap:
                            new.append([q[0], q[1], self.rng.uniform(-300, 300), -300.0])
                    dx, dy = b[0] - q[0], b[1] - q[1]
                    dd = math.hypot(dx, dy) or 1
                    b[2], b[3] = reflect(b[2], b[3], dx / dd, dy / dd)
                    break
        self.balls += new

    def draw(self, d):
        d.rectangle((self.L, self.T, self.R, self.B), outline=(40, 100, 110), width=4)
        for q in self.bub:
            if q[4]:
                d.ellipse((q[0] - q[2], q[1] - q[2], q[0] + q[2], q[1] + q[2]), outline=hsv(q[3] * 0.3 + 0.4, 0.5, 1), width=4)
                d.ellipse((q[0] - q[2] * 0.5, q[1] - q[2] * 0.6, q[0] - q[2] * 0.2, q[1] - q[2] * 0.3), fill=(220, 255, 255))
        for b in self.balls:
            d.ellipse((b[0] - 7, b[1] - 7, b[0] + 7, b[1] + 7), fill=(255, 255, 255))

    def stats(self):
        return [f"BALLS  {len(self.balls)}"]


# ---------------------------------------------------------------- 18 GRAVITY WELLS
class GravityWells(Sim):
    TITLE, SUB = "GRAVITY WELLS", "THREE WELLS  -  SWALLOW EVERY BALL"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 18, (180, 130, 255), "bell", 262.0
    BG = (8, 6, 14)
    CX, CY = 540, 1040
    COUNTER = "SWALLOWED"
    TARGET = 380
    SCALE = MAJOR

    def setup(self):
        self.balls, self.acc_spawn, self.sw = [], 0.0, 0

    def wells(self):
        t = self.t
        return [(540 + 300 * math.sin(t * 0.5 + k * 2.1), 1040 + 360 * math.cos(t * 0.37 + k * 2.1 * 1.3)) for k in range(3)]

    def physics(self, dt):
        self.acc_spawn += clamp(5 * self.gain(), 1, 30) * dt
        while self.acc_spawn >= 1 and len(self.balls) < 260:
            self.acc_spawn -= 1
            side = self.rng.random() < 0.5
            self.balls.append([60 if side else 1020, self.rng.uniform(450, 1650), (1 if side else -1) * self.rng.uniform(150, 350), self.rng.uniform(-200, 200), []])
        ws = self.wells()
        keep = []
        for b in self.balls:
            sw = False
            for (wx, wy) in ws:
                dx, dy = wx - b[0], wy - b[1]
                dd = math.hypot(dx, dy) or 1
                f = 1.6e6 / (dd * dd + 3000)
                b[2] += dx / dd * f * dt
                b[3] += dy / dd * f * dt
                if dd < 36:
                    sw = True
                    self.burst(b[0], b[1], (200, 160, 255), 5, 200, 0.4)
                    self.ev("hit", self.rng.random())
            sp = math.hypot(b[2], b[3])
            if sp > 1100:
                b[2], b[3] = b[2] * 1100 / sp, b[3] * 1100 / sp
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[4].append((b[0], b[1]))
            b[4] = b[4][-10:]
            if b[0] < 40 or b[0] > 1040:
                b[2] = -b[2]
                b[0] = clamp(b[0], 40, 1040)
            if b[1] < 420 or b[1] > 1680:
                b[3] = -b[3]
                b[1] = clamp(b[1], 420, 1680)
            if sw:
                self.sw += 1
                self.p = min(1.0, self.sw / self.TARGET)
                continue
            keep.append(b)
        self.balls = keep

    def draw(self, d):
        d.rectangle((40, 420, 1040, 1680), outline=(60, 40, 100), width=4)
        for (wx, wy) in self.wells():
            for k in range(4, 0, -1):
                r = 34 + k * 16
                d.ellipse((wx - r, wy - r, wx + r, wy + r), outline=(70 + k * 20, 40 + k * 10, 140 + k * 20), width=3)
            d.ellipse((wx - 28, wy - 28, wx + 28, wy + 28), fill=(0, 0, 0), outline=(200, 160, 255), width=4)
        for b in self.balls:
            for i, (x, y) in enumerate(b[4]):
                a = i / 10
                d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(int(110 * a), int(80 * a), int(200 * a)))
            d.ellipse((b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6), fill=(255, 255, 255))

    def stats(self):
        return [f"BALLS  {len(self.balls)}"]


# ---------------------------------------------------------------- 19 LASER GRID
class LaserGrid(Sim):
    TITLE, SUB = "LASER GRID", "CROSS A BEAM  -  SPLIT IN TWO"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 19, (255, 60, 90), "click", 392.0
    BG = (6, 6, 10)
    L, R, T, B = 60, 1020, 440, 1660
    COUNTER = "SPLITS"
    TARGET = 1100

    def setup(self):
        self.balls = [[540 + i * 20, 1000, self.rng.uniform(-300, 300), self.rng.uniform(-300, 300), 0, 0] for i in range(4)]
        self.sp = 0

    def beams(self):
        t = self.t
        h = self.T + (self.B - self.T) * (0.5 + 0.45 * math.sin(t * 0.8))
        v = self.L + (self.R - self.L) * (0.5 + 0.45 * math.sin(t * 0.55 + 1))
        return h, v

    def physics(self, dt):
        h0, v0 = self.beams()
        cap = 350
        new = []
        for b in self.balls:
            ox, oy = b[0], b[1]
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < self.L + 6 or b[0] > self.R - 6:
                b[2] = -b[2]
                b[0] = clamp(b[0], self.L + 6, self.R + -6)
            if b[1] < self.T + 6 or b[1] > self.B - 6:
                b[3] = -b[3]
                b[1] = clamp(b[1], self.T + 6, self.B - 6)
            b[5] = max(0, b[5] - dt)
            for kind, pos_old, pos_new, beam in (("h", oy, b[1], h0), ("v", ox, b[0], v0)):
                if b[5] == 0 and (pos_old - beam) * (pos_new - beam) <= 0:
                    b[5] = 0.12
                    self.add(0.0009)
                    self.ev("hit", self.rng.random())
                    self.burst(b[0], b[1], (255, 80, 110), 5, 200, 0.3)
                    if len(self.balls) + len(new) < cap:
                        a = self.rng.uniform(0, 6.28)
                        new.append([b[0], b[1], math.cos(a) * 330, math.sin(a) * 330, 0, 0.5])
        self.balls += new
        if len(self.balls) >= cap and len(self.balls) > 4:
            self.balls.pop(self.rng.randrange(len(self.balls)))

    def draw(self, d):
        d.rectangle((self.L, self.T, self.R, self.B), outline=(80, 40, 60), width=4)
        h, v = self.beams()
        d.line((self.L, h, self.R, h), fill=(255, 40, 80), width=7)
        d.line((v, self.T, v, self.B), fill=(255, 40, 80), width=7)
        d.line((self.L, h, self.R, h), fill=(255, 190, 200), width=2)
        d.line((v, self.T, v, self.B), fill=(255, 190, 200), width=2)
        for b in self.balls:
            d.ellipse((b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6), fill=(255, 255, 255))

    def stats(self):
        return [f"BALLS  {len(self.balls)}"]


# ---------------------------------------------------------------- 20 SPIROGRAPH
class Spirograph(Sim):
    TITLE, SUB = "SPIROGRAPH", "TWO SPINNING ARMS  -  ONE PERFECT PATTERN"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 20, (255, 120, 220), "glass", 330.0
    BG = (8, 6, 14)
    CX, CY = 540, 1040
    COUNTER = "PATTERN DRAWN"
    SCALE = MAJOR

    def setup(self):
        self.th = 0.0
        self.pts = []
        self.R1, self.R2 = 300.0, 190.0
        self.k = 7.0 / 3.0

    def pen(self, th):
        a = th
        b = th * (1 + self.k) * 1.0
        x = self.CX + self.R1 * math.cos(a) + self.R2 * math.cos(b) * 0.9
        y = self.CY + self.R1 * math.sin(a) + self.R2 * math.sin(b) * 0.9
        return x, y

    TH_MAX = 6 * math.pi * 3

    def physics(self, dt):
        if self.done_at is None:
            step = dt * clamp(self.gain(), 0.2, 6) * (self.TH_MAX / self.T_END) * 1.0
            n = 3
            for i in range(n):
                self.th += step / n
                self.pts.append(self.pen(self.th))
                if len(self.pts) % 40 == 0:
                    self.ev("hit", (self.th / 0.7) % 1)
            self.p = min(1.0, self.th / self.TH_MAX)

    def draw(self, d):
        n = len(self.pts)
        for i in range(1, n, 1):
            if i % 2:
                pass
            d.line((self.pts[i - 1], self.pts[i]), fill=hsv(i / 900, 0.7, 1), width=3)
        a = self.th
        b = self.th * (1 + self.k)
        p1 = (self.CX + self.R1 * math.cos(a), self.CY + self.R1 * math.sin(a))
        d.line((self.CX, self.CY, *p1), fill=(110, 110, 150), width=4)
        if self.pts:
            d.line((*p1, *self.pts[-1]), fill=(110, 110, 150), width=4)
            x, y = self.pts[-1]
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(255, 255, 255))
        d.ellipse((p1[0] - 8, p1[1] - 8, p1[0] + 8, p1[1] + 8), fill=(200, 200, 255))


# ---------------------------------------------------------------- 21 XYLOPHONE DROP
class XyloDrop(Sim):
    TITLE, SUB = "XYLOPHONE DROP", "BALLS BOUNCE OUT A MELODY"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 21, (255, 190, 90), "marimba", 262.0
    BG = (14, 10, 6)
    COUNTER = "NOTES PLAYED"
    TARGET = 9000
    SCALE = MAJOR

    def setup(self):
        self.bars = [(80 + i * 90, 520 + i * 96, 150) for i in range(10)]
        self.bars += [(850 - i * 90, 600 + i * 96, 150) for i in range(9)]
        self.balls, self.acc_spawn, self.hits = [], 0.0, 0

    def physics(self, dt):
        self.acc_spawn += clamp(4 * self.gain(), 1, 28) * dt
        while self.acc_spawn >= 1 and len(self.balls) < 120:
            self.acc_spawn -= 1
            self.balls.append([self.rng.uniform(80, 1000), 440, self.rng.uniform(-60, 60), 0.0])
        keep = []
        for b in self.balls:
            b[3] += 1500 * dt
            ox, oy = b[0], b[1]
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < 50 or b[0] > 1030:
                b[2] = -b[2]
                b[0] = clamp(b[0], 50, 1030)
            for i, (x, y, w) in enumerate(self.bars):
                if b[3] > 0 and x <= b[0] <= x + w and oy <= y <= b[1] + 9:
                    b[1] = y - 9
                    b[3] = -b[3] * 0.82
                    b[2] = clamp(b[2] + self.rng.uniform(-80, 80), -350, 350)
                    self.hits += 1
                    self.p = min(1.0, self.hits / self.TARGET)
                    self.ev("hit", i / 19)
                    break
            if b[1] > 1760:
                continue
            keep.append(b)
        self.balls = keep

    def draw(self, d):
        for i, (x, y, w) in enumerate(self.bars):
            d.rounded_rectangle((x, y, x + w, y + 18), radius=7, fill=hsv(i / 19 * 0.85, 0.75, 1))
        for b in self.balls:
            d.ellipse((b[0] - 9, b[1] - 9, b[0] + 9, b[1] + 9), fill=(255, 255, 255))

    def stats(self):
        return [f"NOTES  {self.hits}"]


BATCH_B = [FourKingdoms, Contagion, MergeMania, SnowballDots, BubblePop, GravityWells, LaserGrid, Spirograph, XyloDrop]
