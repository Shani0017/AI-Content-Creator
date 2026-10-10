"""Small vector-style illustrations drawn with Pillow (4x supersampled, cached). Every icon is original artwork.
get(name, size, color=None) -> RGBA image (size x size)."""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

SS = 4


def _canvas(size):
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), s / 100.0


def _c(col, k=1.0):
    return tuple(max(0, min(255, int(v * k))) for v in col[:3])


def shade(col, k):
    return _c(col, k)


def lighten(col, k=0.35):
    return tuple(int(v + (255 - v) * k) for v in col[:3])


DEF = {"car": (255, 92, 138), "person": (95, 211, 255), "ball": (255, 92, 138), "sheep": (240, 240, 250), "machine": (95, 211, 255),
       "critter": (125, 255, 138)}


def _rr(d, u, x0, y0, x1, y1, r, fill, outline=None, w=0):
    d.rounded_rectangle((x0 * u, y0 * u, x1 * u, y1 * u), radius=r * u, fill=fill, outline=outline, width=int(w * u))


def _el(d, u, x0, y0, x1, y1, fill, outline=None, w=0):
    d.ellipse((x0 * u, y0 * u, x1 * u, y1 * u), fill=fill, outline=outline, width=int(w * u))


def _poly(d, u, pts, fill, outline=None):
    d.polygon([(x * u, y * u) for x, y in pts], fill=fill, outline=outline)


def _line(d, u, pts, fill, w):
    d.line([(x * u, y * u) for x, y in pts], fill=fill, width=int(w * u), joint="curve")


# ------------------------------------------------------------------ drawers
def car(d, u, col):
    body = col
    _rr(d, u, 6, 46, 94, 72, 9, body)
    _poly(d, u, [(22, 46), (32, 26), (68, 26), (80, 46)], shade(body, 0.85))
    _poly(d, u, [(28, 44), (36, 30), (49, 30), (49, 44)], (190, 232, 255))
    _poly(d, u, [(53, 44), (53, 30), (65, 30), (74, 44)], (190, 232, 255))
    _rr(d, u, 86, 52, 94, 60, 3, (255, 232, 140))
    _rr(d, u, 6, 54, 12, 62, 3, (255, 90, 90))
    for cx in (28, 73):
        _el(d, u, cx - 10, 62, cx + 10, 82, (30, 32, 44))
        _el(d, u, cx - 5, 67, cx + 5, 77, (190, 196, 220))


def person(d, u, col):
    _el(d, u, 34, 6, 66, 38, (255, 214, 170))
    _rr(d, u, 24, 42, 76, 96, 18, col)
    _el(d, u, 43, 18, 47, 22, (40, 30, 30))
    _el(d, u, 53, 18, 57, 22, (40, 30, 30))
    _line(d, u, [(44, 28), (50, 31), (56, 28)], (140, 70, 60), 1.8)
    _rr(d, u, 34, 4, 66, 16, 6, shade(col, 0.55))


def ball(d, u, col):
    _el(d, u, 6, 6, 94, 94, col, (255, 255, 255), 3)
    d.arc((-30 * u, 20 * u, 40 * u, 80 * u), -60, 60, fill=(255, 255, 255), width=int(3 * u))
    d.arc((60 * u, 20 * u, 130 * u, 80 * u), 120, 240, fill=(255, 255, 255), width=int(3 * u))


def bat(d, u, col):
    _poly(d, u, [(10, 82), (16, 90), (62, 40), (54, 32)], (230, 175, 100))
    _rr(d, u, 52, 14, 90, 52, 12, (230, 175, 100))
    _line(d, u, [(10, 86), (18, 78)], (110, 70, 30), 5)


def pen(d, u, col):
    _poly(d, u, [(12, 88), (20, 80), (84, 16), (92, 24), (28, 88), (12, 92)], col)
    _poly(d, u, [(12, 88), (20, 80), (28, 88)], (60, 60, 70))
    _poly(d, u, [(78, 14), (86, 8), (94, 16), (88, 22)], (230, 230, 240))


def eraser(d, u, col):
    _rr(d, u, 10, 30, 90, 72, 8, (255, 160, 190))
    _rr(d, u, 10, 30, 42, 72, 8, (95, 150, 255))


def burger(d, u, col):
    _rr(d, u, 10, 14, 90, 44, 20, (230, 160, 70))
    _rr(d, u, 8, 46, 92, 56, 5, (110, 220, 110))
    _rr(d, u, 10, 56, 90, 70, 6, (120, 70, 40))
    _rr(d, u, 10, 72, 90, 90, 10, (230, 160, 70))


def fries(d, u, col):
    for i, x in enumerate(range(22, 82, 10)):
        _rr(d, u, x, 8 + (i % 3) * 5, x + 8, 66, 2, (255, 210, 80))
    _poly(d, u, [(16, 50), (84, 50), (76, 94), (24, 94)], (255, 92, 92))


