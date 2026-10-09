"""ASMR batch A: nine rule sets."""
import math
from core import *


def nearest(items, x, y, key=lambda it: (it[0], it[1])):
    best, bd = None, 1e18
    for it in items:
        px, py = key(it)
        dd = (px - x) ** 2 + (py - y) ** 2
        if dd < bd:
            best, bd = it, dd
    return best


# ---------------------------------------------------------------- 04 BRICK RAIN
class BrickRain(Sim):
    TITLE, SUB = "BRICK RAIN", "FALLING BALLS  -  EVERY BREAK CLONES"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 4, (255, 170, 80), "marimba", 262.0
    BG = (14, 9, 8)
    LIST, AIDX = "bricks", 3
    HONEST = True
    COUNTER = "BRICKS BROKEN"
    L, R, T, B = 60, 1020, 400, 1640

    def setup(self):
        self.bricks = []
        for r in range(12):
            for c in range(12):
                self.bricks.append([90 + c * 75, 430 + r * 40, r, True])
        self.M, self.rem = len(self.bricks), 0
        self.balls = [[540 + i * 60, 1100, self.rng.uniform(-250, 250), -200] for i in range(2)]

    def physics(self, dt):
        cap = int(2 + 0.05 * self.t)
        new = []
        for b in self.balls:
            b[3] += 600 * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < self.L + 7 or b[0] > self.R - 7:
                b[2] = -b[2]
                b[0] = max(self.L + 7, min(self.R - 7, b[0]))
            if b[1] > self.B - 7:
                b[3] = -self.rng.uniform(1230, 1300)
                b[1] = self.B - 7
            if b[1] < self.T:
                b[3] = abs(b[3])
            for br in self.bricks:
                if not br[3]:
                    continue
                if br[0] - 7 < b[0] < br[0] + 71 and br[1] - 7 < b[1] < br[1] + 37:
                    cx, cy = br[0] + 36, br[1] + 18
                    if abs(b[0] - cx) / 43 > abs(b[1] - cy) / 25:
                        b[2] = -b[2]
                    else:
                        b[3] = -b[3]
                    if True:
                        br[3] = False
                        self.rem += 1
                        self.burst(cx, cy, hsv(br[2] / 12), 7)
                        self.ev("hit", (br[0] - 90) / 900)
                        if len(self.balls) + len(new) < cap and self.rng.random() < 0.1:
                            new.append([b[0], b[1], -b[2] + self.rng.uniform(-80, 80), b[3]])
                    break
        self.balls += new

    def draw(self, d):
        d.rectangle((self.L, self.T, self.R, self.B), outline=(80, 60, 50), width=4)
        for br in self.bricks:
            if br[3]:
                d.rounded_rectangle((br[0], br[1], br[0] + 71, br[1] + 35), radius=6, fill=hsv(br[2] / 12 * 0.9, 0.7, 0.95))
        for b in self.balls:
            d.ellipse((b[0] - 7, b[1] - 7, b[0] + 7, b[1] + 7), fill=(255, 255, 255))

    def stats(self):
        return [f"BALLS  {len(self.balls)}"]


