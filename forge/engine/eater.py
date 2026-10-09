"""Batch 2 'eater' archetype: balls that always destroy (and optionally bounce off) every element they touch.
Honest by construction: spatial-hash collisions, every overlap counts, no time scaling, finale sweep clears leftovers."""
import json, math
from PIL import Image, ImageDraw, ImageFont
from core import *

def calib(name, default):
    try:
        return json.load(open(HERE / "calib" / f"{name}.json"))["K"]
    except Exception:
        return default


def clamp(x, a, b):
    return max(a, min(b, x))


# ------------------------------------------------------------------ masks (u, v in [-1, 1], v down)
def m_heart(u, v, c, r):
    x, y = u * 1.25, -v * 1.25 + 0.15
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 < 0


def m_pyramid(u, v, c, r):
    return abs(u) <= (v + 1) / 2 * 0.98


def m_diamond(u, v, c, r):
    return abs(u) + abs(v) < 1


def m_circle(u, v, c, r):
    return u * u + v * v < 1


def m_checker(u, v, c, r):
    return (c + r) % 2 == 0


def m_star(u, v, c, r):
    rad = math.hypot(u, v)
    th = math.atan2(v, u) + math.pi / 2
    return rad < 0.38 + 0.62 * abs(math.cos(2.5 * th)) ** 1.5


def m_smiley(u, v, c, r):
    rad = math.hypot(u, v)
    if 0.78 < rad < 1.0:
        return True
    for ex in (-0.36, 0.36):
        if math.hypot(u - ex, v + 0.3) < 0.17:
            return True
    return 0.5 < rad < 0.66 and v > 0.18


def m_wave(u, v, c, r):
    return abs(v - 0.55 * math.sin(3.2 * math.pi * u / 2 * 2)) < 0.2


def m_zigzag(u, v, c, r):
    return abs(v - (1.6 * abs(((u * 2.5) % 2) - 1) - 0.8)) < 0.22


def m_bolt(u, v, c, r):
    # lightning bolt polygon
    pts = [(0.15, -1), (-0.55, 0.15), (-0.05, 0.15), (-0.3, 1), (0.6, -0.25), (0.05, -0.25), (0.45, -1)]
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > v) != (yj > v) and u < (xj - xi) * (v - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def m_text(text):
    fnt = ImageFont.truetype(IMPACT, 260)
    img = Image.new("L", (900, 300), 0)
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=fnt)
    d.text(((900 - w) / 2, 10), text, font=fnt, fill=255)
    bb = img.getbbox()
    img = img.crop(bb)
    W_, H_ = img.size

    def mask(u, v, c, r):
        x = int((u + 1) / 2 * (W_ - 1))
        y = int((v + 1) / 2 * (H_ - 1))
        return img.getpixel((x, y)) > 128
    mask.aspect = W_ / H_
    return mask


# ------------------------------------------------------------------ element builders
def rect_el(x, y, w, h, col, v):
    return [x, y, w, h, True, col, "r", v]


def circ_el(x, y, r, col, v):
    return [x, y, r, 0, True, col, "c", v]


def mask_layout(mask, M, region, colfn, aspect=None):
    """square-ish bricks filling `mask` inside region; chooses a resolution giving ~M elements"""
    x0, y0, x1, y1 = region
    W_, H_ = x1 - x0, y1 - y0
    if aspect is None:
        aspect = getattr(mask, "aspect", None)
    if aspect:
        # keep the mask's own aspect ratio, centred
        if W_ / H_ > aspect:
            nw = H_ * aspect
            x0 += (W_ - nw) / 2
            W_ = nw
        else:
            nh = W_ / aspect
            y0 += (H_ - nh) / 2
            H_ = nh
    best = None
    for cols in range(5, 120):
        cw = W_ / cols
        rows = max(1, int(H_ / cw))
        cnt = sum(1 for r in range(rows) for c in range(cols) if mask((c + .5) / cols * 2 - 1, (r + .5) / rows * 2 - 1, c, r))
        if best is None or abs(cnt - M) < abs(best[0] - M):
            best = (cnt, cols, rows)
    _, cols, rows = best
    cw, ch = W_ / cols, H_ / rows
    out = []
    for r in range(rows):
        for c in range(cols):
            u, v = (c + .5) / cols * 2 - 1, (r + .5) / rows * 2 - 1
            if mask(u, v, c, r):
                out.append(rect_el(x0 + c * cw + 1, y0 + r * ch + 1, cw - 2, ch - 2, colfn(u, v, c, r, cols, rows), (c + 0.5) / cols))
    return out