def phone(d, u, col):
    _rr(d, u, 28, 4, 72, 96, 9, (40, 44, 64))
    _rr(d, u, 32, 12, 68, 84, 4, col)
    _el(d, u, 46, 87, 54, 94, (180, 186, 210))


def case(d, u, col):
    _rr(d, u, 22, 4, 78, 96, 14, col)
    _rr(d, u, 30, 12, 70, 88, 8, (30, 34, 54))
    _el(d, u, 36, 14, 50, 28, (20, 22, 34))


def sandwich(d, u, col):
    _poly(d, u, [(8, 60), (50, 18), (92, 60)], (230, 190, 120))
    _rr(d, u, 8, 56, 92, 66, 3, (110, 220, 110))
    _rr(d, u, 8, 66, 92, 76, 3, (255, 120, 120))
    _poly(d, u, [(8, 76), (92, 76), (50, 92)], (230, 190, 120))


def drink(d, u, col):
    _poly(d, u, [(24, 20), (76, 20), (68, 94), (32, 94)], col)
    _rr(d, u, 20, 12, 80, 22, 4, (240, 240, 250))
    _line(d, u, [(56, 14), (62, 0)], (255, 255, 255), 5)


def coin(d, u, col):
    _el(d, u, 6, 6, 94, 94, (255, 205, 60), (200, 150, 20), 4)
    _el(d, u, 20, 20, 80, 80, None, (210, 160, 30), 3)
    _line(d, u, [(50, 28), (50, 72)], (170, 120, 10), 5)
    d.arc((34 * u, 32 * u, 66 * u, 52 * u), 90, 270, fill=(170, 120, 10), width=int(5 * u))
    d.arc((34 * u, 48 * u, 66 * u, 68 * u), 270, 90, fill=(170, 120, 10), width=int(5 * u))


def bill(d, u, col):
    _rr(d, u, 4, 24, 96, 76, 8, (90, 200, 120), (40, 130, 70), 3)
    _el(d, u, 34, 34, 66, 66, (60, 160, 90))
    _line(d, u, [(50, 38), (50, 62)], (220, 255, 230), 4)


def sheep(d, u, col):
    for cx, cy in ((30, 46), (50, 38), (70, 46), (40, 58), (60, 58)):
        _el(d, u, cx - 17, cy - 16, cx + 17, cy + 16, col)
    _el(d, u, 70, 40, 92, 66, (70, 70, 90))
    _el(d, u, 80, 48, 84, 52, (255, 255, 255))
    for x in (34, 62):
        _rr(d, u, x, 68, x + 6, 90, 2, (70, 70, 90))


def machine(d, u, col):
    _rr(d, u, 8, 30, 92, 90, 10, col)
    _rr(d, u, 16, 38, 60, 62, 5, (20, 26, 52))
    _rr(d, u, 66, 38, 84, 82, 4, shade(col, 0.7))
    _rr(d, u, 24, 8, 36, 30, 3, (120, 126, 150))
    _el(d, u, 28, 46, 48, 58, (255, 216, 77))


def gear(d, u, col):
    cx = cy = 50
    for k in range(8):
        a = k * math.pi / 4
        x, y = cx + 38 * math.cos(a), cy + 38 * math.sin(a)
        _el(d, u, x - 10, y - 10, x + 10, y + 10, col)
    _el(d, u, 18, 18, 82, 82, col)
    _el(d, u, 36, 36, 64, 64, (20, 26, 52))


def pizza(d, u, col):
    _el(d, u, 6, 6, 94, 94, (240, 190, 90), (210, 140, 50), 3)
    _el(d, u, 14, 14, 86, 86, (255, 120, 80))
    for x, y in ((38, 34), (62, 40), (46, 60), (68, 66), (30, 58)):
        _el(d, u, x - 7, y - 7, x + 7, y + 7, (170, 40, 50))


def cookie(d, u, col):
    _el(d, u, 6, 6, 94, 94, (215, 160, 90), (170, 110, 50), 3)
    for x, y in ((34, 34), (62, 36), (46, 58), (68, 64), (30, 64)):
        _el(d, u, x - 6, y - 6, x + 6, y + 6, (80, 48, 30))


def shirt(d, u, col):
    _poly(d, u, [(30, 8), (44, 8), (50, 18), (56, 8), (70, 8), (94, 28), (82, 44), (72, 38), (72, 92), (28, 92), (28, 38), (18, 44), (6, 28)], col)


def train(d, u, col):
    _rr(d, u, 6, 36, 70, 76, 7, col)
    _rr(d, u, 58, 20, 94, 76, 7, shade(col, 0.8))
    _rr(d, u, 66, 28, 86, 46, 3, (190, 232, 255))
    _rr(d, u, 14, 22, 28, 38, 3, (60, 62, 80))
    for cx in (22, 44, 76):
        _el(d, u, cx - 9, 66, cx + 9, 84, (40, 44, 60))
        _el(d, u, cx - 4, 71, cx + 4, 79, (190, 196, 220))


