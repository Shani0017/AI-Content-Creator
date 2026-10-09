"""Batch 2 - generative art (9), sorting visualisers (4), chain reactions (3), physics toys (4)."""
import cmath, heapq, math
from PIL import Image, ImageDraw
from core import *
from eater import clamp


# ================================================================== ART BASE (time-driven, exact length)
class Art(Sim):
    TS = False
    T_END = 66
    WIDTH = 3
    BEATS = 260
    CX, CY = 540, 1050

    def setup(self):
        self.canvas = Image.new("RGB", (W, H), self.BG)
        self.cd = ImageDraw.Draw(self.canvas)
        self.s = 0.0
        self.last = None
        self.nb = 0
        self.init()

    def init(self):
        pass

    def pos(self, s):
        return (self.CX, self.CY)

    def color(self, s):
        return hsv(s * 1.5, 0.65, 1.0)

    def seg(self, a, b, s):
        self.cd.line((a, b), fill=self.color(s), width=self.WIDTH)

    def physics(self, dt):
        if self.done_at is not None:
            return
        s1 = min(1.0, self.t / self.T_END)
        s0 = self.s
        n = 4
        for k in range(1, n + 1):
            q = s0 + (s1 - s0) * k / n
            pnt = self.pos(q)
            if self.last is not None:
                self.seg(self.last, pnt, q)
            self.last = pnt
        self.s = s1
        self.p = s1
        nb = int(s1 * self.BEATS)
        while self.nb < nb:
            self.nb += 1
            self.beat(self.nb)

    def beat(self, i):
        x, y = self.last
        self.ev("hit", clamp((math.atan2(y - self.CY, x - self.CX) / (2 * math.pi)) % 1.0, 0, 1))

    def overlay(self, d):
        pass

    def draw(self, d):
        d._image.paste(self.canvas)
        self.overlay(d)
        if self.last is not None and self.done_at is None:
            x, y = self.last
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(255, 255, 255))

    def leftovers(self):
        return 0


class Harmonograph(Art):
    TITLE, SUB = "HARMONOGRAPH", "TWO SWINGING PENDULUMS DRAW ONE LINE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 301, (255, 170, 120), "glass", 262.0, (10, 8, 12)
    COUNTER = "DRAWING"
    WIDTH = 2

    def pos(self, s):
        T = s * 260
        x = 235 * (math.sin(3.001 * T) * math.exp(-0.0045 * T) + math.sin(2.0 * T + math.pi / 2) * math.exp(-0.0035 * T))
        y = 235 * (math.sin(2.0 * T + math.pi / 4) * math.exp(-0.004 * T) + math.sin(3.0 * T + 1.3) * math.exp(-0.005 * T))
        return (self.CX + x, self.CY + y)

    def color(self, s):
        return hsv(0.02 + s * 0.6, 0.6, 1.0)


class RoseCurve(Art):
    TITLE, SUB = "ROSE CURVE", "ONE EQUATION  -  A PERFECT FLOWER"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 302, (255, 120, 170), "bell", 294.0, (12, 6, 10)
    COUNTER = "PETALS DRAWN"
    WIDTH = 4
    SCALE = MAJOR

    def pos(self, s):
        th = s * 8 * math.pi
        r = 450 * math.cos(7 / 4 * th)
        return (self.CX + r * math.cos(th), self.CY + r * math.sin(th))

    def color(self, s):
        return hsv(0.9 + 0.25 * s, 0.6, 1.0)


class LissajousWeave(Art):
    TITLE, SUB = "LISSAJOUS WEAVE", "A SLOW PHASE SHIFT WEAVES THE PATTERN"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 303, (120, 220, 255), "glass", 330.0, (6, 8, 14)
    COUNTER = "WEAVE"
    WIDTH = 2

    def pos(self, s):
        T = s * 36 * math.pi
        d = s * 1.3
        return (self.CX + 440 * math.sin(5 * T + d), self.CY + 440 * math.sin(4 * T))

    def color(self, s):
        return hsv(0.5 + 0.35 * s, 0.6, 1.0)