# ---------------------------------------------------------------- 05 SPIRAL SIEGE
class SpiralSiege(Sim):
    TITLE, SUB = "SPIRAL SIEGE", "ONE BALL  -  IT GROWS WITH EVERY BLOCK"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 66, 5, (120, 255, 190), "bell", 330.0
    BG = (6, 14, 14)
    SCALE = MAJOR
    CX, CY, R = 540, 1010, 480
    LIST, AIDX = "blocks", 3
    HONEST = True
    COUNTER = "BLOCKS EATEN"

    def setup(self):
        self.blocks = []
        n = 420
        for i in range(n):
            a = i * 0.43
            r = 46 + i * 1.0
            self.blocks.append([self.CX + math.cos(a) * r, self.CY + math.sin(a) * r, i / n, True])
        self.M, self.rem = n, 0
        self.ball = [self.CX + 150, self.CY - 100, 330.0, 380.0]
        self.trail = []

    def rad(self):
        return 9 + 54 * self.p

    def physics(self, dt):
        b, r = self.ball, self.rad()
        al = [q for q in self.blocks if q[3]]
        ang = math.atan2(b[3], b[2])
        if al:
            q = nearest(al, b[0], b[1])
            want = math.atan2(q[1] - b[1], q[0] - b[0])
            diff = math.atan2(math.sin(want - ang), math.cos(want - ang))
            ang += max(-4.0 * dt, min(4.0 * dt, diff))
        b[2], b[3] = math.cos(ang) * 250, math.sin(ang) * 250
        b[0] += b[2] * dt
        b[1] += b[3] * dt
        dx, dy = b[0] - self.CX, b[1] - self.CY
        dist = math.hypot(dx, dy)
        if dist + r > self.R:
            nx, ny = dx / dist, dy / dist
            b[2], b[3] = reflect(b[2], b[3], nx, ny)
            b[0] = self.CX + nx * (self.R - r - 1)
            b[1] = self.CY + ny * (self.R - r - 1)
            self.ev("hit", 0.1)
        for bl in self.blocks:
            if bl[3] and (bl[0] - b[0]) ** 2 + (bl[1] - b[1]) ** 2 < (r + 11) ** 2:
                if True:
                    bl[3] = False
                    self.rem += 1
                    self.burst(bl[0], bl[1], hsv(bl[2]), 6)
                    self.ev("hit", bl[2])
        self.trail.append((b[0], b[1]))
        self.trail = self.trail[-26:]

    def draw(self, d):
        d.ellipse((self.CX - self.R, self.CY - self.R, self.CX + self.R, self.CY + self.R), outline=(40, 90, 90), width=4)
        for bl in self.blocks:
            if bl[3]:
                d.ellipse((bl[0] - 10, bl[1] - 10, bl[0] + 10, bl[1] + 10), fill=hsv(bl[2] * 0.85, 0.75, 1))
        for i, (x, y) in enumerate(self.trail):
            a = i / len(self.trail)
            rr = self.rad() * (0.3 + 0.7 * a)
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(int(255 * a * .5), int(255 * a * .5), int(255 * a * .5)))
        r = self.rad()
        d.ellipse((self.ball[0] - r, self.ball[1] - r, self.ball[0] + r, self.ball[1] + r), fill=(255, 255, 255))

    def stats(self):
        return [f"BALL SIZE  {int(self.rad())}"]


# ---------------------------------------------------------------- 06 HEX HIVE
class HexHive(Sim):
    TITLE, SUB = "HEX HIVE", "EVERY CELL EATEN  -  THE BALLS GO FASTER"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 68, 6, (255, 200, 60), "glass", 247.0
    BG = (16, 12, 4)
    CX, CY, R = 540, 1010, 470
    LIST, AIDX = "cells", 3
    HONEST = True
    COUNTER = "CELLS CLEARED"

    def setup(self):
        s = 24
        self.cells = []
        for q in range(-20, 21):
            for r in range(-20, 21):
                x = self.CX + s * 1.5 * q
                y = self.CY + s * math.sqrt(3) * (r + q / 2)
                if math.hypot(x - self.CX, y - self.CY) < self.R - 30:
                    self.cells.append([x, y, math.hypot(x - self.CX, y - self.CY) / self.R, True])
        self.s, self.M, self.rem = s, len(self.cells), 0
        self.balls = []
        for i in range(2):
            a = self.rng.uniform(0, 6.28)
            self.balls.append([self.CX + math.cos(a) * 300, self.CY + math.sin(a) * 300, a + 1.0])

    def speed(self):
        return 260 + 300 * self.p

    def physics(self, dt):
        sp = self.speed()
        alive = [c for c in self.cells if c[3]]
        for b in self.balls:
            if alive and self.rng.random() < 0.08:
                c = nearest(alive, b[0], b[1])
                want = math.atan2(c[1] - b[1], c[0] - b[0])
                b[2] += (math.atan2(math.sin(want - b[2]), math.cos(want - b[2]))) * 0.25
            vx, vy = math.cos(b[2]) * sp, math.sin(b[2]) * sp
            b[0] += vx * dt
            b[1] += vy * dt
            dx, dy = b[0] - self.CX, b[1] - self.CY
            dist = math.hypot(dx, dy)
            if dist > self.R - 8:
                nx, ny = dx / dist, dy / dist
                vx, vy = reflect(vx, vy, nx, ny)
                b[2] = math.atan2(vy, vx)
                b[0], b[1] = self.CX + nx * (self.R - 9), self.CY + ny * (self.R - 9)
                self.ev("hit", 0.9)
            for c in self.cells:
                if c[3] and (c[0] - b[0]) ** 2 + (c[1] - b[1]) ** 2 < (self.s * 0.8) ** 2:
                    if True:
                        c[3] = False
                        self.rem += 1
                        self.burst(c[0], c[1], (255, 220, 100), 5)
                        self.ev("hit", c[2])
                        b[2] += math.pi + self.rng.uniform(-0.6, 0.6)
                    break

    def draw(self, d):
        d.ellipse((self.CX - self.R, self.CY - self.R, self.CX + self.R, self.CY + self.R), outline=(120, 90, 30), width=4)
        s = self.s - 3
        for c in self.cells:
            if c[3]:
                pts = [(c[0] + s * math.cos(math.pi / 3 * k), c[1] + s * math.sin(math.pi / 3 * k)) for k in range(6)]
                d.polygon(pts, fill=(int(255 - 90 * c[2]), int(190 - 80 * c[2]), int(40 + 20 * c[2])))
        for b in self.balls:
            d.ellipse((b[0] - 9, b[1] - 9, b[0] + 9, b[1] + 9), fill=(255, 255, 255))

    def stats(self):
        return [f"SPEED  x{self.speed() / 280:.1f}"]