def ring_layout(M, cx, cy, r0, r1, colfn, nrings=None):
    nrings = nrings or max(3, int(math.sqrt(M / 5)))
    out = []
    tot = sum(r0 + (r1 - r0) * k / max(1, nrings - 1) for k in range(nrings))
    for k in range(nrings):
        R = r0 + (r1 - r0) * k / max(1, nrings - 1)
        n = max(6, int(M * R / tot))
        rr = clamp(math.pi * R / n * 0.8, 4, 14)
        for i in range(n):
            a = 2 * math.pi * i / n + k * 0.3
            out.append(circ_el(cx + R * math.cos(a), cy + R * math.sin(a), rr, colfn(k / max(1, nrings - 1), i / n), i / n))
    return out


def scatter_layout(rng, M, region, rmin, rmax, colfn, shape=None):
    x0, y0, x1, y1 = region
    out, tries = [], 0
    while len(out) < M and tries < M * 60:
        tries += 1
        r = rng.uniform(rmin, rmax)
        x, y = rng.uniform(x0 + r, x1 - r), rng.uniform(y0 + r, y1 - r)
        if shape and not shape((x - (x0 + x1) / 2) / ((x1 - x0) / 2), (y - (y0 + y1) / 2) / ((y1 - y0) / 2)):
            continue
        if all((x - e[0]) ** 2 + (y - e[1]) ** 2 > (r + e[2] + 2) ** 2 for e in out[-80:]) and all((x - e[0]) ** 2 + (y - e[1]) ** 2 > (r + e[2] + 2) ** 2 for e in out):
            out.append(circ_el(x, y, r, colfn((x - x0) / (x1 - x0), (y - y0) / (y1 - y0)), (x - x0) / (x1 - x0)))
    return out


def spiral_layout(M, cx, cy, rmax, colfn, arms=2):
    out = []
    per = M // arms
    for a in range(arms):
        for i in range(per):
            t = i / per
            ang = a * 2 * math.pi / arms + t * 5.0 * math.pi
            R = 25 + t * rmax
            out.append(circ_el(cx + R * math.cos(ang), cy + R * math.sin(ang), clamp(4 + 6 * t, 4, 11), colfn(t, a / arms), t))
    return out