class StringArt(Art):
    TITLE, SUB = "STRING ART", "200 PINS  -  ONE THREAD  -  TIMES TABLE OF 3"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 304, (255, 220, 140), "pluck", 220.0, (10, 9, 8)
    COUNTER = "THREAD WOVEN"
    WIDTH = 2
    NP, KMUL, RR = 200, 3, 450
    BEATS = 200

    def init(self):
        self.pins = [(self.CX + self.RR * math.cos(2 * math.pi * i / self.NP - math.pi / 2), self.CY + self.RR * math.sin(2 * math.pi * i / self.NP - math.pi / 2)) for i in range(self.NP)]
        for (x, y) in self.pins:
            self.cd.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(140, 120, 90))

    def pos(self, s):
        f = s * self.NP
        i = min(self.NP - 1, int(f))
        u = f - i
        a = self.pins[i]
        b = self.pins[(i * self.KMUL) % self.NP]
        # first half of each slot: travel the chord, second half: hop to the next pin along the rim
        if u < 0.8:
            k = u / 0.8
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        c = self.pins[(i + 1) % self.NP]
        k = (u - 0.8) / 0.2
        return (b[0] + (c[0] - b[0]) * k, b[1] + (c[1] - b[1]) * k)

    def seg(self, a, b, s):
        self.cd.line((a, b), fill=hsv(0.1 + 0.5 * s, 0.55, 1.0), width=2)

    def beat(self, i):
        self.ev("hit", (i % 24) / 24)


class Mandala(Art):
    TITLE, SUB = "MANDALA", "ONE PEN  -  EIGHT MIRRORS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 305, (200, 160, 255), "bell", 262.0, (8, 6, 14)
    COUNTER = "MANDALA"
    WIDTH = 2

    def pos(self, s):
        T = s * 90
        r = 60 + 380 * abs(math.sin(0.37 * T)) * (0.6 + 0.4 * math.sin(0.11 * T))
        th = 0.06 * T + 0.35 * math.sin(1.3 * T)
        return (self.CX + r * math.cos(th), self.CY + r * math.sin(th))

    def seg(self, a, b, s):
        col = hsv(0.65 + 0.4 * s, 0.55, 1.0)
        for k in range(8):
            ang = k * math.pi / 4
            for mirror in (1, -1):
                pts = []
                for (x, y) in (a, b):
                    dx, dy = x - self.CX, (y - self.CY) * mirror
                    pts.append((self.CX + dx * math.cos(ang) - dy * math.sin(ang), self.CY + dx * math.sin(ang) + dy * math.cos(ang)))
                self.cd.line(pts, fill=col, width=2)


class Sunflower(Art):
    TITLE, SUB = "SUNFLOWER", "EVERY SEED TURNS 137.5 DEGREES"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 306, (255, 210, 80), "marimba", 262.0, (10, 9, 4)
    COUNTER = "SEEDS PLANTED"
    NSEED = 1100
    BEATS = 1100
    SCALE = MAJOR

    def init(self):
        self.done_seeds = 0
        self.c = 470 / math.sqrt(self.NSEED)

    def seed_pos(self, i):
        r = self.c * math.sqrt(i)
        th = i * math.radians(137.508)
        return (self.CX + r * math.cos(th), self.CY + r * math.sin(th))

    def pos(self, s):
        return self.seed_pos(max(0, int(s * self.NSEED) - 1))

    def seg(self, a, b, s):
        n = int(s * self.NSEED)
        while self.done_seeds < n:
            i = self.done_seeds
            x, y = self.seed_pos(i)
            rr = 4 + 9 * math.sqrt(i / self.NSEED)
            self.cd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=hsv(0.08 + 0.1 * math.sqrt(i / self.NSEED), 0.85, 0.7 + 0.3 * ((i % 21) / 21)))
            self.done_seeds += 1

    def beat(self, i):
        if i % 6 == 0:
            self.ev("hit", (i % 34) / 34)