# ---------------------------------------------------------------- 07 ORBIT EATER
class OrbitEater(Sim):
    TITLE, SUB = "ORBIT EATER", "BALLS CIRCLE THE STAR  -  EAT TO MULTIPLY"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 70, 7, (200, 140, 255), "glass", 294.0
    BG = (8, 6, 16)
    CX, CY = 540, 1010
    LIST, AIDX = "dots", 3
    HONEST = True
    COUNTER = "STARDUST EATEN"

    def setup(self):
        self.dots = []
        for i in range(620):
            a = self.rng.uniform(0, 6.283)
            r = self.rng.uniform(70, 460)
            self.dots.append([self.CX + math.cos(a) * r, self.CY + math.sin(a) * r, r / 460, True])
        self.M, self.rem = len(self.dots), 0
        self.balls = []
        for i in range(4):
            a = i * 1.57
            r = 150 + i * 70
            self.balls.append([self.CX + math.cos(a) * r, self.CY + math.sin(a) * r, -math.sin(a) * 430, math.cos(a) * 430, []])

    def physics(self, dt):
        cap = int(4 + 0.3 * self.t)
        new = []
        for b in self.balls:
            dx, dy = b[0] - self.CX, b[1] - self.CY
            b[2] -= 1.6 * dx * dt
            b[3] -= 1.6 * dy * dt
            al = [q for q in self.dots if q[3]]
            if al:
                q = nearest(al, b[0], b[1])
                ddx, ddy = q[0] - b[0], q[1] - b[1]
                dd = math.hypot(ddx, ddy) or 1
                b[2] += ddx / dd * 300 * dt
                b[3] += ddy / dd * 300 * dt
            sp_ = math.hypot(b[2], b[3])
            if sp_ > 400:
                b[2], b[3] = b[2] * 400 / sp_, b[3] * 400 / sp_
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[4].append((b[0], b[1]))
            b[4] = b[4][-22:]
            for dt_ in self.dots:
                if dt_[3] and (dt_[0] - b[0]) ** 2 + (dt_[1] - b[1]) ** 2 < 24 ** 2:
                    if True:
                        dt_[3] = False
                        self.rem += 1
                        self.burst(dt_[0], dt_[1], (230, 200, 255), 6)
                        self.ev("hit", dt_[2])
                        if len(self.balls) + len(new) < cap and self.rng.random() < 0.2:
                            new.append([b[0], b[1], -b[2] * 0.8 + 40, -b[3] * 0.8, []])
                    break
        self.balls += new

    def draw(self, d):
        d.ellipse((self.CX - 38, self.CY - 38, self.CX + 38, self.CY + 38), fill=(255, 220, 120))
        for dt_ in self.dots:
            if dt_[3]:
                d.ellipse((dt_[0] - 5, dt_[1] - 5, dt_[0] + 5, dt_[1] + 5), fill=hsv(0.72 + dt_[2] * 0.2, 0.5, 1))
        for b in self.balls:
            for i, (x, y) in enumerate(b[4]):
                a = i / max(1, len(b[4]))
                d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(int(120 * a), int(90 * a), int(255 * a)))
            d.ellipse((b[0] - 8, b[1] - 8, b[0] + 8, b[1] + 8), fill=(255, 255, 255))

    def stats(self):
        return [f"BALLS  {len(self.balls)}"]


