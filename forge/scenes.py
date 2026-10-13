"""Illustrated, animated scenes - one per problem family. Everything is drawn from the problem's own numbers:
50 cars means 50 cars on screen, a 12-person handshake draws 12 people and every handshake line, a clock shows the real time.
draw(frame_rgb_image, name, T, theme, params) where T = beat_index + progress_in_beat (float)."""
import math
import random

from PIL import Image, ImageDraw, ImageFont

from . import icons, paths

X0, Y0, X1, Y1 = 60, 352, 1020, 1015          # illustration area (the info row sits below it)
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2
TEXT, DIM, CARD = (255, 255, 255), (150, 160, 200), (18, 24, 58)
_f = {}


def font(sz, bold=True):
    k = (sz, bold)
    if k not in _f:
        _f[k] = ImageFont.truetype(str(paths.FONTS / ("Poppins-ExtraBold.ttf" if bold else "Poppins-SemiBold.ttf")), sz)
    return _f[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def back(x):
    x = clamp(x) - 1
    return 1 + 2.6 * x ** 3 + 1.6 * x ** 2


ARROW_W = 0.9


def _rich(d, s, cx, cy, f, fill, anchor="mm", shadow=False):
    """text with '→' drawn as a real arrow; returns nothing. anchor mm / lm / rm"""
    s = s.replace("->", "→")
    parts = s.split("→")
    sz = f.size
    widths = [d.textlength(p_, font=f) for p_ in parts]
    aw = sz * ARROW_W * 1.25
    total = sum(widths) + aw * (len(parts) - 1)
    x = cx - total / 2 if anchor == "mm" else (cx if anchor == "lm" else cx - total)
    for i, p_ in enumerate(parts):
        if shadow:
            d.text((x + 3, cy + 3), p_, font=f, fill=(0, 0, 0, 170), anchor="lm")
        d.text((x, cy), p_, font=f, fill=fill, anchor="lm")
        x += widths[i]
        if i < len(parts) - 1:
            y0 = cy
            d.line([(x + aw * 0.18, y0), (x + aw * 0.82, y0)], fill=fill, width=max(3, int(sz * 0.09)))
            d.polygon([(x + aw * 0.86, y0), (x + aw * 0.58, y0 - sz * 0.24), (x + aw * 0.58, y0 + sz * 0.24)], fill=fill)
            x += aw


def _tw(d, s, f):
    s = s.replace("->", "→")
    parts = s.split("→")
    return sum(d.textlength(p_, font=f) for p_ in parts) + f.size * ARROW_W * 1.25 * (len(parts) - 1)


class C:
    def __init__(self, im, th, T, P):
        self.im, self.d, self.th, self.T, self.P = im, ImageDraw.Draw(im, "RGBA"), th, T, P

    def a(self, t0, t1):
        """eased 0..1 progress of T between t0 and t1"""
        return ease((self.T - t0) / max(1e-6, t1 - t0))

    def on(self, t0, t1=99):
        return t0 <= self.T < t1

    def ico(self, name, cx, cy, size, col=None, alpha=1.0, flip=False, scale=1.0):
        s = max(8, int(size * scale))
        sp = icons.get(name, s, col)
        if flip:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
        if alpha < 1.0:
            sp = sp.copy()
            sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
        self.im.paste(sp, (int(cx - s / 2), int(cy - s / 2)), sp)

    def txt(self, s, cx, cy, size=48, col=TEXT, bold=True, anchor="mm", shadow=True):
        f = font(size, bold)
        _rich(self.d, s, cx, cy, f, col, {"mm": "mm", "lm": "lm", "rm": "rm"}.get(anchor, "mm"), shadow)

    def box(self, x0, y0, x1, y1, fill=(255, 255, 255, 16), outline=(255, 255, 255, 50), r=22, w=3):
        self.d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=fill, outline=outline, width=w)

    def chip(self, s, cx, cy, col, size=40, pad=26):
        f = font(size)
        w = _tw(self.d, s, f) + pad * 2
        self.d.rounded_rectangle((cx - w / 2, cy - size * 0.85, cx + w / 2, cy + size * 0.85), radius=size, fill=CARD + (235,), outline=col + (255,), width=3)
        _rich(self.d, s, cx, cy, f, col, "mm")

    def line(self, p, q, col, w=4):
        self.d.line([p, q], fill=col, width=w)

    def arrow(self, p, q, col, w=6):
        self.d.line([p, q], fill=col, width=w)
        a = math.atan2(q[1] - p[1], q[0] - p[0])
        for s in (2.6, -2.6):
            self.d.line([q, (q[0] + 26 * math.cos(a + s), q[1] + 26 * math.sin(a + s))], fill=col, width=w)

    def dashed(self, p, q, col, w=3, dash=14):
        L = math.dist(p, q)
        n = int(L / dash)
        for i in range(0, n, 2):
            a, b = i / n, min(1, (i + 1) / n)
            self.d.line([(p[0] + (q[0] - p[0]) * a, p[1] + (q[1] - p[1]) * a), (p[0] + (q[0] - p[0]) * b, p[1] + (q[1] - p[1]) * b)], fill=col, width=w)


def _bars(c, rows, scale, x0=250, y0=470, gap=170, h=86, icons_=None, maxv=None):
    """rows: [(label, [(value, colour, text)...], progress)] horizontal stacked bars"""
    for k, (lab, segs, prog) in enumerate(rows):
        y = y0 + k * gap
        if icons_ and icons_[k]:
            c.ico(icons_[k][0], 130, y + h / 2, 120, icons_[k][1] if len(icons_[k]) > 1 else None)
        x = x0
        for v, col, t in segs:
            w = v * scale * prog
            c.d.rounded_rectangle((x, y, x + max(w, 0), y + h), radius=16, fill=col + (255,), outline=(255, 255, 255, 90), width=3)
            if t and w > 70:
                c.txt(t, x + w / 2, y + h / 2, 40, (16, 22, 52), shadow=False)
            x += w
        if lab and prog > 0.6:
            c.txt(lab, x + 20, y + h / 2, 40, TEXT, anchor="lm")