class Epicycles(Art):
    TITLE, SUB = "EPICYCLES", "SPINNING CIRCLES DRAW A HEART"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 307, (255, 120, 150), "glass", 294.0, (10, 6, 10)
    COUNTER = "HEART DRAWN"
    WIDTH = 5
    NC = 40

    def init(self):
        M = 256
        pts = []
        for k in range(M):
            t = 2 * math.pi * k / M
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append(complex(x * 24, y * 24 - 30))
        co = []
        for f in range(-M // 2, M // 2):
            c = sum(pts[k] * cmath.exp(-2j * math.pi * f * k / M) for k in range(M)) / M
            co.append((abs(c), f, c))
        co.sort(reverse=True)
        self.co = [(f, c) for _, f, c in co[:self.NC]]

    def chain(self, s):
        z = complex(self.CX, self.CY)
        pts = [z]
        for f, c in self.co:
            z += c * cmath.exp(2j * math.pi * f * s)
            pts.append(z)
        return pts

    def pos(self, s):
        z = self.chain(s)[-1]
        return (z.real, z.imag)

    def color(self, s):
        return hsv(0.95 + 0.05 * s, 0.7, 1.0)

    def overlay(self, d):
        if self.done_at is not None:
            return
        pts = self.chain(self.s)
        for k in range(1, len(pts)):
            a, b = pts[k - 1], pts[k]
            r = abs(b - a)
            if r > 2:
                d.ellipse((a.real - r, a.imag - r, a.real + r, a.imag + r), outline=(70, 60, 90), width=1)
            d.line((a.real, a.imag, b.real, b.imag), fill=(150, 140, 180), width=2)


class LorenzButterfly(Art):
    TITLE, SUB = "LORENZ BUTTERFLY", "CHAOS DRAWS A PERFECT BUTTERFLY"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 308, (120, 200, 255), "glass", 330.0, (4, 6, 12)
    COUNTER = "CHAOS TRACED"
    WIDTH = 2
    STEPS = 16000

    def init(self):
        x, y, z = 0.1, 0.0, 0.0
        self.path = []
        h = 0.005
        for i in range(self.STEPS + 1):
            self.path.append((x, z))
            dx, dy, dz = 10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z
            x, y, z = x + dx * h, y + dy * h, z + dz * h

    def pos(self, s):
        x, z = self.path[min(self.STEPS, int(s * self.STEPS))]
        return (self.CX + x * 21, self.CY + 470 - z * 19)

    def color(self, s):
        x, z = self.path[min(self.STEPS, int(s * self.STEPS))]
        return hsv(0.55 + 0.012 * z, 0.6, 1.0)

    def beat(self, i):
        x, z = self.path[min(self.STEPS, int(i / self.BEATS * self.STEPS))]
        self.ev("hit", clamp((x + 20) / 40, 0, 1))


class MaurerRose(Art):
    TITLE, SUB = "MAURER ROSE", "360 STRAIGHT LINES HIDE A ROSE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 309, (255, 140, 200), "pluck", 262.0, (10, 6, 12)
    COUNTER = "LINES DRAWN"
    WIDTH = 2
    N_, D_ = 6, 71
    BEATS = 360

    def rose(self, k):
        th = math.radians(k * self.D_)
        r = 450 * math.sin(self.N_ * th)
        return (self.CX + r * math.cos(th), self.CY + r * math.sin(th))

    def pos(self, s):
        if s < 0.8:
            f = s / 0.8 * 360
            i = int(f)
            a, b = self.rose(i), self.rose(i + 1)
            u = f - i
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        th = (s - 0.8) / 0.2 * 2 * math.pi
        r = 450 * math.sin(self.N_ * th)
        return (self.CX + r * math.cos(th), self.CY + r * math.sin(th))

    def seg(self, a, b, s):
        if s <= 0.8:
            self.cd.line((a, b), fill=hsv(0.85 + 0.2 * s, 0.5, 0.9), width=2)
        else:
            self.cd.line((a, b), fill=(255, 220, 120), width=6)

    def beat(self, i):
        self.ev("hit", (i % 24) / 24)


# ================================================================== SORTING VISUALISERS
class SortViz(Sim):
    TS = False
    T_END = 62
    N = 60
    SOUND = "pluck"
    BASE_NOTE = 196.0
    SCALE = MAJOR

    def setup(self):
        a = list(range(1, self.N + 1))
        self.rng.shuffle(a)
        self.arr = a[:]
        self.ops = list(self.algo(a[:]))
        self.i = 0
        self.hl = ()
        self.sweep = -1
        self.writes = 0
        self.cmps = 0

    def apply(self, op):
        k = op[0]
        if k == "c":
            self.hl = (op[1], op[2])
            self.cmps += 1
        elif k == "s":
            i, j = op[1], op[2]
            self.arr[i], self.arr[j] = self.arr[j], self.arr[i]
            self.hl = (i, j)
            self.writes += 1
            self.ev("hit", self.arr[i] / self.N)
        else:
            self.arr[op[1]] = op[2]
            self.hl = (op[1],)
            self.writes += 1
            self.ev("hit", op[2] / self.N)

    def physics(self, dt):
        if self.done_at is not None:
            return
        tgt = int(min(1.0, self.t / self.T_END) * len(self.ops))
        while self.i < tgt:
            self.apply(self.ops[self.i])
            self.i += 1
        if self.i >= len(self.ops):
            if self.sweep < 0:
                self.sweep = 0.0
                self.hl = ()
            old = int(self.sweep)
            self.sweep += dt * self.N / 2.2
            for k in range(old, min(self.N, int(self.sweep))):
                if k == 0 or self.arr[k - 1] <= self.arr[k]:
                    self.ev("special", self.arr[k] / self.N)
            if self.sweep >= self.N:
                self.p = 1.0
                return
        self.p = min(0.999, 0.97 * self.i / len(self.ops) + (0.03 * self.sweep / self.N if self.sweep >= 0 else 0))

    def leftovers(self):
        return sum(1 for k in range(1, self.N) if self.arr[k - 1] > self.arr[k])

    def draw(self, d):
        x0, x1, yb, hmax = 60, 1020, 1640, 1100
        bw = (x1 - x0) / self.N
        for k, v in enumerate(self.arr):
            h = hmax * v / self.N
            if self.sweep >= 0 and k < self.sweep:
                col = (90, 230, 130)
            elif k in self.hl:
                col = (255, 80, 80)
            else:
                col = hsv(0.55 + 0.4 * v / self.N, 0.55, 1.0)
            d.rectangle((x0 + k * bw + 1, yb - h, x0 + (k + 1) * bw - 1, yb), fill=col)

    def stats(self):
        return [f"COMPARISONS {self.cmps}   WRITES {self.writes}"]


class BubbleSort(SortViz):
    TITLE, SUB = "BUBBLE SORT", "BIG BARS BUBBLE TO THE TOP"
    T_END, SEED, ACC, BG = 62, 311, (120, 200, 255), (6, 8, 14)
    COUNTER = "SORTED"
    N = 50

    def algo(self, a):
        n = len(a)
        for i in range(n):
            for j in range(n - 1 - i):
                yield ("c", j, j + 1)
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    yield ("s", j, j + 1)


class InsertionSort(SortViz):
    TITLE, SUB = "INSERTION SORT", "EACH BAR SLIDES INTO ITS PLACE"
    T_END, SEED, ACC, BG = 62, 312, (255, 180, 120), (12, 8, 6)
    COUNTER = "SORTED"
    N = 56
    SOUND = "marimba"

    def algo(self, a):
        for i in range(1, len(a)):
            j = i
            while j > 0:
                yield ("c", j - 1, j)
                if a[j - 1] > a[j]:
                    a[j - 1], a[j] = a[j], a[j - 1]
                    yield ("s", j - 1, j)
                    j -= 1
                else:
                    break


class MergeSort(SortViz):
    TITLE, SUB = "MERGE SORT", "SPLIT  -  SORT  -  MERGE"
    T_END, SEED, ACC, BG = 62, 313, (150, 255, 180), (6, 12, 8)
    COUNTER = "SORTED"
    N = 120
    SOUND = "glass"

    def algo(self, a):
        def rec(lo, hi):
            if hi - lo <= 1:
                return
            mid = (lo + hi) // 2
            yield from rec(lo, mid)
            yield from rec(mid, hi)
            left, right = a[lo:mid], a[mid:hi]
            i = j = 0
            k = lo
            while i < len(left) and j < len(right):
                yield ("c", lo + i, mid + j)
                if left[i] <= right[j]:
                    a[k] = left[i]
                    i += 1
                else:
                    a[k] = right[j]
                    j += 1
                yield ("w", k, a[k])
                k += 1
            while i < len(left):
                a[k] = left[i]
                yield ("w", k, a[k])
                i += 1
                k += 1
            while j < len(right):
                a[k] = right[j]
                yield ("w", k, a[k])
                j += 1
                k += 1
        yield from rec(0, len(a))


class QuickSort(SortViz):
    TITLE, SUB = "QUICK SORT", "PICK A PIVOT  -  DIVIDE AND CONQUER"
    T_END, SEED, ACC, BG = 62, 314, (255, 120, 200), (12, 6, 12)
    COUNTER = "SORTED"
    N = 120
    SOUND = "bell"

    def algo(self, a):
        def rec(lo, hi):
            if lo >= hi:
                return
            piv = a[hi]
            i = lo
            for j in range(lo, hi):
                yield ("c", j, hi)
                if a[j] < piv:
                    a[i], a[j] = a[j], a[i]
                    yield ("s", i, j)
                    i += 1
            a[i], a[hi] = a[hi], a[i]
            yield ("s", i, hi)
            yield from rec(lo, i - 1)
            yield from rec(i + 1, hi)
        yield from rec(0, len(a) - 1)


# ================================================================== CHAIN REACTIONS
class Chain(Sim):
    TS = False
    RMAX = 46.0
    START_T = 1.0
    TOTAL = 63.0

    def setup(self):
        self.dots = self.layout()          # [x, y, col]
        n = len(self.dots)
        self.trig = [None] * n
        self.N = n
        # geometric graph -> exact chain timing (radius grows at a constant rate)
        self.cells = {}
        for i, (x, y, c) in enumerate(self.dots):
            self.cells.setdefault((int(x // self.RMAX), int(y // self.RMAX)), []).append(i)
        dist = [1e18] * n
        s0 = self.start_index()
        dist[s0] = 0.0
        pq = [(0.0, s0)]
        while pq:
            dd, i = heapq.heappop(pq)
            if dd > dist[i]:
                continue
            for j in self.neigh(i):
                dj = dd + math.hypot(self.dots[i][0] - self.dots[j][0], self.dots[i][1] - self.dots[j][1])
                if dj < dist[j]:
                    dist[j] = dj
                    heapq.heappush(pq, (dj, j))
        reach = max(dist)
        assert reach < 1e17, "chain layout is not connected"
        self.speed = reach / (self.TOTAL - self.START_T)    # px/s of radius growth
        self.grow = self.RMAX / self.speed
        self.s0 = s0
        self.count = 0
        self.active = []

    def neigh(self, i):
        x, y, _ = self.dots[i]
        cx, cy = int(x // self.RMAX), int(y // self.RMAX)
        for a in range(cx - 1, cx + 2):
            for b in range(cy - 1, cy + 2):
                for j in self.cells.get((a, b), ()):
                    if j != i and (self.dots[j][0] - x) ** 2 + (self.dots[j][1] - y) ** 2 <= self.RMAX ** 2:
                        yield j

    def start_index(self):
        return 0

    def fire(self, i, t):
        self.trig[i] = t
        self.count += 1
        self.active.append(i)
        if self.count % 2 == 0 or self.count < 30:
            self.ev("pop", (self.dots[i][0] - 60) / 960 * 0.6 + (self.dots[i][1] - 460) / 1200 * 0.4)

    def physics(self, dt):
        if self.t >= self.START_T and self.trig[self.s0] is None:
            self.fire(self.s0, self.t)
        still = []
        for i in self.active:
            r = min(self.RMAX, (self.t - self.trig[i]) * self.speed)
            for j in self.neigh(i):
                if self.trig[j] is None and (self.dots[j][0] - self.dots[i][0]) ** 2 + (self.dots[j][1] - self.dots[i][1]) ** 2 <= r * r:
                    self.fire(j, self.t)
            if self.t - self.trig[i] < self.grow:
                still.append(i)
        self.active = still
        self.p = self.count / self.N

    def leftovers(self):
        return sum(1 for t in self.trig if t is None)

    def draw(self, d):
        for i, (x, y, c) in enumerate(self.dots):
            t0 = self.trig[i]
            if t0 is None:
                d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=c)
            else:
                age = self.t - t0
                if age < self.grow + 0.5:
                    r = min(self.RMAX, age * self.speed)
                    a = clamp(1 - age / (self.grow + 0.5), 0, 1)
                    d.ellipse((x - r, y - r, x + r, y + r), outline=tuple(int(v * a) for v in c), width=3)
                    d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 255, 255) if age < 0.25 else tuple(int(v * 0.35) for v in c))
                else:
                    d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=tuple(int(v * 0.3) for v in c))


class GridChain(Chain):
    TITLE, SUB = "CHAIN REACTION", "ONE POP  -  900 DOTS  -  ONE CHAIN"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 321, (255, 150, 90), "pop", 262.0, (12, 8, 6)
    COUNTER = "POPPED"

    def layout(self):
        out = []
        for r in range(30):
            for c in range(30):
                out.append([105 + c * 30, 610 + r * 30, hsv(0.02 + 0.12 * ((r + c) / 58), 0.75, 1.0)])
        return out

    def start_index(self):
        return 0


class SpiralChain(Chain):
    TITLE, SUB = "SPIRAL FUSE", "THE FIRE RUNS ALL THE WAY TO THE CENTRE"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 322, (255, 210, 90), "pop", 294.0, (10, 8, 4)
    COUNTER = "FUSE BURNED"
    RMAX = 30.0

    def layout(self):
        out = []
        th, r = 0.0, 460.0
        while r > 40:
            out.append([540 + r * math.cos(th), 1060 + r * math.sin(th), hsv(0.08 + 0.1 * (1 - r / 460), 0.8, 1.0)])
            th += 22.0 / r
            r = 460 - 50 * th / (2 * math.pi)
        return out


class RandomChain(Chain):
    TITLE, SUB = "FIREWORK FIELD", "EVERY BLAST LIGHTS ITS NEIGHBOURS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 323, (180, 150, 255), "pop", 330.0, (6, 6, 14)
    COUNTER = "FIREWORKS LIT"
    RMAX = 52.0

    def layout(self):
        rng = self.rng
        out = [[540, 1060, hsv(0.7, 0.6, 1.0)]]
        tries = 0
        while len(out) < 700 and tries < 60000:
            tries += 1
            base = out[rng.randrange(len(out))]
            a = rng.uniform(0, 6.283)
            dd = rng.uniform(0.62, 0.9) * self.RMAX
            x, y = base[0] + math.cos(a) * dd, base[1] + math.sin(a) * dd
            if not (90 < x < 990 and 520 < y < 1600):
                continue
            if any((x - o[0]) ** 2 + (y - o[1]) ** 2 < (0.55 * self.RMAX) ** 2 for o in out):
                continue
            out.append([x, y, hsv(rng.random(), 0.55, 1.0)])
        return out


# ================================================================== PHYSICS TOYS
class NewtonCradle(Sim):
    TS = False
    TITLE, SUB = "NEWTON'S CRADLE", "MOMENTUM PASSES THROUGH SEVEN STEEL BALLS"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 331, (220, 220, 235), "click", 523.0, (10, 10, 14)
    COUNTER = "SWINGING"
    NBALL, RB, LEN, G = 7, 44, 560, 2400.0

    def setup(self):
        n = self.NBALL
        self.th = [0.0] * n
        self.om = [0.0] * n
        self.px = [540 + (i - (n - 1) / 2) * 2 * self.RB for i in range(n)]
        self.th[0] = -0.75
        self.th[1] = -0.75
        self.hits = 0

    def bob(self, i):
        return (self.px[i] + self.LEN * math.sin(self.th[i]), 640 + self.LEN * math.cos(self.th[i]))

    def physics(self, dt):
        if self.done_at is not None:
            return
        for i in range(self.NBALL):
            self.om[i] += -(self.G / self.LEN) * math.sin(self.th[i]) * dt
            self.th[i] += self.om[i] * dt
        for _ in range(self.NBALL):
            for i in range(self.NBALL - 1):
                xa, xb = self.bob(i)[0], self.bob(i + 1)[0]
                if xb - xa < 2 * self.RB - 0.01 and self.om[i] > self.om[i + 1]:
                    rel = self.om[i] - self.om[i + 1]
                    self.om[i], self.om[i + 1] = self.om[i + 1], self.om[i]
                    if rel * self.LEN > 120:
                        self.hits += 1
                        self.ev("hit", clamp(rel / 6, 0, 1))
                    # resolve overlap symmetrically (equal masses)
                    ov = (2 * self.RB - (xb - xa)) / 2 / self.LEN
                    self.th[i] -= ov
                    self.th[i + 1] += ov
        self.p = min(1.0, self.t / self.T_END)

    def leftovers(self):
        return 0

    def draw(self, d):
        d.rectangle((140, 620, 940, 640), fill=(120, 120, 140))
        for i in range(self.NBALL):
            x, y = self.bob(i)
            d.line((self.px[i] - 30, 640, x, y), fill=(150, 150, 170), width=2)
            d.line((self.px[i] + 30, 640, x, y), fill=(150, 150, 170), width=2)
        for i in range(self.NBALL):
            x, y = self.bob(i)
            r = self.RB - 1
            d.ellipse((x - r, y - r, x + r, y + r), fill=(185, 190, 205))
            d.ellipse((x - r * 0.55, y - r * 0.7, x - r * 0.05, y - r * 0.2), fill=(245, 245, 255))

    def stats(self):
        return [f"CLICKS  {self.hits}"]


class TripleDoublePendulum(Sim):
    TS = False
    TITLE, SUB = "CHAOS PENDULUMS", "THREE PENDULUMS  -  ALMOST THE SAME START"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 332, (255, 255, 255), "glass", 262.0, (6, 6, 12)
    COUNTER = "CHAOS"
    L1, L2, G = 230.0, 230.0, 900.0
    COLS = [(255, 90, 100), (90, 220, 130), (100, 160, 255)]

    def setup(self):
        self.st = [[2.6 + k * 0.002, 2.4, 0.0, 0.0] for k in range(3)]
        self.trails = [[] for _ in range(3)]
        self.sign = [0, 0, 0]
        self.tick = 0

    def deriv(self, s):
        t1, t2, w1, w2 = s
        d = t1 - t2
        den = 2 - math.cos(2 * d)
        a1 = (-self.G * 3 * math.sin(t1) - self.G * math.sin(t1 - 2 * t2) - 2 * math.sin(d) * (w2 * w2 * self.L2 + w1 * w1 * self.L1 * math.cos(d))) / (self.L1 * den)
        a2 = (2 * math.sin(d) * (w1 * w1 * self.L1 * 2 + self.G * 2 * math.cos(t1) + w2 * w2 * self.L2 * math.cos(d))) / (self.L2 * den)
        return [w1, w2, a1, a2]

    def rk4(self, s, h):
        k1 = self.deriv(s)
        k2 = self.deriv([s[i] + h / 2 * k1[i] for i in range(4)])
        k3 = self.deriv([s[i] + h / 2 * k2[i] for i in range(4)])
        k4 = self.deriv([s[i] + h * k3[i] for i in range(4)])
        return [s[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(4)]

    def ends(self, s):
        x1 = 540 + self.L1 * math.sin(s[0])
        y1 = 980 + self.L1 * math.cos(s[0])
        return (x1, y1), (x1 + self.L2 * math.sin(s[1]), y1 + self.L2 * math.cos(s[1]))

    def physics(self, dt):
        if self.done_at is not None:
            return
        self.tick += 1
        for k in range(3):
            self.st[k] = self.rk4(self.st[k], dt)
            sg = 1 if math.sin(self.st[k][1]) > 0 else -1
            if sg != self.sign[k]:
                self.sign[k] = sg
                self.ev("hit", (k * 0.33 + 0.1 + 0.2 * abs(math.sin(self.st[k][0]))) % 1)
            if self.tick % 2 == 0:
                self.trails[k].append(self.ends(self.st[k])[1])
                del self.trails[k][:-260]
        self.p = min(1.0, self.t / self.T_END)

    def leftovers(self):
        return 0

    def draw(self, d):
        for k in range(3):
            tr = self.trails[k]
            c = self.COLS[k]
            for i in range(1, len(tr)):
                a = i / len(tr)
                d.line((tr[i - 1], tr[i]), fill=tuple(int(v * a) for v in c), width=3)
        for k in range(3):
            (x1, y1), (x2, y2) = self.ends(self.st[k])
            c = self.COLS[k]
            d.line((540, 980, x1, y1), fill=(200, 200, 210), width=4)
            d.line((x1, y1, x2, y2), fill=(200, 200, 210), width=4)
            d.ellipse((x1 - 12, y1 - 12, x1 + 12, y1 + 12), fill=c)
            d.ellipse((x2 - 16, y2 - 16, x2 + 16, y2 + 16), fill=c)
        d.ellipse((530, 970, 550, 990), fill=(255, 255, 255))


class VenusDance(Art):
    TITLE, SUB = "VENUS DANCE", "EARTH AND VENUS DRAW A FIVE-PETAL FLOWER"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 333, (255, 220, 150), "bell", 262.0, (4, 4, 10)
    COUNTER = "EIGHT YEARS"
    BEATS = 320
    RE, RV = 460, 333

    def init(self):
        self.lines = 0
        self.cd.ellipse((self.CX - self.RE, self.CY - self.RE, self.CX + self.RE, self.CY + self.RE), outline=(30, 40, 70), width=2)
        self.cd.ellipse((self.CX - self.RV, self.CY - self.RV, self.CX + self.RV, self.CY + self.RV), outline=(60, 45, 30), width=2)

    def planets(self, s):
        years = s * 8
        ae = 2 * math.pi * years
        av = 2 * math.pi * years / 0.61520
        return ((self.CX + self.RE * math.cos(ae), self.CY + self.RE * math.sin(ae)), (self.CX + self.RV * math.cos(av), self.CY + self.RV * math.sin(av)))

    def pos(self, s):
        return self.planets(s)[1]

    def seg(self, a, b, s):
        pass

    def beat(self, i):
        e, v = self.planets(i / self.BEATS)
        self.cd.line((e, v), fill=hsv(0.08 + 0.5 * i / self.BEATS, 0.45, 0.85), width=2)
        if i % 2 == 0:
            self.ev("hit", (i % 40) / 40)

    def overlay(self, d):
        e, v = self.planets(self.s)
        d.line((e, v), fill=(255, 255, 255), width=1)
        d.ellipse((self.CX - 26, self.CY - 26, self.CX + 26, self.CY + 26), fill=(255, 200, 80))
        d.ellipse((e[0] - 15, e[1] - 15, e[0] + 15, e[1] + 15), fill=(90, 160, 255))
        d.ellipse((v[0] - 13, v[1] - 13, v[0] + 13, v[1] + 13), fill=(255, 210, 150))


class SpinHexagon(Sim):
    TS = False
    TITLE, SUB = "SPINNING HEXAGON", "WALL BOUNCES ADD BALLS  -  UP TO 120"
    T_END, SEED, ACC, SOUND, BASE_NOTE, BG = 66, 334, (120, 255, 200), "marimba", 262.0, (6, 12, 10)
    COUNTER = "SPINNING"
    CX, CY, RAD, OM, G, BR, CAP = 540, 1050, 440, 0.55, 900.0, 13, 120

    def setup(self):
        self.ang = 0.0
        self.balls = [[540.0, 900.0, 260.0, 0.0, 0.0]]
        self.bounces = 0

    def verts(self):
        return [(self.CX + self.RAD * math.cos(self.ang + k * math.pi / 3), self.CY + self.RAD * math.sin(self.ang + k * math.pi / 3)) for k in range(6)]

    def walls(self, b, vs, new, spawn):
        for k in range(6):
            (x0, y0), (x1, y1) = vs[k], vs[(k + 1) % 6]
            ex, ey = x1 - x0, y1 - y0
            L = math.hypot(ex, ey)
            nx, ny = -ey / L, ex / L                      # candidate normal
            if (self.CX - x0) * nx + (self.CY - y0) * ny < 0:
                nx, ny = -nx, -ny                         # make it point inward
            dist = (b[0] - x0) * nx + (b[1] - y0) * ny
            if dist < self.BR:
                # wall surface velocity at the contact point (rigid rotation)
                cx, cy = b[0] - nx * dist, b[1] - ny * dist
                svx, svy = -self.OM * (cy - self.CY), self.OM * (cx - self.CX)
                rvx, rvy = b[2] - svx, b[3] - svy
                vn = rvx * nx + rvy * ny
                if vn < 0:
                    rvx -= 1.9 * vn * nx
                    rvy -= 1.9 * vn * ny
                    b[2], b[3] = rvx + svx, rvy + svy
                    if spawn and -vn > 150:
                        self.bounces += 1
                        self.ev("hit", k / 6 + self.rng.random() * 0.15)
                        if len(self.balls) + len(new) < self.CAP:
                            a = self.rng.uniform(0, 6.283)
                            new.append([b[0], b[1], b[2] + math.cos(a) * 120, b[3] + math.sin(a) * 120, len(self.balls) + len(new)])
                b[0] += nx * (self.BR - dist)
                b[1] += ny * (self.BR - dist)

    def physics(self, dt):
        if self.done_at is not None:
            return
        self.ang += self.OM * dt
        vs = self.verts()
        new = []
        for b in self.balls:
            b[3] += self.G * dt
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            self.walls(b, vs, new, True)
            sp = math.hypot(b[2], b[3])
            if sp > 1800:
                b[2], b[3] = b[2] * 1800 / sp, b[3] * 1800 / sp
        self.balls += new
        for _ in range(2):
            self.collide_balls()
            for b in self.balls:
                self.walls(b, vs, None, False)
        self.p = min(1.0, self.t / self.T_END)

    def collide_balls(self):
        r2 = 2 * self.BR
        cells = {}
        for i, b in enumerate(self.balls):
            cells.setdefault((int(b[0] // r2), int(b[1] // r2)), []).append(i)
        for (cx, cy), ids in cells.items():
            for ox, oy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 1)):
                other = cells.get((cx + ox, cy + oy))
                if not other:
                    continue
                for i in ids:
                    for j in other:
                        if (ox, oy) == (0, 0) and j <= i:
                            continue
                        a, b = self.balls[i], self.balls[j]
                        dx, dy = b[0] - a[0], b[1] - a[1]
                        d2 = dx * dx + dy * dy
                        if 1e-6 < d2 < r2 * r2:
                            d = math.sqrt(d2)
                            nx, ny = dx / d, dy / d
                            ov = (r2 - d) / 2
                            a[0] -= nx * ov
                            a[1] -= ny * ov
                            b[0] += nx * ov
                            b[1] += ny * ov
                            rv = (b[2] - a[2]) * nx + (b[3] - a[3]) * ny
                            if rv < 0:
                                imp = -0.9 * rv
                                a[2] -= nx * imp
                                a[3] -= ny * imp
                                b[2] += nx * imp
                                b[3] += ny * imp

    def overlaps(self):
        n = 0
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                a, b = self.balls[i], self.balls[j]
                if (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 < (2 * self.BR - 6) ** 2:
                    n += 1
        return n

    def audit_missed(self):
        vs = self.verts()
        n = 0
        for b in self.balls:
            for k in range(6):
                (x0, y0), (x1, y1) = vs[k], vs[(k + 1) % 6]
                ex, ey = x1 - x0, y1 - y0
                L = math.hypot(ex, ey)
                nx, ny = -ey / L, ex / L
                if (self.CX - x0) * nx + (self.CY - y0) * ny < 0:
                    nx, ny = -nx, -ny
                if (b[0] - x0) * nx + (b[1] - y0) * ny < self.BR - 2:
                    n += 1
        return n

    def leftovers(self):
        return 0

    def draw(self, d):
        vs = self.verts()
        d.polygon(vs, outline=(120, 255, 200), width=10)
        for b in self.balls:
            d.ellipse((b[0] - self.BR, b[1] - self.BR, b[0] + self.BR, b[1] + self.BR), fill=hsv(b[4] / 40, 0.55, 1.0))

    def stats(self):
        return [f"BALLS  {len(self.balls)}"]


BATCH_F = [Harmonograph, RoseCurve, LissajousWeave, StringArt, Mandala, Sunflower, Epicycles, LorenzButterfly, MaurerRose,
           BubbleSort, InsertionSort, MergeSort, QuickSort, GridChain, SpiralChain, RandomChain,
           NewtonCradle, TripleDoublePendulum, VenusDance, SpinHexagon]