# ---------------------------------------------------------------- 08 CANNON WALL
class CannonWall(Sim):
    TITLE, SUB = "CANNON WALL", "A SWEEPING CANNON  -  FIRE RATE KEEPS RISING"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 68, 8, (255, 90, 120), "pop", 220.0
    BG = (14, 6, 10)
    L, R, T = 60, 1020, 400
    LIST, AIDX = "bricks", 3
    HONEST = True
    COUNTER = "WALL DESTROYED"

    def setup(self):
        self.bricks = []
        for r in range(10):
            for c in range(14):
                self.bricks.append([75 + c * 67, 430 + r * 40, r, True])
        self.M, self.rem = len(self.bricks), 0
        self.balls, self.cool = [], 0.0

    def physics(self, dt):
        ang = math.sin(self.t * 0.9) * 1.0
        rate = 0.9 + 0.9 * self.p
        self.cool -= dt
        if self.cool <= 0 and len(self.balls) < 420:
            self.cool = 1.0 / rate
            self.balls.append([540, 1590, math.sin(ang) * 820, -math.cos(ang) * 820])
            self.ev("hit", 0.05)
        keep = []
        for b in self.balls:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < self.L + 7 or b[0] > self.R - 7:
                b[2] = -b[2]
            if b[1] < self.T:
                b[3] = abs(b[3])
            if b[1] > 1700:
                continue
            for br in self.bricks:
                if br[3] and br[0] - 7 < b[0] < br[0] + 62 and br[1] - 7 < b[1] < br[1] + 37:
                    if abs(b[0] - br[0] - 31) / 38 > abs(b[1] - br[1] - 18) / 25:
                        b[2] = -b[2]
                    else:
                        b[3] = -b[3]
                    if True:
                        br[3] = False
                        self.rem += 1
                        self.burst(br[0] + 31, br[1] + 18, hsv(0.95 - br[2] * 0.05, 0.8, 1), 6)
                        self.ev("hit", br[2] / 8 + self.rng.random() * 0.1)
                    break
            keep.append(b)
        self.balls = keep

    def draw(self, d):
        d.line((self.L, self.T, self.L, 1700), fill=(90, 40, 60), width=4)
        d.line((self.R, self.T, self.R, 1700), fill=(90, 40, 60), width=4)
        for br in self.bricks:
            if br[3]:
                d.rounded_rectangle((br[0], br[1], br[0] + 62, br[1] + 35), radius=6, fill=hsv(0.95 - br[2] * 0.05, 0.75, 1))
        ang = math.sin(self.t * 0.9) * 1.0
        x1, y1 = 540 + math.sin(ang) * 60, 1590 - math.cos(ang) * 60
        d.line((540, 1590, x1, y1), fill=(255, 255, 255), width=22)
        d.ellipse((510, 1560, 570, 1620), fill=(70, 70, 90))
        for b in self.balls:
            d.ellipse((b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6), fill=(255, 235, 240))

    def stats(self):
        return [f"FIRE RATE  {0.9 + 0.9 * self.p:.1f}/s"]