def fly(d, u, col):
    _el(d, u, 20, 20, 60, 56, (255, 255, 255, 140))
    _el(d, u, 40, 14, 80, 50, (255, 255, 255, 140))
    _el(d, u, 28, 42, 78, 72, (40, 40, 52))
    _el(d, u, 66, 44, 90, 66, (40, 40, 52))
    _el(d, u, 78, 48, 84, 54, (255, 90, 90))


def critter(d, u, col):
    _el(d, u, 12, 28, 88, 90, col)
    _el(d, u, 20, 14, 46, 42, (255, 255, 255))
    _el(d, u, 54, 14, 80, 42, (255, 255, 255))
    _el(d, u, 30, 24, 40, 34, (30, 30, 40))
    _el(d, u, 62, 24, 72, 34, (30, 30, 40))
    d.arc((30 * u, 52 * u, 70 * u, 80 * u), 20, 160, fill=(30, 30, 40), width=int(3 * u))


def lily(d, u, col):
    _el(d, u, 6, 18, 94, 82, col)
    _poly(d, u, [(50, 50), (96, 24), (96, 50)], (0, 0, 0, 0))
    d.pieslice((6 * u, 18 * u, 94 * u, 82 * u), -20, 14, fill=(0, 0, 0, 0))
    _el(d, u, 62, 28, 76, 42, (255, 150, 190))


def sock(d, u, col):
    _poly(d, u, [(30, 4), (62, 4), (62, 56), (92, 70), (92, 92), (40, 92), (30, 70)], col)
    _rr(d, u, 30, 4, 62, 18, 3, lighten(col, 0.5))


def door(d, u, col):
    _rr(d, u, 14, 4, 86, 96, 8, col)
    _rr(d, u, 24, 14, 76, 86, 5, shade(col, 0.82))
    _el(d, u, 66, 50, 74, 58, (255, 220, 120))


def log(d, u, col):
    _el(d, u, 4, 4, 96, 96, (150, 100, 55), (110, 70, 35), 3)
    _el(d, u, 22, 22, 78, 78, None, (190, 140, 85), 3)
    _el(d, u, 38, 38, 62, 62, None, (190, 140, 85), 3)


def watermelon(d, u, col):
    d.pieslice((4 * u, -40 * u, 96 * u, 96 * u), 0, 180, fill=(60, 170, 80))
    d.pieslice((12 * u, -30 * u, 88 * u, 86 * u), 0, 180, fill=(255, 90, 110))
    for x, y in ((34, 52), (50, 62), (66, 52), (42, 42), (58, 42)):
        _el(d, u, x - 3, y - 4, x + 3, y + 4, (30, 30, 40))


def tag(d, u, col):
    _poly(d, u, [(8, 50), (42, 8), (92, 8), (92, 58), (50, 92)], col)
    _el(d, u, 66, 20, 82, 36, (20, 26, 52))


def star(d, u, col):
    pts = []
    for k in range(10):
        r = 46 if k % 2 == 0 else 20
        a = math.pi / 5 * k - math.pi / 2
        pts.append((50 + r * math.cos(a), 52 + r * math.sin(a)))
    _poly(d, u, pts, col)


def runner(d, u, col):
    _el(d, u, 52, 6, 74, 28, (255, 214, 170))
    _line(d, u, [(58, 30), (46, 56)], col, 12)
    _line(d, u, [(46, 56), (28, 78), (20, 94)], col, 9)
    _line(d, u, [(46, 56), (64, 72), (74, 92)], col, 9)
    _line(d, u, [(58, 34), (78, 48)], col, 8)
    _line(d, u, [(58, 34), (36, 42)], col, 8)


def goat(d, u, col):
    _el(d, u, 20, 34, 80, 90, (235, 235, 245))
    _el(d, u, 30, 14, 70, 52, (235, 235, 245))
    _line(d, u, [(36, 16), (30, 0)], (90, 80, 70), 4)
    _line(d, u, [(64, 16), (70, 0)], (90, 80, 70), 4)
    _el(d, u, 38, 26, 44, 32, (30, 30, 40))
    _el(d, u, 56, 26, 62, 32, (30, 30, 40))
    _el(d, u, 42, 40, 58, 50, (255, 190, 200))


def cartop(d, u, col):          # trophy car for monty (the prize)
    car(d, u, col)


DRAW = {k: v for k, v in globals().items() if callable(v) and k in (
    "car", "person", "ball", "bat", "pen", "eraser", "burger", "fries", "phone", "case", "sandwich", "drink", "coin", "bill", "sheep", "machine", "gear",
    "pizza", "cookie", "shirt", "train", "fly", "critter", "lily", "sock", "door", "log", "watermelon", "tag", "star", "runner", "goat")}


@lru_cache(maxsize=2048)
def _cached(name, size, col):
    im, d, u = _canvas(size)
    DRAW[name](d, u, col)
    return im.resize((size, size), Image.LANCZOS)


def get(name, size=96, color=None):
    col = tuple(color[:3]) if color else DEF.get(name, (95, 211, 255))
    return _cached(name, max(8, int(size)), col)