# ------------------------------------------------------------------ 1 bat & ball
def batball(c):
    P, th = c.P, c.th
    s, D, T = P["s"], P["D"], P["T"]
    big, small = P["big"], P["small"]
    ib, is_ = P["icon_big"], P["icon_small"]
    t = c.T
    money = lambda cents: (f"${cents / 100:.2f}" if cents >= 100 else f"{cents}¢")
    if t < 1.0:
        k = back(t * 2)
        c.ico(ib, 330, 650, 250, scale=k)
        c.ico(is_, 760, 690, 170, scale=k)
        c.txt(big.upper(), 330, 830, 40, th["c"])
        c.txt(small.upper(), 760, 830, 40, th["p"])
        c.chip(f"together {money(T)}", CX, 450, th["y"], 54)
        if t > 0.5:
            c.chip(f"{big} = {small} + {money(D)}", CX, 960, th["c"], 40)
        return
    wrong = T - D
    small_v = {1: wrong, 2: wrong, 3: s, 4: s, 5: s}.get(int(t), s)
    colr = th["r"] if t < 3 else (th["c"] if t < 4 else th["g"])
    grow = c.a(int(t), int(t) + 0.55)
    maxv = max(T * 1.18, 2 * wrong + D + 4)
    scale = 600 / maxv
    segs_small = [(small_v, colr, "x" if 3 <= t < 4 else money(small_v))]
    segs_big = [(small_v, colr, "x" if 3 <= t < 4 else ""), (D, th["y"], money(D))]
    total = [(small_v, colr, ""), (small_v, colr, ""), (D, th["y"], "")]
    rows = [(f"{small}", segs_small, grow), (f"{big}", segs_big, grow), ("together", total, grow)]
    _bars(c, rows, scale, y0=470, icons_=[(is_,), (ib,), None])
    x_t = 250 + T * scale
    c.dashed((x_t, 430), (x_t, 880), th["g"], 4)
    c.txt(money(T), x_t, 405, 38, th["g"])
    if 1 <= t < 2:
        c.txt("10¢ ?", CX, 960, 80, th["r"])
    if 2 <= t < 3 and grow > 0.8:
        c.txt(f"total {money(2 * wrong + D)}", 250 + (2 * wrong + D) * scale, 830, 38, th["r"], anchor="rm")
    if t >= 4:
        c.ico("coin", 900, 960, 110, scale=back(c.a(4, 4.6)))


# ------------------------------------------------------------------ 2 doubling lake
_PADS = None