# ---------------------------------------------------------------- 09 TRIANGLE TRAP
class TriangleTrap(Sim):
    TITLE, SUB = "TRIANGLE TRAP", "BOUNCE = CLONE  -  ESCAPE THROUGH THE GAP"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 9, (255, 120, 220), "pluck", 262.0
    BG = (12, 6, 16)
    CX, CY, R = 540, 1060, 520
    TARGET = 900
    COUNTER = "ESCAPED"

    def setup(self):
        self.balls = [[self.CX + 30 * i - 30, self.CY - 80 + 20 * i, 120 * (i - 1), 60.0, 0] for i in range(3)]
        self.esc = 0
        self.theta = 0.0

    def gapw(self):
        return min(0.9, 0.05 * self.gain()) if self.t > 4 else 0.0

    def physics(self, dt):
        self.theta += (0.8 + 0.8 * self.p) * dt
        ap = self.R / 2
        new, keep = [], []
        for b in self.balls:
            b[3] += 750 * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            px, py = b[0] - self.CX, b[1] - self.CY
            inside = True
            out = False
            for k in range(3):
                na = self.theta + 2 * math.pi * (k + 0.5) / 3
                nx, ny = math.cos(na), math.sin(na)
                dist = px * nx + py * ny
                if dist > ap - 8:
                    s = -px * ny + py * nx
                    if k == 0 and abs(s) < self.gapw() * self.R * 0.866:
                        out = True
                    elif b[4] == 0:
                        b[2], b[3] = reflect(b[2], b[3], nx, ny)
                        b[0] -= nx * (dist - ap + 9)
                        b[1] -= ny * (dist - ap + 9)
                        sp = math.hypot(b[2], b[3])
                        if sp < 420:
                            b[2], b[3] = b[2] * 420 / sp, b[3] * 420 / sp
                        elif sp > 900:
                            b[2], b[3] = b[2] * 900 / sp, b[3] * 900 / sp
                        self.ev("hit", self.rng.random())
                        if len(self.balls) + len(new) < 900 and self.rng.random() < 0.5:
                            a2 = math.atan2(b[3], b[2]) + self.rng.uniform(-0.7, 0.7)
                            new.append([b[0], b[1], math.cos(a2) * 450, math.sin(a2) * 450, 0])
            if out:
                b[4] = 1
            if b[4] and math.hypot(px, py) > self.R * 0.75:
                self.esc += 1
                self.p = min(1.0, self.esc / self.TARGET)
                self.ev("special", 0.5)
                continue
            if b[1] > H:
                continue
            keep.append(b)
        self.balls = keep + new
        if not self.balls:
            self.balls = [[self.CX, self.CY - 100, 100.0, 0.0, 0]]

    def draw(self, d):
        ap = self.R / 2
        for k in range(3):
            a0 = self.theta + 2 * math.pi * k / 3
            a1 = self.theta + 2 * math.pi * (k + 1) / 3
            p0 = (self.CX + math.cos(a0) * self.R, self.CY + math.sin(a0) * self.R)
            p1 = (self.CX + math.cos(a1) * self.R, self.CY + math.sin(a1) * self.R)
            if k == 1:  # edge 0 is between vertices k=... draw gap on edge facing normal angle theta+pi/3
                pass
            d.line((p0, p1), fill=(255, 120, 220), width=12)
        # carve the gap visually on edge 0
        na = self.theta + math.pi / 3
        nx, ny = math.cos(na), math.sin(na)
        tx, ty = -ny, nx
        mx, my = self.CX + nx * ap, self.CY + ny * ap
        gw = self.gapw() * self.R * 0.866
        d.line((mx - tx * gw, my - ty * gw, mx + tx * gw, my + ty * gw), fill=self.BG, width=18)
        d.ellipse((mx - 9, my - 9, mx + 9, my + 9), fill=(120, 255, 190))
        for b in self.balls:
            d.ellipse((b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6), fill=(120, 255, 190) if b[4] else (255, 255, 255))

    def stats(self):
        return [f"ESCAPED  {self.esc}   BALLS  {len(self.balls)}"]


# ---------------------------------------------------------------- 10 PLINKO RAIN
class PlinkoRain(Sim):
    TITLE, SUB = "PLINKO RAIN", "DROP  -  BOUNCE  -  PILE UP"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 66, 10, (90, 230, 255), "marimba", 247.0
    BG = (6, 10, 18)
    COUNTER = "BALLS LANDED"
    TARGET = 1100
    SCALE = MAJOR

    def setup(self):
        self.pegs = []
        for r in range(11):
            n = 10 if r % 2 == 0 else 9
            for c in range(n):
                self.pegs.append((90 + c * 100 + (0 if r % 2 == 0 else 50), 520 + r * 78))
        self.balls, self.bins, self.acc_spawn, self.landed = [], [0] * 10, 0.0, 0

    def physics(self, dt):
        rate = 14 * self.gain()
        self.acc_spawn += rate * dt
        while self.acc_spawn >= 1 and len(self.balls) < 900:
            self.acc_spawn -= 1
            self.balls.append([540 + self.rng.uniform(-60, 60), 440, self.rng.uniform(-60, 60), 0])
        keep = []
        for b in self.balls:
            b[3] += 1300 * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < 60 or b[0] > 1020:
                b[2] = -b[2] * 0.7
                b[0] = max(60, min(1020, b[0]))
            for (px, py) in self.pegs:
                dx, dy = b[0] - px, b[1] - py
                if abs(dy) < 22 and abs(dx) < 22 and dx * dx + dy * dy < 22 * 22:
                    d = math.hypot(dx, dy) or 1
                    nx, ny = dx / d, dy / d
                    b[2], b[3] = reflect(b[2], b[3], nx, ny)
                    b[2] *= 0.72
                    b[3] *= 0.72
                    b[0], b[1] = px + nx * 23, py + ny * 23
                    self.ev("hit", (py - 520) / 780 * 0.5 + self.rng.random() * 0.5)
                    break
            if b[1] > 1380:
                i = min(9, max(0, int((b[0] - 60) / 96)))
                self.bins[i] += 1
                self.landed += 1
                self.p = min(1.0, self.landed / self.TARGET)
                self.ev("special", i / 10)
                continue
            keep.append(b)
        self.balls = keep

    def draw(self, d):
        for (px, py) in self.pegs:
            d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=(70, 120, 160))
        mx = max(self.bins) or 1
        for i, v in enumerate(self.bins):
            x0 = 60 + i * 96
            h = 230 * v / max(mx, 60)
            d.rectangle((x0 + 4, 1640 - h, x0 + 92, 1640), fill=hsv(0.5 + i * 0.04, 0.7, 1))
            d.line((x0, 1380, x0, 1640), fill=(60, 80, 110), width=3)
        for b in self.balls:
            d.ellipse((b[0] - 8, b[1] - 8, b[0] + 8, b[1] + 8), fill=(255, 255, 255))

    def stats(self):
        return [f"LANDED  {self.landed}"]