# ------------------------------------------------------------------ the archetype
class Eater(Sim):
    HONEST = True
    TS = False
    LIST, AIDX = "el", 4
    FIN = 0.97
    M0 = 300
    MOTION = "grav"          # grav | bounce | orbit | home | cannon | rain
    SOLID = True
    CLONE = 0.0
    CAP0, CAPK = 3, 0.1
    NB = 3
    SPEED = 420
    BR = 7
    GROW = 0.0
    GRAV = 700
    ARENA = "box"            # box | circle
    L, R, T, B = 60, 1020, 420, 1680
    CX, CY, RAD = 540, 1050, 500
    TURN = 4.0
    SPAWN = 3.0
    CAPMAX = 400
    REGION = (80, 470, 1000, 1000)
    FLOORV = None
    ORBK = 4.4
    cur_assist = 0.0

    def __init__(self):
        c = type(self)
        K = calib(c.__name__, 1.0)
        self.K = K
        self.SPEED = c.SPEED
        if c.NB == 1 and c.CLONE == 0:
            self.NB = 1
            self.SPEED = c.SPEED * clamp(K, 0.6, 1.7)
            K = 1.0
        else:
            self.NB = max(1, round(c.NB * K))
        self.SPAWN = c.SPAWN * K
        self.CAPMAX = max(3, int(c.CAPMAX * K))
        self.CAPK = c.CAPK * K
        self.CLONE = min(0.9, c.CLONE * K)
        super().__init__()

    def assist(self):
        """0..1: how far behind schedule we are (aiming help only; physics stays honest)"""
        return clamp((self.target() - self.p) * 10 - 0.3, 0.0, 1.0)

    def aim_target(self, b):
        best, bd = None, 1e18
        for e in self.alive_cache[::max(1, len(self.alive_cache) // 80)]:
            ex = e[0] + (e[2] / 2 if e[6] == "r" else 0)
            ey = e[1] + (e[3] / 2 if e[6] == "r" else 0)
            dd = (ex - b[0]) ** 2 + (ey - b[1]) ** 2
            if dd < bd:
                best, bd = (ex, ey), dd
        return best

    # -- to override
    def layout(self):
        return []

    # -- setup
    def setup(self):
        self.el = self.layout()
        self.M, self.rem = len(self.el), 0
        self.cells = {}
        for e in self.el:
            if e[6] == "r":
                x0, y0, x1, y1 = e[0], e[1], e[0] + e[2], e[1] + e[3]
            else:
                x0, y0, x1, y1 = e[0] - e[2], e[1] - e[2], e[0] + e[2], e[1] + e[2]
            for cx in range(int(x0 // 48), int(x1 // 48) + 1):
                for cy in range(int(y0 // 48), int(y1 // 48) + 1):
                    self.cells.setdefault((cx, cy), []).append(e)
        self.top_el = min((e[1] - (e[2] if e[6] == "c" else 0)) for e in self.el) if self.el else self.T + 100
        self.launch = math.sqrt(2 * self.GRAV * max(200, self.B - self.top_el + 60))
        self.balls, self.acc, self.alive_cache, self.tick = [], 0.0, [], 0
        self.init_balls()

    def new_ball(self, x, y, vx, vy):
        return [x, y, vx, vy, self.BR, [], False]

    def init_balls(self):
        rng = self.rng
        for i in range(self.NB):
            if self.MOTION in ("grav", "bounce", "home"):
                a = rng.uniform(0, 6.283)
                x = rng.uniform(self.L + 150, self.R - 150) if self.ARENA == "box" else self.CX + rng.uniform(-150, 150)
                y = rng.uniform(self.B - 400, self.B - 150) if self.ARENA == "box" else self.CY + rng.uniform(-150, 150)
                v = self.SPEED if self.MOTION != "grav" else 0
                vx, vy = math.cos(a) * v, math.sin(a) * v - (self.launch if self.MOTION == "grav" else 0)
                self.balls.append(self.new_ball(x, y, vx, vy))
            elif self.MOTION == "orbit":
                a = rng.uniform(0, 6.283)
                R = rng.uniform(150, 350)
                s = rng.uniform(0.6, 1.1) * R * math.sqrt(self.ORBK)
                self.balls.append(self.new_ball(self.CX + R * math.cos(a), self.CY + R * math.sin(a), -math.sin(a) * s, math.cos(a) * s))

    # -- collisions
    def touching(self, e, x, y, r):
        if e[6] == "c":
            d2 = (x - e[0]) ** 2 + (y - e[1]) ** 2
            if d2 < (r + e[2]) ** 2:
                d = math.sqrt(d2) or 0.01
                return ((x - e[0]) / d, (y - e[1]) / d)
            return None
        cx, cy = clamp(x, e[0], e[0] + e[2]), clamp(y, e[1], e[1] + e[3])
        d2 = (x - cx) ** 2 + (y - cy) ** 2
        if d2 < r * r:
            if d2 < 1e-6:
                mx, my = e[0] + e[2] / 2, e[1] + e[3] / 2
                if abs(x - mx) / (e[2] / 2 + 1e-6) > abs(y - my) / (e[3] / 2 + 1e-6):
                    return (1.0 if x > mx else -1.0, 0.0)
                return (0.0, 1.0 if y > my else -1.0)
            d = math.sqrt(d2)
            return ((x - cx) / d, (y - cy) / d)
        return None

    def nearby(self, x, y, r):
        seen, out = set(), []
        for cx in range(int((x - r) // 48), int((x + r) // 48) + 1):
            for cy in range(int((y - r) // 48), int((y + r) // 48) + 1):
                for e in self.cells.get((cx, cy), ()):
                    if e[4] and id(e) not in seen:
                        seen.add(id(e))
                        out.append(e)
        return out

    def audit_missed(self):
        n = 0
        for b in self.balls:
            for e in self.nearby(b[0], b[1], b[4] + 1):
                if self.touching(e, b[0], b[1], b[4] - 0.5):
                    n += 1
        return n

    def destroy(self, e, b, new, cap):
        e[4] = False
        self.rem += 1
        cx = e[0] + (e[2] / 2 if e[6] == "r" else 0)
        cy = e[1] + (e[3] / 2 if e[6] == "r" else 0)
        self.burst(cx, cy, e[5], 6, 230, 0.45)
        self.ev("hit", e[7])
        if self.CLONE and len(self.balls) + len(new) < cap and self.rng.random() < self.CLONE:
            a = self.rng.uniform(0, 6.283)
            sp = max(self.SPEED, 200) if self.MOTION != "grav" else 0
            vx = math.cos(a) * sp if sp else -b[2] + self.rng.uniform(-120, 120)
            vy = math.sin(a) * sp if sp else b[3]
            new.append(self.new_ball(b[0], b[1], vx, vy))

    # -- motion
    def refresh_alive(self):
        self.alive_cache = [e for e in self.el if e[4]]

    def move(self, b, dt):
        m = self.MOTION
        if m in ("grav", "rain"):
            b[3] += self.GRAV * dt
        elif m == "orbit":
            b[2] -= self.ORBK * (b[0] - self.CX) * dt
            b[3] -= self.ORBK * (b[1] - self.CY) * dt
        elif m == "home" or (m == "bounce" and self.cur_assist > 0.05):
            if self.alive_cache:
                best = self.aim_target(b)
                ang = math.atan2(b[3], b[2])
                want = math.atan2(best[1] - b[1], best[0] - b[0])
                diff = math.atan2(math.sin(want - ang), math.cos(want - ang))
                dist = math.hypot(best[0] - b[0], best[1] - b[1])
                rate = self.TURN if m == "home" else self.TURN * self.cur_assist
                rate = max(rate, self.SPEED / max(15.0, dist) * 1.3 * (1.0 if m == "home" else self.cur_assist))
                ang += clamp(diff, -rate * dt, rate * dt)
                b[2], b[3] = math.cos(ang) * self.SPEED, math.sin(ang) * self.SPEED
        if m == "orbit" and self.cur_assist > 0.05 and self.alive_cache:
            best = self.aim_target(b)
            dd = math.hypot(best[0] - b[0], best[1] - b[1]) or 1
            b[2] += (best[0] - b[0]) / dd * 700 * self.cur_assist * dt
            b[3] += (best[1] - b[1]) / dd * 700 * self.cur_assist * dt
        b[0] += b[2] * dt
        b[1] += b[3] * dt
        r = b[4]
        if self.ARENA == "circle":
            dx, dy = b[0] - self.CX, b[1] - self.CY
            d = math.hypot(dx, dy)
            if d + r > self.RAD:
                nx, ny = dx / d, dy / d
                if b[2] * nx + b[3] * ny > 0:
                    b[2], b[3] = reflect(b[2], b[3], nx, ny)
                b[0], b[1] = self.CX + nx * (self.RAD - r - 0.5), self.CY + ny * (self.RAD - r - 0.5)
            return
        if b[0] < self.L + r:
            b[0], b[2] = self.L + r, abs(b[2])
        elif b[0] > self.R - r:
            b[0], b[2] = self.R - r, -abs(b[2])
        if b[1] < self.T + r:
            b[1], b[3] = self.T + r, abs(b[3])
        if b[1] > self.B - r:
            if m == "grav":
                b[1] = self.B - r
                b[3] = -self.launch * self.rng.uniform(0.97, 1.0)
                b[2] = self.rng.uniform(-380, 380)
                if self.cur_assist > 0.05 and self.alive_cache and self.rng.random() < self.cur_assist:
                    ex, ey = self.aim_target(b)
                    disc = b[3] * b[3] - 2 * self.GRAV * (self.B - ey)
                    if disc > 0:
                        tt = (-b[3] - math.sqrt(disc)) / self.GRAV
                        if tt > 0.05:
                            b[2] = clamp((ex - b[0]) / tt, -800, 800)
            elif m in ("cannon", "rain"):
                if b[1] > self.B + 30:
                    b[6] = True
            else:
                b[1], b[3] = self.B - r, -abs(b[3])

    def spawn(self, dt):
        if self.MOTION not in ("cannon", "rain"):
            return
        self.acc += self.SPAWN * dt
        while self.acc >= 1 and len(self.balls) < self.CAPMAX:
            self.acc -= 1
            if self.MOTION == "cannon":
                ang = math.sin(self.t * 0.9) * 0.95
                if self.cur_assist > 0.05 and self.alive_cache:
                    tgt = self.alive_cache[self.rng.randrange(len(self.alive_cache))]
                    aim = math.atan2(tgt[0] + (tgt[2] / 2 if tgt[6] == "r" else 0) - self.CX, self.B - tgt[1])
                    ang = ang * (1 - self.cur_assist) + clamp(aim, -1.2, 1.2) * self.cur_assist
                self.cang = ang
                self.balls.append(self.new_ball(self.CX + math.sin(ang) * 60, self.B - 30 - math.cos(ang) * 60, math.sin(ang) * self.SPEED, -math.cos(ang) * self.SPEED))
            else:
                x = self.rng.uniform(self.L + 30, self.R - 30)
                if self.cur_assist > 0.05 and self.alive_cache and self.rng.random() < self.cur_assist:
                    tgt = self.alive_cache[self.rng.randrange(len(self.alive_cache))]
                    x = clamp(tgt[0] + (tgt[2] / 2 if tgt[6] == "r" else 0), self.L + 30, self.R - 30)
                self.balls.append(self.new_ball(x, self.T + 10, self.rng.uniform(-60, 60), 0.0))
        self.acc = min(self.acc, 1.0)

    def physics(self, dt):
        self.tick += 1
        if self.tick % 20 == 1:
            self.refresh_alive()
        asst = self.assist()
        cap = int(self.CAP0 + self.CAPK * self.t)
        new = []
        self.cur_assist = asst
        self.spawn(dt)
        for b in self.balls:
            b[4] = self.BR * (1 + self.GROW * self.p)
            self.move(b, dt)
            hits = []
            for e in self.nearby(b[0], b[1], b[4]):
                n = self.touching(e, b[0], b[1], b[4])
                if n:
                    hits.append((e, n))
            if hits:
                for e, n in hits:
                    self.destroy(e, b, new, cap)
                if self.SOLID:
                    n = hits[0][1]
                    if b[2] * n[0] + b[3] * n[1] < 0:
                        b[2], b[3] = reflect(b[2], b[3], n[0], n[1])
                    b[0] += n[0] * 1.5
                    b[1] += n[1] * 1.5
            if len(b[5]) == 0 or self.tick % 6 == 0:
                b[5].append((b[0], b[1]))
                del b[5][:-14]
        self.balls = [b for b in self.balls if not b[6]] + new
        if not self.balls and self.MOTION in ("cannon", "rain"):
            pass

    # -- drawing
    def draw_arena(self, d):
        if self.ARENA == "circle":
            d.ellipse((self.CX - self.RAD, self.CY - self.RAD, self.CX + self.RAD, self.CY + self.RAD), outline=(70, 70, 90), width=4)
        else:
            d.rectangle((self.L, self.T, self.R, self.B), outline=(70, 70, 90), width=4)

    cang = 0.0

    def draw(self, d):
        self.draw_arena(d)
        if self.MOTION == "cannon":
            bx, by = self.CX, self.B - 30
            ex, ey = bx + math.sin(self.cang) * 70, by - math.cos(self.cang) * 70
            d.line((bx, by, ex, ey), fill=(220, 220, 235), width=26)
            d.ellipse((bx - 34, by - 34, bx + 34, by + 34), fill=(90, 90, 110), outline=(220, 220, 235), width=4)
        for e in self.el:
            if e[4]:
                if e[6] == "r":
                    d.rounded_rectangle((e[0], e[1], e[0] + e[2], e[1] + e[3]), radius=min(6, e[2] / 3), fill=e[5])
                else:
                    d.ellipse((e[0] - e[2], e[1] - e[2], e[0] + e[2], e[1] + e[2]), fill=e[5])
        for b in self.balls:
            tr = b[5]
            for i, (x, y) in enumerate(tr[:-1]):
                a = (i + 1) / len(tr) * 0.45
                rr = b[4] * (0.35 + 0.5 * a)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(int(255 * a), int(255 * a), int(255 * a)))
            d.ellipse((b[0] - b[4], b[1] - b[4], b[0] + b[4], b[1] + b[4]), fill=(255, 255, 255))

    def stats(self):
        return [f"BALLS  {len(self.balls)}"]