def lily(c):
    global _PADS
    P, th, t = c.P, c.th, c.T
    N = P["N"]
    cols, rows = 13, 8
    if _PADS is None:
        r = random.Random(7)
        _PADS = [(i % cols, i // cols) for i in range(cols * rows)]
        r.shuffle(_PADS)
    lx0, ly0, lx1, ly1 = 80, 460, 1000, 990
    c.d.rounded_rectangle((lx0, ly0, lx1, ly1), radius=40, fill=(22, 52, 94, 255), outline=(95, 211, 255, 255), width=6)
    # coverage fraction by beat
    if t < 1:
        f = 2 ** (-(N - 1) * (1 - ease(t * 1.1)))
        day = max(1, int(round(N + math.log2(max(f, 1e-9)))))
    elif t < 2:
        f, day = 0.5, "?"
    elif t < 3:
        f, day = 0.5, "24?" if t < 2.8 else ""
    elif t < 4:
        u = c.a(3, 3.5)
        f = 1 - 0.5 * u
        day = N if u < 0.5 else N - 1
    else:
        f, day = (0.5 if t < 4.5 else 1.0), (N - 1 if t < 4.5 else N)
    n_pads = max(1, int(round(f * cols * rows)))
    cw, ch = (lx1 - lx0 - 40) / cols, (ly1 - ly0 - 40) / rows
    for i in range(n_pads):
        gx, gy = _PADS[i]
        c.ico("lily", lx0 + 20 + (gx + 0.5) * cw, ly0 + 20 + (gy + 0.5) * ch, int(ch * 1.25), (60, 200, 100))
    label = f"DAY {day}" if day != "" else ""
    if t < 1 or t >= 3:
        c.chip(label if label else f"DAY {N - 1}", CX, 405, th["y"], 52)
    elif t < 2:
        c.chip("DAY ?", CX, 405, th["p"], 52)
    else:
        c.chip("DAY 24 ?", CX, 405, th["r"], 52)
    if t >= 3:
        c.txt("½" if f <= 0.6 else "FULL", CX, 1030, 64, th["g"] if f > 0.6 else th["y"])


# ------------------------------------------------------------------ 3 machines
def widgets(c):
    P, th, t = c.P, c.th, c.T
    n = P["n"]
    ik = P["item_icon"]
    if t < 2:                                          # n machines, n items, n minutes
        k = back(t)
        gap = 880 / n
        for i in range(n):
            x = 100 + gap * (i + 0.5)
            c.ico("machine", x, 560, min(150, gap * 0.9), scale=k)
            c.ico(ik, x, 740, min(90, gap * 0.55), scale=clamp(t - 0.3 - i * 0.05) * 1.0)
        c.chip(f"{n} machines · {n} minutes · {n} items", CX, 430, th["y"], 40)
        if t >= 1:
            c.txt("100 machines → 100 minutes ?", CX, 930, 48, th["r"])
    elif t < 3:                                        # one machine
        c.ico("machine", CX, 600, 260, scale=back(c.a(2, 2.4)))
        c.ico(ik, CX, 830, 130, scale=back(c.a(2.4, 3.0)))
        c.chip(f"1 machine → 1 item → {n} min", CX, 440, th["y"], 44)
    else:                                              # 100 machines at once
        cols = 10
        sz = 62
        for i in range(100):
            x = CX - (cols - 1) * (sz + 14) / 2 + (i % cols) * (sz + 14)
            y = 470 + (i // cols) * (sz + 14) * 0.95
            vis = clamp((t - 3) * 3 - i * 0.012)
            c.ico("machine", x, y, sz, scale=vis, alpha=0.95)
        c.chip(f"100 machines → 100 items → {n} min", CX, 410, th["g"], 40)


# ------------------------------------------------------------------ 4 round trip
def avgspeed(c):
    P, th, t = c.P, c.th, c.T
    a, b = P["a"], P["b"]
    y = 640
    c.d.rounded_rectangle((120, y - 26, 960, y + 26), radius=26, fill=(48, 52, 76, 255))
    for x in range(150, 940, 70):
        c.line((x, y), (x + 34, y), (255, 232, 140), 5)
    c.ico("tag", 120, y - 175, 100, th["c"])
    c.txt("A", 118, y - 175, 44, (16, 22, 52), shadow=False)
    c.ico("tag", 960, y - 175, 100, th["p"])
    c.txt("B", 958, y - 175, 44, (16, 22, 52), shadow=False)
    # car position: outbound during beat 0.3-1, back during 3-4 (visual story)
    if t < 3:
        pos = ease((t - 0.2) / 0.9) if t < 1.2 else 1.0
        flip = False
    else:
        pos = 1 - ease((t - 3) / 1.0) if t < 4.2 else 0.0
        flip = True
    c.ico("car", 150 + pos * 770, y - 70, 130, th["y"] if not flip else th["g"], flip=flip)
    c.chip(f"there {a} mph", 350, 420, th["y"], 42)
    c.chip(f"back {b} mph", 730, 420, th["g"], 42)
    if 1 <= t < 2:
        c.chip(f"({a}+{b})÷2 = {(a + b) / 2:g} ?", CX, 880, th["r"], 46)
    if t >= 2:                                         # time bars: slower speed takes longer
        tw = 760.0 / (a + b)
        c.txt("same road, so time:", CX, 790, 38, DIM, anchor="mm")
        c.d.rounded_rectangle((150, 830, 150 + b * tw * ease(t - 2), 900), radius=14, fill=th["y"] + (255,))
        c.d.rounded_rectangle((150 + b * tw, 830, 150 + b * tw + a * tw * ease(t - 2.3) + 1, 900), radius=14, fill=th["g"] + (255,))
        c.txt(f"{b} h", 150 + b * tw / 2, 865, 36, (16, 22, 52), shadow=False)
        c.txt(f"{a} h", 150 + b * tw + a * tw / 2, 865, 36, (16, 22, 52), shadow=False)
    if t >= 4:
        c.chip(f"average {P['avg']:g} mph", CX, 980, th["g"], 54)


# ------------------------------------------------------------------ 5 handshakes
def handshake(c):
    P, th, t = c.P, c.th, c.T
    n = P["n"]
    R = 285
    cx, cy = CX, 680
    pts = [(cx + R * math.sin(2 * math.pi * i / n), cy - R * math.cos(2 * math.pi * i / n)) for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    if t < 1:
        shown = n
    else:
        shown = n
    # lines
    if 1 <= t < 2:                                     # one person shakes everybody
        k = int(c.a(1, 1.9) * (n - 1))
        for j in range(1, 1 + k):
            c.line(pts[0], pts[j], th["y"] + (255,), 5)
        c.chip(f"1 person → {n - 1} hands", CX, 1000, th["y"], 44)
    elif 2 <= t < 3:
        for (i, j) in pairs[: int(len(pairs) * 0.35)]:
            c.line(pts[i], pts[j], (255, 255, 255, 40), 2)
        i, j = 0, 1
        c.line(pts[i], pts[j], th["r"] + (255,), 8)
        c.chip("each handshake counted twice", CX, 1000, th["r"], 40)
    elif t >= 3:
        k = int(c.a(3, 3.9) * len(pairs))
        for (i, j) in pairs[:k]:
            c.line(pts[i], pts[j], th["g"] + (210,), 3 if n > 12 else 4)
        c.chip(f"{n}×{n - 1} ÷ 2 = {P['tot']}", CX, 1000, th["g"], 50)
    sz = int(clamp(600 / n, 60, 150))
    for i in range(n):
        c.ico("person", pts[i][0], pts[i][1], sz, [th["c"], th["p"], th["g"], th["y"]][i % 4], scale=back(t * 2.5 - i * 0.08))


# ------------------------------------------------------------------ 6 percent up / down
def percent(c):
    P, th, t = c.P, c.th, c.T
    price, up, down, p = P["price"], P["up"], P["down"], P["p"]
    base_y = 960
    sc = 470.0 / max(up, price)
    xs = [260, 540, 820]
    vals = [price, up, down]
    cols = [th["c"], th["g"], th["p"]]
    labels = [f"${price}", f"+{p}%  ${up}", f"-{p}%  ${down}"]
    vis = [1.0, c.a(2, 2.6), c.a(3, 3.6)]
    for k in range(3):
        h = vals[k] * sc * vis[k]
        c.d.rounded_rectangle((xs[k] - 80, base_y - h, xs[k] + 80, base_y), radius=18, fill=cols[k] + (255,), outline=(255, 255, 255, 90), width=3)
        if vis[k] > 0.5:
            c.txt(labels[k], xs[k], base_y - h - 40, 40, cols[k])
    c.dashed((150, base_y - price * sc), (940, base_y - price * sc), th["y"], 4)
    if 1 <= t < 2:
        c.chip(f"back to ${price}?", 820, base_y - price * sc - 120, th["r"], 40)
    if t >= 4:
        gap = (price - down) * sc
        c.d.rectangle((915, base_y - price * sc, 945, base_y - price * sc + gap), fill=th["r"] + (255,))
        c.chip(f"${price - down} below the start", CX, 1010, th["r"], 46)


# ------------------------------------------------------------------ 7 fence posts
def fence(c):
    P, th, t = c.P, c.th, c.T
    gaps = P["gaps"]
    n = gaps + 1
    x0, x1, y = 130, 950, 760
    c.d.rounded_rectangle((x0 - 40, y + 70, x1 + 40, y + 100), radius=12, fill=(60, 120, 70, 255))
    for i in range(n):
        x = x0 + (x1 - x0) * i / gaps
        appear = back((t - 0.2) * 3 - i * 0.12) if t >= 3 else (1.0 if t < 2 or i in (0, gaps) else 0.0)
        if t >= 2 and t < 3:
            appear = 1.0 if i in (0, 1, gaps) else 0.35
        c.d.rounded_rectangle((x - 14, y - 110 * appear, x + 14, y + 80), radius=8, fill=(190, 140, 85, 255), outline=(110, 70, 35, 255), width=3)
        if t >= 3:
            c.txt(str(i + 1), x, y - 150, 34, th["y"])
    for i in range(gaps):
        xa, xb = x0 + (x1 - x0) * i / gaps, x0 + (x1 - x0) * (i + 1) / gaps
        col = th["r"] if 1 <= t < 3 else th["c"]
        c.d.rectangle((xa + 14, y - 60, xb - 14, y - 40), fill=(150, 100, 55, 255))
        c.d.rectangle((xa + 14, y - 10, xb - 14, y + 10), fill=(150, 100, 55, 255))
        if 1 <= t < 2:
            c.txt(str(i + 1), (xa + xb) / 2, y - 190, 34, col)
    c.chip(f"{P['L']} m  ·  every {P['s']} m", CX, 450, th["y"], 46)
    if 1 <= t < 2:
        c.chip(f"{gaps} gaps ≠ posts", CX, 1000, th["r"], 46)
    if t >= 3:
        c.chip(f"{gaps} gaps + 1 = {n} posts", CX, 1000, th["g"], 50)


# ------------------------------------------------------------------ 8 climbing animal
def frog(c):
    P, th, t = c.P, c.th, c.T
    d, a, b, days = P["d"], P["a"], P["b"], P["days"]
    wx0, wx1, wy0, wy1 = 330, 750, 400, 940
    c.d.rounded_rectangle((wx0, wy0, wx1, wy1), radius=18, fill=(30, 36, 70, 255), outline=(150, 160, 200, 255), width=6)
    sc = (wy1 - wy0 - 40) / d
    for m in range(0, d + 1):
        yy = wy1 - 20 - m * sc
        c.line((wx0 + 6, yy), (wx0 + (36 if m % 5 else 70), yy), (150, 160, 200, 255), 3)
        if m % (1 if d <= 12 else 5) == 0:
            c.txt(f"{m}", wx0 - 40, yy, 28, DIM, shadow=False)
    # path keyframes: (height after climb, height after slip)
    h, keys = 0, []
    for day in range(1, days + 1):
        top = min(h + a, d)
        keys.append((day, h, top))
        h = top - b if top < d else top
        keys[-1] = (day, keys[-1][1], top, h)
    if t < 2:
        cur, day = 0, 1
    elif t >= 4:
        cur, day = d, days
    else:
        u = (t - 2) / 2 * days
        k = min(days - 1, int(u))
        v = u - k
        _, h0, top, h1 = keys[k]
        cur = h0 + (top - h0) * ease(v * 2) if v < 0.5 else top + (h1 - top) * ease((v - 0.5) * 2)
        day = k + 1
    c.ico("critter", (wx0 + wx1) / 2, wy1 - 20 - cur * sc - 40, 90, P["col"])
    c.chip(f"day {day}", 880, 520, th["y"], 40)
    c.chip(f"+{a} / −{b}", 190, 520, th["c"], 40)
    if t >= 4:
        c.chip(f"{days} days", CX, 1000, th["g"], 54)
    elif 1 <= t < 2:
        c.chip(f"{d} ÷ {a - b} ?", CX, 1000, th["r"], 46)


# ------------------------------------------------------------------ 9 teamwork
def work(c):
    P, th, t = c.P, c.th, c.T
    a, b, tg = P["a"], P["b"], P["tg"]
    tau = max(a, b)
    prog = clamp((t - 2.0) / 2.6) * tau if t >= 2 else 0
    rows = [("Sam", a, th["c"], th["c"]), ("Alex", b, th["p"], th["p"]), ("Together", tg, th["g"], th["g"])]
    for k, (nm, tm, col, pc) in enumerate(rows):
        y = 470 + k * 190
        if k < 2 or t >= 2.6:
            c.ico("person", 120, y + 40, 130 if k < 2 else 150, pc if k < 2 else None)
            if k == 2:
                c.ico("person", 190, y + 40, 130, th["p"])
        c.d.rounded_rectangle((300, y, 960, y + 84), radius=22, fill=(30, 36, 70, 255), outline=(150, 160, 200, 255), width=3)
        frac = clamp(prog / tm) if t >= 2 and (k < 2 or t >= 3) else (0.0 if k == 2 else clamp(prog / tm))
        if frac > 0:
            c.d.rounded_rectangle((304, y + 4, 304 + 652 * frac, y + 80), radius=18, fill=col + (255,))
        c.txt(f"{nm}: {tm:g} h" if k < 2 else f"{nm}: {tg:g} h", 320, y - 28, 34, col, anchor="lm")
        if frac >= 1:
            c.txt("✓".replace("✓", "DONE"), 940, y + 42, 34, (16, 22, 52), anchor="rm", shadow=False)
    if t >= 2 and t < 3:
        c.chip("rate = job ÷ time", CX, 395, th["y"], 40)


# ------------------------------------------------------------------ 10 dehydrated watermelon
def water(c):
    P, th, t = c.P, c.th, c.T
    m, p1, p2, solid, new = P["m"], P["p1"], P["p2"], float(P["solid"]), float(P["new"])
    base, H = 980, 470
    sc = H / m
    def col_(x, total, w_pct, label, vis, ghost=False):
        h = total * sc * vis
        hs = max(14.0, solid * sc * vis)
        c.d.rounded_rectangle((x - 110, base - h, x + 110, base), radius=22, fill=(60, 140, 255, 120 if ghost else 255), outline=(255, 255, 255, 120), width=3)
        c.d.rounded_rectangle((x - 110, base - hs, x + 110, base), radius=22, fill=th["g"] + ((90,) if ghost else (255,)))
        c.txt(label, x, base - h - 44, 40, TEXT)
        c.txt(f"{w_pct}% water", x, base - h / 2 - 20, 34, (240, 244, 255), shadow=False)
    col_(300, m, p1, f"{m} kg", c.a(0, 0.8))
    if 1 <= t < 2:
        col_(700, m - 1, p2, "≈ same?", c.a(1, 1.6), ghost=True)
    if t >= 3:
        col_(700, new, p2, f"{new:g} kg", c.a(3, 3.8))
    if 2 <= t < 5:
        c.chip(f"solid = {solid:g} kg (never changes)", CX, 392, th["g"], 36)
    if t >= 4:
        c.chip(f"{solid:g} ÷ {100 - p2}% = {new:g} kg", CX, 1000, th["y"], 46)


# ------------------------------------------------------------------ 11 clock
def clock(c):
    P, th, t = c.P, c.th, c.T
    h, m = P["h"], P["m"]
    cx, cy, R = CX, 705, 265
    c.d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(245, 247, 255, 255), outline=(150, 160, 200, 255), width=10)
    for i in range(60):
        a = math.radians(i * 6)
        r0 = R - (34 if i % 5 == 0 else 16)
        c.line((cx + r0 * math.sin(a), cy - r0 * math.cos(a)), (cx + (R - 6) * math.sin(a), cy - (R - 6) * math.cos(a)), (40, 44, 80, 255), 6 if i % 5 == 0 else 2)
    for n in (12, 3, 6, 9):
        a = math.radians(n * 30)
        c.txt(str(n), cx + (R - 70) * math.sin(a), cy - (R - 70) * math.cos(a), 54, (30, 34, 70), shadow=False)
    mu = c.a(1, 1.8) if t < 2 else 1.0
    hu = c.a(2, 2.8) if t < 3 else 1.0
    hour_ang = (30 * (h % 12) + 0.5 * m) * hu
    min_ang = (6 * m) * mu if t >= 1 else 0
    # shaded gap
    if t >= 3:
        a0, a1 = sorted((hour_ang % 360, min_ang % 360))
        d_ = a1 - a0
        s_, e_ = (a0, a1) if d_ <= 180 else (a1, a0 + 360)
        c.d.pieslice((cx - R + 40, cy - R + 40, cx + R - 40, cy + R - 40), s_ - 90, e_ - 90, fill=th["y"] + (110,))
    c.line((cx, cy), (cx + (R - 90) * math.sin(math.radians(hour_ang)), cy - (R - 90) * math.cos(math.radians(hour_ang))), th["p"] + (255,), 18)
    c.line((cx, cy), (cx + (R - 40) * math.sin(math.radians(min_ang)), cy - (R - 40) * math.cos(math.radians(min_ang))), th["c"] + (255,), 12)
    c.d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(30, 34, 70, 255))
    c.chip(f"{h}:{m:02d}", CX, 385, th["y"], 52)
    if 1 <= t < 2:
        c.chip(f"minute hand {6 * m}°", CX, 1000, th["c"], 40)
    elif 2 <= t < 3:
        c.chip(f"hour hand {30 * h + 0.5 * m:g}°", CX, 1000, th["p"], 40)
    elif t >= 3:
        c.chip(f"angle {P['ang']:g}°", CX, 1000, th["g"], 54)


# ------------------------------------------------------------------ 12 all but n
def allbut(c):
    P, th, t = c.P, c.th, c.T
    tot, n = P["tot"], P["n"]
    cols = 10 if tot > 40 else 7
    rows = math.ceil(tot / cols)
    sz = int(min(100, 880 / cols, 520 / rows))
    for i in range(tot):
        x = CX - (cols - 1) * sz * 1.06 / 2 + (i % cols) * sz * 1.06
        y = 560 + (i // cols) * sz * 0.98
        keep = i < n
        al, dx = 1.0, 0.0
        if t >= 2:
            u = c.a(2, 3.0)
            if not keep:
                dx, al = u * 700, 1 - u
        c.ico("sheep", x + dx, y, sz, P["col"], alpha=al, scale=back(t * 2.5 - i * 0.03))
        if keep and t >= 2.4:
            c.d.ellipse((x - sz * 0.55, y - sz * 0.55, x + sz * 0.55, y + sz * 0.55), outline=th["g"] + (255,), width=5)
    c.chip(f"{tot} {P['animal']} · all but {n} run away", CX, 420, th["y"], 40)
    if t >= 3:
        c.chip(f"{n} left", CX, 1000, th["g"], 58)
    elif 1 <= t < 2:
        c.chip(f"{tot} − {n} = {tot - n} ?", CX, 1000, th["r"], 46)


# ------------------------------------------------------------------ 13 socks
def socks(c):
    P, th, t = c.P, c.th, c.T
    n = P["c"]
    pal = [(255, 92, 138), (95, 211, 255), (125, 255, 138), (255, 216, 77), (190, 130, 255), (255, 150, 60),
           (60, 220, 200), (240, 240, 240), (170, 110, 70), (255, 120, 220), (130, 140, 255), (200, 255, 80)][:n]
    c.d.rounded_rectangle((140, 600, 940, 980), radius=30, fill=(40, 44, 76, 255), outline=(150, 160, 200, 255), width=6)
    c.txt("DRAWER (lights off)", CX, 650, 36, DIM, shadow=False)
    r = random.Random(3)
    for i in range(n * 4):
        x, y = 190 + (i * 97) % 700 + r.randint(-12, 12), 700 + ((i * 53) % 220)
        c.ico("sock", x, y, 96, pal[i % n], alpha=0.55 if t >= 2 else 1.0)
    pulled = n if t >= 2 else 0
    if t >= 2:
        for i in range(n):
            u = back(c.a(2, 3) * (n + 1) - i * 0.9)
            c.ico("sock", 160 + i * (780 / max(n, 1)), 470, 110, pal[i], scale=clamp(u, 0, 1.2))
        c.chip(f"worst case: {n} socks, no pair", CX, 1020, th["y"], 38)
    if t >= 3:
        u = c.a(3, 3.6)
        x0 = 160
        c.ico("sock", x0 + 86, 470, 110, pal[0], scale=back(u))
        c.d.ellipse((x0 - 62, 400, x0 + 150, 540), outline=th["g"] + (255,), width=6)
        c.ico("sock", x0 + 150, 400, 54, th["g"]) if False else None
        c.chip(f"{n + 1} socks = pair guaranteed", CX, 1020, th["g"], 44)


# ------------------------------------------------------------------ 14 doubling reward
def wheat(c):
    P, th, t = c.P, c.th, c.T
    n = P["n"]
    show = min(n, 12)
    cols = 6
    sz = 120
    for i in range(show):
        x = CX - (cols - 1) * (sz + 14) / 2 + (i % cols) * (sz + 14)
        y = 520 + (i // cols) * (sz + 90)
        vis = clamp((t * 4 - i * 0.7)) if t < 3 else 1.0
        sq = (220, 224, 240) if (i + i // cols) % 2 else (90, 100, 150)
        c.d.rectangle((x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2), fill=sq + (255,))
        grains = 2 ** i
        if vis > 0:
            rad = min(sz * 0.42, 8 + 6 * math.log2(grains + 1)) * vis
            c.d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(255, 216, 77, 255))
            c.txt(str(grains), x, y + sz / 2 + 24, 30, th["y"], shadow=False)
    if n > 12:
        c.txt(f"… {n} squares", CX, 960, 44, DIM)
    if t >= 2:
        c.chip(f"square {n} = {2 ** (n - 1):,} grains", CX, 420, th["p"], 38)
    if t >= 3:
        c.chip(f"total = {P['tot']:,}", CX, 1020, th["g"], 52)


# ------------------------------------------------------------------ 15 coupon order
def discount(c):
    P, th, t = c.P, c.th, c.T
    d, cp, price, A, Bv = P["d"], P["c"], P["price"], P["A"], P["B"]
    lanes = [("percent first", [f"${price}", f"-{d}%", f"-${cp}"], [price, price * (100 - d) // 100, A], th["c"], 2.0),
             ("coupon first", [f"${price}", f"-${cp}", f"-{d}%"], [price, price - cp, Bv], th["g"], 3.0)]
    for k, (nm, ops, vals, col, t0) in enumerate(lanes):
        y = 520 + k * 270
        c.txt(nm, 100, y - 70, 38, col, anchor="lm")
        steps = clamp((t - t0) * 3.2 + (1 if t >= 1 else 0), 0, 3) if t >= 1 else 1
        for i in range(3):
            x = 190 + i * 340
            vis = back(steps - i)
            c.ico("tag", x, y + 20, 150, col if i < 2 else (th["y"]), scale=clamp(vis, 0, 1.15))
            c.txt(f"${vals[i]}", x, y + 20, 40, (16, 22, 52), shadow=False)
            if i < 2 and vis > 0.5:
                c.arrow((x + 90, y + 20), (x + 250, y + 20), TEXT, 6)
                c.txt(ops[i + 1], x + 170, y - 30, 34, th["y"])
    if t >= 4:
        c.chip(f"percent first saves ${Bv - A}", CX, 1000, th["g"], 48)


# ------------------------------------------------------------------ 16 race
def race(c):
    P, th, t = c.P, c.th, c.T
    pos = P["pos"]
    n = pos + 2
    cols = [th["c"], th["p"], th["g"], th["y"], (190, 130, 255), (255, 150, 60), (120, 220, 230), (255, 120, 120), (180, 200, 120), (160, 160, 255), (255, 180, 200), (200, 200, 200)]
    slot = lambda k: 160 + k * (760 / max(1, n - 1))
    for k in range(n):
        idx = k + 1
        if idx == pos:        # the runner being passed: slips back one place
            x = slot(k) + (slot(k + 1) - slot(k)) * c.a(2, 3)
            col = th["r"]
        elif idx == pos + 1:  # you
            x = slot(k) - (slot(k) - slot(k - 1)) * c.a(2, 3)
            col = th["y"]
        else:
            x = slot(k)
            col = cols[k % len(cols)]
        c.ico("runner", x, 720 - (30 if idx == pos + 1 else 0), 150, col)
        if idx == pos + 1:
            c.ico("star", x, 580, 60, th["y"])
            c.txt("YOU", x, 840, 34, th["y"])
    for k in range(n):
        c.txt(str(k + 1), slot(k), 930, 44, DIM)
    if t >= 3:
        c.chip(f"you are now #{pos}", CX, 1010, th["g"], 54)
    elif t >= 1:
        c.chip(f"you pass #{pos}", CX, 460, th["y"], 44)


# ------------------------------------------------------------------ 17 ages
def age(c):
    P, th, t = c.P, c.th, c.T
    k, tot, s = P["k"], P["tot"], P["s"]
    c.ico("person", 200, 520, 130, th["c"])
    c.txt("son", 200, 610, 34, th["c"])
    c.ico("person", 440, 480, 210, th["p"])
    c.txt("father", 440, 610, 34, th["p"])
    if t >= 1:
        unit = 760.0 / (k + 1)
        u = c.a(1, 2.0)
        c.d.rounded_rectangle((150, 740, 150 + unit - 6, 820), radius=14, fill=th["c"] + (255,))
        c.txt("x" if t < 3 else str(s), 150 + unit / 2, 780, 40, (16, 22, 52), shadow=False)
        for i in range(k):
            xx = 150 + unit * (i + 1)
            if u * (k + 1) > i + 1:
                c.d.rounded_rectangle((xx, 740, xx + unit - 6, 820), radius=14, fill=th["p"] + (255,))
                c.txt("x" if t < 3 else str(s), xx + unit / 2, 780, 40, (16, 22, 52), shadow=False)
        c.dashed((150, 860), (150 + (k + 1) * unit, 860), TEXT, 4)
        c.txt(f"{k + 1}x = {tot}" if t < 3 else f"{k + 1} × {s} = {tot}", CX, 920, 54, th["y"])
    if t >= 4:
        c.chip(f"son {s} · father {s * k}", CX, 1010, th["g"], 46)


# ------------------------------------------------------------------ 18 missing dollar
def missing(c):
    P, th, t = c.P, c.th, c.T
    p, Rm, ref, each = P["p"], P["Rm"], P["ref"], P["each"]
    T = 3 * p
    for i, col in enumerate([th["c"], th["p"], th["g"]]):
        c.ico("person", 230 + i * 310, 520, 150, col, scale=back(t * 3 - i * 0.3))
        if t < 2 or t >= 5:
            c.ico("bill", 230 + i * 310, 650, 90, scale=clamp(t * 2 - 0.4))
            c.txt(f"${p}", 230 + i * 310, 730, 36, th["y"])
    if t >= 1 and t < 3:
        c.chip(f"room ${Rm}", 300, 430, th["c"], 38)
        c.chip(f"refund ${ref}", 780, 430, th["g"], 38)
    if 2 <= t < 3:
        c.chip(f"bellboy keeps $2", 300, 900, th["p"], 38)
        c.chip(f"each friend +${each}", 780, 900, th["g"], 38)
    if 3 <= t < 5:
        paid = 3 * (p - each)
        c.txt(f"3 × ${p - each} = ${paid}", CX, 760, 66, th["y"])
        c.txt(f"+ $2 = ${paid + 2}", CX, 870, 66, th["r"] if t >= 3.5 else th["y"])
        if t >= 4:
            c.chip("$1 missing?!", CX, 1000, th["r"], 56)
    if t >= 5:
        unit = 700.0 / T
        paid = 3 * (p - each)
        x = 190
        c.d.rounded_rectangle((x, 820, x + Rm * unit, 910), radius=14, fill=th["c"] + (255,))
        c.txt(f"room ${Rm}", x + Rm * unit / 2, 865, 36, (16, 22, 52), shadow=False)
        c.d.rounded_rectangle((x + Rm * unit, 820, x + paid * unit, 910), radius=14, fill=th["p"] + (255,))
        c.d.rounded_rectangle((x + paid * unit, 820, x + T * unit, 910), radius=14, fill=th["g"] + (255,))
        c.chip(f"${paid} paid + ${T - paid} refund = ${T}", CX, 1000, th["g"], 44)


# ------------------------------------------------------------------ 19 trains & fly
def fly(c):
    P, th, t = c.P, c.th, c.T
    D, s1, s2 = P["D"], P["s1"], P["s2"]
    y = 700
    c.d.rounded_rectangle((90, y + 60, 990, y + 78), radius=8, fill=(90, 96, 130, 255))
    for x in range(100, 980, 40):
        c.d.rectangle((x, y + 52, x + 12, y + 86), fill=(120, 126, 160, 255))
    prog = clamp((t - 2.6) / 1.6) if t >= 2.6 else 0.0
    xa = 150 + prog * 330
    xb = 930 - prog * 330
    c.ico("train", xa, y, 190, th["c"])
    c.ico("train", xb, y, 190, th["p"], flip=True)
    c.chip(f"{s1} mph", 190, 540, th["c"], 36)
    c.chip(f"{s2} mph", 890, 540, th["p"], 36)
    c.chip(f"{D} miles", CX, 450, th["y"], 40)
    # fly zig-zag
    if t >= 1:
        vf = 6.0
        L0 = (930 - 150)
        tt = prog
        # simulate bounces between fronts
        def front(tt_):
            return 150 + tt_ * 330 + 95, 930 - tt_ * 330 - 95
        pos_t, x_, going = 0.0, front(0)[0], True
        px = x_
        T_end = prog
        steps = 0
        while pos_t < T_end and steps < 40:
            xa_, xb_ = front(pos_t)
            gap = xb_ - xa_
            if gap < 8:
                break
            tgt_time = pos_t + gap / (vf * 330 + 330)
            tgt_time = min(tgt_time, T_end)
            xa2, xb2 = front(tgt_time)
            px = xb2 if going else xa2
            pos_t = tgt_time
            going = not going
            steps += 1
        c.ico("fly", px, y - 140 + 18 * math.sin(t * 20), 70, flip=not going)
    if t >= 3:
        c.chip(f"meet in {P['t']:g} h", CX, 930, th["y"], 44)
    if t >= 4:
        c.chip(f"fly: {P['fl']} mph × {P['t']:g} h = {P['dist']:g} mi", CX, 1010, th["g"], 40)


# ------------------------------------------------------------------ 20 stack of logs
def logs(c):
    P, th, t = c.P, c.th, c.T
    n = P["n"]
    rows = min(n, 12)
    sz = int(min(70, 420 / rows * 1.15))
    y0 = 540
    for r in range(rows):
        cnt = n - r if n <= 12 else rows - r
        vis = clamp(t * 2.2 - r * 0.25) if t < 2 else 1.0
        for i in range(cnt):
            x = CX - (cnt - 1) * sz * 1.02 / 2 + i * sz * 1.02
            y = y0 + (rows - 1 - r) * sz * 0.92
            c.ico("log", x, y, sz, scale=vis)
    if n > 12:
        c.txt(f"… {n} on the bottom row", CX, 960, 40, DIM)
    if 2 <= t < 4:
        c.chip(f"1 + {n} = {n + 1}   2 + {n - 1} = {n + 1}", CX, 420, th["y"], 40)
    if t >= 4:
        c.chip(f"{n} × {n + 1} ÷ 2 = {P['tot']}", CX, 1010, th["g"], 54)


# ------------------------------------------------------------------ 21 pizza cuts
def pizza(c):
    P, th, t = c.P, c.th, c.T
    n = P["n"]
    cx, cy, R = CX, 660, 270
    c.ico("pizza", cx, cy, 2 * R)
    shown = int(clamp((t - 1.5) / 2.5) * n + 0.0001) if t >= 1.5 else 0
    shown = min(n, shown + (1 if t >= 1.5 else 0))
    for i in range(shown):
        ang = math.pi * (i / n) + 0.35
        off = 70 * math.sin(i * 2.1 + 0.8)
        dx, dy = math.cos(ang), math.sin(ang)
        px, py = cx - dy * off, cy + dx * off
        c.line((px - dx * R * 1.0, py - dy * R * 1.0), (px + dx * R * 1.0, py + dy * R * 1.0), (255, 255, 255, 255), 8)
    pieces = shown * (shown + 1) // 2 + 1
    c.chip(f"{shown} cut{'s' if shown != 1 else ''} → {pieces} pieces" if shown else f"{n} cuts · most pieces?", CX, 420, th["y"], 46)
    if t >= 4:
        c.chip(f"{n}×{n + 1} ÷ 2 + 1 = {P['pieces']}", CX, 1010, th["g"], 52)
    elif 1 <= t < 2:
        c.chip(f"{2 * n} ?", CX, 1010, th["r"], 52)


# ------------------------------------------------------------------ 22 birthday paradox
def birthday(c):
    P, th, t = c.P, c.th, c.T
    n = P["n"]
    cols, rows = 30, 13
    sz = 28
    gx0, gy0 = CX - cols * (sz + 4) / 2, 470
    r = random.Random(11)
    days = r.sample(range(cols * rows - 25), n - 1)
    clash = days[len(days) // 2]
    taken = days + [clash]
    k = int(c.a(0.2, 2.6) * n) if t < 3 else n
    for i in range(cols * rows):
        x = gx0 + (i % cols) * (sz + 4)
        y = gy0 + (i // cols) * (sz + 4)
        if i >= 365:
            continue
        col = (60, 66, 104)
        c.d.rounded_rectangle((x, y, x + sz, y + sz), radius=6, fill=col + (255,))
    for j in range(min(k, n)):
        i = taken[j]
        x = gx0 + (i % cols) * (sz + 4)
        y = gy0 + (i // cols) * (sz + 4)
        hit = (j == n - 1) and t >= 2.6
        c.d.rounded_rectangle((x, y, x + sz, y + sz), radius=6, fill=(th["r"] if hit else th["y"]) + (255,))
    c.chip(f"{n} people · 365 days", CX, 410, th["c"], 40)
    if 1 <= t < 2:
        c.chip("looks unlikely…", CX, 1010, th["r"], 46)
    elif 2 <= t < 3:
        c.chip(f"{n * (n - 1) // 2} pairs to compare", CX, 1010, th["y"], 46)
    elif t >= 3:
        c.chip(f"{P['ps']}% chance of a match", CX, 1010, th["g"], 52)


# ------------------------------------------------------------------ 23 monty hall
def monty(c):
    P, th, t = c.P, c.th, c.T
    n = P["n"]
    r = random.Random(5)
    pick, other = 0, min(n - 1, max(1, (n // 2)))
    car = other if True else pick
    cols = n if n <= 5 else 10
    rows = math.ceil(n / cols)
    sz = int(min(170, 900 / cols, 520 / rows))
    for i in range(n):
        x = CX - (cols - 1) * sz * 1.08 / 2 + (i % cols) * sz * 1.08
        y = 640 + (i // cols) * sz * 1.12
        opened = t >= 1 and i not in (pick, other) and c.a(1, 1.4 + 0.02 * i) > 0.5
        if opened:
            c.d.rounded_rectangle((x - sz * 0.38, y - sz * 0.46, x + sz * 0.38, y + sz * 0.46), radius=10, fill=(30, 36, 70, 255))
            c.ico("goat", x, y, sz * 0.8)
        else:
            c.ico("door", x, y, sz, th["y"] if i == pick else (th["c"] if (i == other and t >= 3) else (150, 110, 70)))
            if n <= 10:
                c.txt(str(i + 1), x, y, int(sz * 0.4), (255, 255, 255), shadow=False)
    if t >= 0.4:
        c.chip("your pick", CX - (cols - 1) * sz * 1.08 / 2, 640 + sz * 0.68 + (rows - 1) * sz * 1.12, th["y"], 30)
    if t >= 3:
        c.chip(f"stay 1/{n}", 300, 1010, th["r"], 46)
        c.chip(f"switch {n - 1}/{n}", 760, 1010, th["g"], 46)
    elif 1 <= t < 3:
        c.chip(f"host opens {n - 2} goat door{'s' if n != 3 else ''}", CX, 420, th["p"], 40)


SCENES = {k: v for k, v in globals().items() if k in (
    "batball", "lily", "widgets", "avgspeed", "handshake", "percent", "fence", "frog", "work", "water", "clock", "allbut", "socks", "wheat",
    "discount", "race", "age", "missing", "fly", "logs", "pizza", "birthday", "monty")}


def draw(frame, name, T, th, params):
    fn = SCENES.get(name)
    if fn:
        fn(C(frame, th, T, params))