# ---------------------------------------------------------------- 11 GEAR GATES
class GearGates(Sim):
    TITLE, SUB = "GEAR GATES", "BALLS FALL INWARD  -  FIND EVERY GAP"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 68, 11, (255, 210, 90), "click", 330.0
    BG = (12, 11, 6)
    CX, CY = 540, 1010
    RINGS = [150, 235, 320, 405, 480]
    COUNTER = "REACHED THE CORE"
    TARGET = 300

    def setup(self):
        self.balls = []
        self.acc_spawn = 0.0
        self.core = 0

    def gap_w(self):
        return min(1.3, 0.22 * self.gain())

    def ring_ang(self, k):
        return self.t * (0.5 + 0.25 * k) * (1 if k % 2 == 0 else -1)

    def in_gap(self, k, ang):
        g = self.gap_w()
        for j in range(2):
            c = self.ring_ang(k) + j * math.pi
            if abs((ang - c + math.pi) % (2 * math.pi) - math.pi) < g / 2:
                return True
        return False

    def physics(self, dt):
        self.acc_spawn += (7 + 8 * self.p) * dt
        while self.acc_spawn >= 1 and len(self.balls) < 500:
            self.acc_spawn -= 1
            a = self.rng.uniform(0, 6.283)
            self.balls.append([self.CX + math.cos(a) * 470, self.CY + math.sin(a) * 470, -math.cos(a) * 160, -math.sin(a) * 160])
        keep = []
        for b in self.balls:
            dx, dy = b[0] - self.CX, b[1] - self.CY
            d0 = math.hypot(dx, dy)
            b[2] -= dx / max(d0, 1) * 300 * dt
            b[3] -= dy / max(d0, 1) * 300 * dt
            ox, oy = b[0], b[1]
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            dx, dy = b[0] - self.CX, b[1] - self.CY
            d1 = math.hypot(dx, dy)
            if d1 < 34:
                self.core += 1
                self.p = min(1.0, self.core / self.TARGET)
                self.ev("special", self.rng.random())
                continue
            for k, R in enumerate(self.RINGS):
                if (d0 - R) * (d1 - R) < 0:
                    ang = math.atan2(dy, dx) % (2 * math.pi)
                    if not self.in_gap(k, ang):
                        nx, ny = dx / d1, dy / d1
                        b[2], b[3] = reflect(b[2], b[3], nx, ny)
                        b[0], b[1] = ox, oy
                        self.ev("hit", k / 5 + self.rng.random() * 0.1)
                        break
            keep.append(b)
        self.balls = keep

    def draw(self, d):
        d.ellipse((self.CX - 34, self.CY - 34, self.CX + 34, self.CY + 34), fill=(255, 210, 90))
        for k, R in enumerate(self.RINGS):
            for seg in range(90):
                a = seg / 90 * 2 * math.pi
                if self.in_gap(k, a + 0.03):
                    continue
                a2 = (seg + 1) / 90 * 2 * math.pi
                d.line((self.CX + math.cos(a) * R, self.CY + math.sin(a) * R, self.CX + math.cos(a2) * R, self.CY + math.sin(a2) * R),
                       fill=hsv(0.1 + k * 0.03, 0.7, 1), width=9)
        for b in self.balls:
            d.ellipse((b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6), fill=(255, 255, 255))

    def stats(self):
        return [f"CORE  {self.core}   BALLS  {len(self.balls)}"]


# ---------------------------------------------------------------- 12 PIXEL PAINTER
class PixelPainter(Sim):
    TITLE, SUB = "PIXEL PAINTER", "BOUNCING BALLS PAINT A HIDDEN PICTURE"
    T_END, SEED, ACC, SOUND, BASE_NOTE = 72, 12, (255, 255, 255), "glass", 262.0
    BG = (10, 10, 12)
    N, S, OX, OY = 36, 26, 72, 440
    COUNTER = "CANVAS PAINTED"
    TIMESCALE = True
    SCALE = MAJOR

    def setup(self):
        N = self.N
        self.col = [[None] * N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                x, y = (c + 0.5 - N / 2) / (N / 2), (r + 0.5 - N / 2) / (N / 2)
                rad = math.hypot(x, y)
                ang = math.atan2(y, x)
                hue = ang / (2 * math.pi) + 0.3 * math.sin(rad * 7)
                val = 1.0 if rad < 1.0 else 0.35
                self.col[r][c] = hsv(hue, 0.8 if rad < 1.0 else 0.4, val * (0.55 + 0.45 * math.cos(rad * 9) ** 2))
        self.painted = [[False] * N for _ in range(N)]
        self.count = 0
        self.balls = []
        for i in range(3):
            a = self.rng.uniform(0, 6.28)
            self.balls.append([self.rng.uniform(150, 900), self.rng.uniform(550, 1300), math.cos(a) * 500, math.sin(a) * 500])

    def physics(self, dt):
        N, S = self.N, self.S
        k = max(0.25, min(1.0, 0.2 * self.gain()))
        if self.t > self.T_END * 0.96:
            k = 1.0
        for b in self.balls:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            if b[0] < self.OX + 8 or b[0] > self.OX + N * S - 8:
                b[2] = -b[2]
                b[0] = max(self.OX + 8, min(self.OX + N * S - 8, b[0]))
            if b[1] < self.OY + 8 or b[1] > self.OY + N * S - 8:
                b[3] = -b[3]
                b[1] = max(self.OY + 8, min(self.OY + N * S - 8, b[1]))
            c, r = int((b[0] - self.OX) // S), int((b[1] - self.OY) // S)
            if 0 <= c < N and 0 <= r < N and not self.painted[r][c]:
                self.painted[r][c] = True
                self.count += 1
                self.burst(b[0], b[1], self.col[r][c], 3, 120, 0.3)
                self.ev("hit", self.rng.random())
        self.p = min(0.999, self.count / (N * N))
        if self.count >= 0.92 * N * N:
            self._sw = getattr(self, '_sw', 0) + 1
            if self._sw % 3 == 0:
                for r in range(N):
                    for c in range(N):
                        if not self.painted[r][c]:
                            self.painted[r][c] = True
                            self.count += 1
                            self.burst(self.OX + c * S + S / 2, self.OY + r * S + S / 2, self.col[r][c], 4, 140, 0.35)
                            self.ev("hit", self.rng.random())
                            return
                    else:
                        continue
                self.p = 1.0

    def draw(self, d):
        N, S = self.N, self.S
        d.rectangle((self.OX - 4, self.OY - 4, self.OX + N * S + 4, self.OY + N * S + 4), outline=(70, 70, 80), width=4)
        for r in range(N):
            for c in range(N):
                x, y = self.OX + c * S, self.OY + r * S
                if self.painted[r][c]:
                    d.rectangle((x, y, x + S - 1, y + S - 1), fill=self.col[r][c])
                else:
                    d.rectangle((x, y, x + S - 1, y + S - 1), fill=(22, 22, 28))
        for b in self.balls:
            d.ellipse((b[0] - 10, b[1] - 10, b[0] + 10, b[1] + 10), fill=(255, 255, 255), outline=(0, 0, 0), width=3)


BATCH_A = [BrickRain, SpiralSiege, HexHive, OrbitEater, CannonWall, TriangleTrap, PlinkoRain, GearGates, PixelPainter]
