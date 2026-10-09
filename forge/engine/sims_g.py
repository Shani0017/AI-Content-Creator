"""ASMR batch G: Country Battle (flag balls, last country standing)."""
import math
from PIL import Image, ImageDraw
from core import *

# ---------------------------------------------------------------- flags (drawn procedurally, no downloads)
NAMES = {"MY": "MALAYSIA", "ID": "INDONESIA", "PH": "PHILIPPINES", "TH": "THAILAND", "VN": "VIETNAM", "SG": "SINGAPORE",
         "BR": "BRAZIL", "US": "USA", "JP": "JAPAN", "IN": "INDIA", "PK": "PAKISTAN", "KR": "KOREA",
         "FR": "FRANCE", "IT": "ITALY", "DE": "GERMANY", "ES": "SPAIN", "CN": "CHINA", "RU": "RUSSIA", "AR": "ARGENTINA", "NG": "NIGERIA"}
TEAMCOL = {"MY": (240, 200, 40), "ID": (230, 40, 50), "PH": (40, 90, 220), "TH": (60, 70, 160), "VN": (220, 30, 30), "SG": (240, 60, 70),
           "BR": (30, 170, 70), "US": (60, 90, 200), "JP": (240, 240, 240), "IN": (255, 150, 50), "PK": (20, 120, 60), "KR": (80, 120, 230),
           "FR": (40, 80, 200), "IT": (30, 160, 70), "DE": (250, 200, 30), "ES": (230, 180, 20), "CN": (230, 30, 30), "RU": (40, 80, 200),
           "AR": (120, 190, 240), "NG": (20, 150, 70)}


def star(d, cx, cy, r, col, pts=5, rot=-math.pi / 2):
    p = []
    for i in range(pts * 2):
        rr = r if i % 2 == 0 else r * 0.42
        a = rot + i * math.pi / pts
        p.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(p, fill=col)


def flag_img(code, w=300, h=200):
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    R, Wh, B, Y, G = (205, 20, 40), (255, 255, 255), (15, 40, 130), (250, 205, 20), (0, 140, 70)
    if code == "MY":
        for i in range(14):
            d.rectangle((0, i * h / 14, w, (i + 1) * h / 14), fill=R if i % 2 == 0 else Wh)
        d.rectangle((0, 0, w * .5, h * 8 / 14), fill=B)
        cx, cy, r = w * .2, h * 4 / 14, h * .2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=Y)
        d.ellipse((cx - r * .7, cy - r * .85, cx + r * 1.0, cy + r * .85), fill=B)
        star(d, w * .36, cy, h * .13, Y, 14)
    elif code == "ID":
        d.rectangle((0, 0, w, h / 2), fill=R)
    elif code == "PH":
        d.rectangle((0, 0, w, h / 2), fill=B)
        d.rectangle((0, h / 2, w, h), fill=R)
        d.polygon([(0, 0), (w * .45, h / 2), (0, h)], fill=Wh)
        star(d, w * .14, h / 2, h * .13, Y, 8)
    elif code == "TH":
        for y0, y1, c in ((0, 1, R), (1, 2, Wh), (2, 4, B), (4, 5, Wh), (5, 6, R)):
            d.rectangle((0, y0 * h / 6, w, y1 * h / 6), fill=c)
    elif code == "VN":
        d.rectangle((0, 0, w, h), fill=(218, 37, 29))
        star(d, w / 2, h / 2, h * .32, (255, 255, 0))
    elif code == "SG":
        d.rectangle((0, 0, w, h / 2), fill=(238, 36, 54))
        cx, cy, r = w * .2, h * .25, h * .17
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=Wh)
        d.ellipse((cx - r * .6, cy - r, cx + r * 1.2, cy + r), fill=(238, 36, 54))
        for k in range(5):
            a = -math.pi / 2 + k * 2 * math.pi / 5
            star(d, w * .3 + math.cos(a) * h * .08, cy + math.sin(a) * h * .08, h * .035, Wh)
    elif code == "BR":
        d.rectangle((0, 0, w, h), fill=G)
        d.polygon([(w * .08, h / 2), (w / 2, h * .1), (w * .92, h / 2), (w / 2, h * .9)], fill=Y)
        r = h * .26
        d.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), fill=(0, 39, 118))
    elif code == "US":
        for i in range(13):
            d.rectangle((0, i * h / 13, w, (i + 1) * h / 13), fill=(178, 34, 52) if i % 2 == 0 else Wh)
        d.rectangle((0, 0, w * .45, h * 7 / 13), fill=(60, 59, 110))
        for i in range(4):
            for j in range(5):
                star(d, w * .05 + j * w * .085, h * .07 + i * h * .12, h * .035, Wh)
    elif code == "JP":
        r = h * .3
        d.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), fill=(188, 0, 45))
    elif code == "IN":
        d.rectangle((0, 0, w, h / 3), fill=(255, 153, 51))
        d.rectangle((0, 2 * h / 3, w, h), fill=(19, 136, 8))
        r = h * .13
        d.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), outline=(0, 0, 128), width=4)
    elif code == "PK":
        d.rectangle((0, 0, w, h), fill=(1, 65, 28))
        d.rectangle((0, 0, w * .25, h), fill=Wh)
        cx, cy, r = w * .62, h * .5, h * .3
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=Wh)
        d.ellipse((cx - r * .55, cy - r * 1.05, cx + r * 1.15, cy + r * .75), fill=(1, 65, 28))
        star(d, cx + r * .45, cy - r * .35, h * .09, Wh)
    elif code in ("FR", "IT"):
        c1 = (0, 85, 164) if code == "FR" else (0, 146, 70)
        d.rectangle((0, 0, w / 3, h), fill=c1)
        d.rectangle((2 * w / 3, 0, w, h), fill=(239, 65, 53) if code == "FR" else (206, 43, 55))
    elif code == "DE":
        for i, c in enumerate([(0, 0, 0), (221, 0, 0), (255, 206, 0)]):
            d.rectangle((0, i * h / 3, w, (i + 1) * h / 3), fill=c)
    elif code == "ES":
        d.rectangle((0, 0, w, h), fill=(198, 11, 30))
        d.rectangle((0, h / 4, w, 3 * h / 4), fill=(255, 196, 0))
    elif code == "CN":
        d.rectangle((0, 0, w, h), fill=(222, 41, 16))
        star(d, w * .17, h * .27, h * .15, (255, 222, 0))
        for k, (x, y) in enumerate([(.33, .1), (.4, .2), (.4, .35), (.33, .45)]):
            star(d, w * x, h * y, h * .05, (255, 222, 0))
    elif code == "RU":
        for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 43, 30)]):
            d.rectangle((0, i * h / 3, w, (i + 1) * h / 3), fill=c)
    elif code == "AR":
        d.rectangle((0, 0, w, h), fill=(116, 172, 223))
        d.rectangle((0, h / 3, w, 2 * h / 3), fill=(255, 255, 255))
        r = h * .1
        d.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), fill=(246, 180, 14))
    elif code == "NG":
        d.rectangle((0, 0, w / 3, h), fill=(0, 135, 81))
        d.rectangle((2 * w / 3, 0, w, h), fill=(0, 135, 81))
    elif code == "KR":
        r = h * .25
        d.pieslice((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), 180, 360, fill=(205, 46, 58))
        d.pieslice((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r), 0, 180, fill=(0, 71, 160))
    return im


_ball = {}


def flag_ball(code, r):
    """circle-cropped flag with a white rim, RGBA, cached per (code, radius)"""
    k = (code, int(r))
    if k not in _ball:
        s = int(r) * 2
        f = flag_img(code).resize((int(s * 1.5), s), Image.LANCZOS).crop((int(s * .25), 0, int(s * .25) + s, s))
        m = Image.new("L", (s * 4, s * 4), 0)
        ImageDraw.Draw(m).ellipse((0, 0, s * 4 - 1, s * 4 - 1), fill=255)
        m = m.resize((s, s), Image.LANCZOS)
        out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        out.paste(f, (0, 0), m)
        ImageDraw.Draw(out).ellipse((1, 1, s - 2, s - 2), outline=(255, 255, 255), width=max(2, s // 16))
        _ball[k] = out
    return _ball[k]


# ---------------------------------------------------------------- COUNTRY BATTLE
class CountryBattle(Sim):
    """Battle royale: one flag ball per country, each with HP shown on it. Every contact between two balls costs BOTH
    one HP, every time (no skipped hits). Constant speed, no slow motion. After a while the ring closes in.
    A ball at 0 HP is eliminated. The last country left wins."""
    TITLE, SUB = "COUNTRY BATTLE", "LAST COUNTRY STANDING WINS"
    SEED, SOUND, BASE_NOTE = 7, "marimba", 220.0
    BG = (8, 10, 16)
    TS = False
    TEAMS = ["MY", "ID", "PH", "TH", "VN", "SG", "BR", "US", "JP", "IN", "KR", "CN", "FR", "DE", "ES", "AR"]
    HP, SPEED, RB = 70, 300.0, 40
    CX, CY, R0, RMIN, SHRINK, SHRINK_AT = 540, 960, 430, 120, 6.0, 25.0
    COUNTER = "BATTLE"

    def setup(self):
        self.R = self.R0
        self.balls = []                 # x, y, vx, vy, team, hp, alive, flash
        for t in range(len(self.TEAMS)):
            for _ in range(500):
                a, rr = self.rng.uniform(0, 2 * math.pi), self.rng.uniform(0, self.R0 - self.RB - 10)
                x, y = self.CX + math.cos(a) * rr, self.CY + math.sin(a) * rr
                if all(math.hypot(x - b[0], y - b[1]) > 2 * self.RB + 12 for b in self.balls):
                    break
            v = self.rng.uniform(0, 2 * math.pi)
            self.balls.append([x, y, math.cos(v) * self.SPEED, math.sin(v) * self.SPEED, t, self.HP, True, 0.0])
        self.total = len(self.balls)
        self.removed = 0
        self.winner = None
        self.out_order = []
        self.touch = {}                 # pair -> time of last counted hit; a held contact re-counts every 0.5 s

    def physics(self, dt):
        if self.winner is not None:
            return
        nal = sum(1 for b in self.balls if b[6])
        if self.t > self.SHRINK_AT:                    # ring closes in; faster in the endgame
            self.R = max(self.RMIN, self.R - (self.SHRINK if nal > 3 else self.SHRINK * 3) * dt)
        r = self.RB
        bl = [b for b in self.balls if b[6]]
        for b in bl:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[7] = max(0.0, b[7] - dt)
            dx, dy = b[0] - self.CX, b[1] - self.CY
            dd = math.hypot(dx, dy) or 1e-9
            if dd > self.R - r:
                nx, ny = dx / dd, dy / dd
                b[0], b[1] = self.CX + nx * (self.R - r), self.CY + ny * (self.R - r)
                if b[2] * nx + b[3] * ny > 0:
                    b[2], b[3] = reflect(b[2], b[3], nx, ny)
                    da = self.rng.uniform(-0.18, 0.18)          # slightly rough wall: no endless periodic orbits
                    c, sn = math.cos(da), math.sin(da)
                    b[2], b[3] = b[2] * c - b[3] * sn, b[2] * sn + b[3] * c
                    if b[2] * nx + b[3] * ny > 0:               # never point back out of the ring
                        b[2], b[3] = reflect(b[2], b[3], nx, ny)
        for i in range(len(bl)):
            a = bl[i]
            if not a[6]:
                continue
            for j in range(i + 1, len(bl)):
                b = bl[j]
                if not b[6]:
                    continue
                dx, dy = b[0] - a[0], b[1] - a[1]
                dd = math.hypot(dx, dy)
                key = (a[4], b[4])
                if dd >= 2 * r + 1.5 or dd == 0:
                    self.touch.pop(key, None)
                    continue
                if dd >= 2 * r:
                    continue
                nx, ny = dx / dd, dy / dd
                ov = (2 * r - dd) / 2
                a[0] -= nx * ov; a[1] -= ny * ov; b[0] += nx * ov; b[1] += ny * ov
                rel = (a[2] - b[2]) * nx + (a[3] - b[3]) * ny
                if rel > 0:
                    a[2] -= rel * nx; a[3] -= rel * ny; b[2] += rel * nx; b[3] += rel * ny
                    for q in (a, b):
                        s = math.hypot(q[2], q[3]) or 1
                        q[2], q[3] = q[2] / s * self.SPEED, q[3] / s * self.SPEED
                if key in self.touch and self.t - self.touch[key] < 0.5:
                    continue                    # same contact still going: not a new hit yet
                self.touch[key] = self.t
                for q in (a, b):
                    q[5] -= 1
                    q[7] = 0.18
                    if q[5] <= 0:
                        q[6] = False
                        self.removed += 1
                        self.out_order.append(q[4])
                        self.burst(q[0], q[1], TEAMCOL[self.TEAMS[q[4]]], 30, 420, 0.8)
                        self.ev("boom", 0.6)
                self.burst((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (255, 255, 255), 6, 200, 0.3)
                self.ev("hit", ((a[4] + b[4]) * 0.13) % 1)
                if not a[6]:
                    break
        alive = [b for b in self.balls if b[6]]
        if len(alive) <= 1 and self.winner is None:
            self.winner = alive[0][4] if alive else (self.out_order[-1] if self.out_order else -1)
        self.p = 1.0 if self.winner is not None else min(0.999, self.removed / max(1, self.total - 1))

    def audit_missed(self):
        bl = [b for b in self.balls if b[6]]
        return sum(1 for i in range(len(bl)) for j in range(i + 1, len(bl))
                   if math.hypot(bl[i][0] - bl[j][0], bl[i][1] - bl[j][1]) < 2 * self.RB * 0.7)

    def leftovers(self):
        return 0

    def draw(self, d):
        img = d._image
        d.ellipse((self.CX - self.R0, self.CY - self.R0, self.CX + self.R0, self.CY + self.R0), outline=(40, 44, 60), width=2)
        d.ellipse((self.CX - self.R - 5, self.CY - self.R - 5, self.CX + self.R + 5, self.CY + self.R + 5), outline=(255, 255, 255), width=6)
        r = self.RB
        fn = font(40)
        for b in self.balls:
            if not b[6]:
                continue
            im = flag_ball(self.TEAMS[b[4]], r)
            img.paste(im, (int(b[0] - r), int(b[1] - r)), im)
            if b[7] > 0:
                d.ellipse((b[0] - r - 4, b[1] - r - 4, b[0] + r + 4, b[1] + r + 4), outline=(255, 80, 80), width=5)
            txt = str(b[5])
            w = d.textlength(txt, font=fn)
            d.text((b[0] - w / 2, b[1] - 24), txt, font=fn, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))

    def hud(self, d):
        ctext(d, self.TITLE, 120, font(112), (255, 255, 255))
        ctext(d, self.SUB, 252, font(38, ARIAL), (255, 220, 90))
        img = d._image
        n = len(self.TEAMS)
        cols = min(8, n)
        rows = math.ceil(n / cols)
        cw = (W - 80) / cols
        for t, code in enumerate(self.TEAMS):
            alive = self.balls[t][6]
            inrow = min(cols, n - (t // cols) * cols)          # centre a short last row
            x0 = W / 2 + ((t % cols) - (inrow - 1) / 2) * cw
            y0 = 1470 + (t // cols) * 150
            im = flag_ball(code, 30)
            if not alive:
                im = im.convert("LA").convert("RGBA")
            img.paste(im, (int(x0 - 30), int(y0)), im)
            nm = NAMES[code]
            fn = font(24 if len(nm) <= 9 else 20)
            w = d.textlength(nm, font=fn)
            d.text((x0 - w / 2, y0 + 66), nm, font=fn, fill=(235, 235, 235) if alive else (90, 90, 90))
            if not alive:
                d.line((x0 - 34, y0 - 4, x0 + 34, y0 + 64), fill=(220, 50, 50), width=5)
        left = sum(1 for b in self.balls if b[6])
        ctext(d, f"{left} COUNTRIES LEFT" if self.winner is None else "", 1790, font(48), (255, 255, 255))
        if self.done_at is not None and self.winner is not None and self.winner >= 0:
            code = self.TEAMS[self.winner]
            d.rectangle((0, 560, W, 1330), fill=(8, 10, 16))
            ctext(d, "WINNER", 600, font(120), (255, 224, 90))
            im = flag_ball(code, 130)
            img.paste(im, (W // 2 - 130, 760), im)
            ctext(d, NAMES[code], 1040, font(130), (255, 255, 255))
            ctext(d, "COMMENT YOUR COUNTRY", 1200, font(56), (255, 224, 90))


def battle(teams, seed=7, per=None):
    """make a CountryBattle variant for a given list of country codes"""
    attrs = {"TEAMS": list(teams), "SEED": seed}
    return type("CountryBattle", (CountryBattle,), attrs)


BATCH_G = [CountryBattle]


# ---------------------------------------------------------------- SHOOTING BATTLE
class ShootingBattle(Sim):
    """Battle royale with guns: every country ball rolls around the ring (constant speed, bouncing) and its turret aims at
    the nearest enemy and fires. Every bullet that touches a ball costs it 1 HP (no skipped hits); bullets that reach
    the ring vanish with a spark. Ball contacts only bounce. 0 HP = eliminated (kill goes to the shooter).
    The ring closes in after a while, faster in the endgame. Last country left wins."""
    TITLE, SUB = "COUNTRY WAR", "LAST COUNTRY STANDING WINS"
    SEED, SOUND, BASE_NOTE = 7, "pluck", 330.0
    BG = (8, 10, 16)
    TS = False
    TEAMS = ["MY", "ID", "PH", "TH", "VN", "SG", "BR", "US", "JP", "IN", "KR", "CN", "FR", "DE", "ES", "AR"]
    HP, SPEED, RB = 18, 170.0, 40
    FIRE, BSPEED, SPREAD = 1.0, 820.0, 0.10
    HEAL = 10                       # a knockout restores HP to the shooter (capped at full)
    CX, CY, R0, RMIN, SHRINK, SHRINK_AT = 540, 960, 480, 150, 5.0, 20.0
    COUNTER = "WAR"

    def setup(self):
        self.R = self.R0
        self.balls = []      # x, y, vx, vy, team, hp, alive, flash, aim, cooldown, kills
        for t in range(len(self.TEAMS)):
            for _ in range(500):
                a, rr = self.rng.uniform(0, 2 * math.pi), self.rng.uniform(0, self.R0 - self.RB - 10)
                x, y = self.CX + math.cos(a) * rr, self.CY + math.sin(a) * rr
                if all(math.hypot(x - b[0], y - b[1]) > 2 * self.RB + 20 for b in self.balls):
                    break
            v = self.rng.uniform(0, 2 * math.pi)
            self.balls.append([x, y, math.cos(v) * self.SPEED, math.sin(v) * self.SPEED, t, self.HP, True, 0.0,
                               self.rng.uniform(0, 6.28), self.rng.uniform(0.3, 1.5), 0])
        self.shots = []      # x, y, vx, vy, owner, life
        self.feed = []       # (t, killer, victim)
        self.total = len(self.balls)
        self.removed = 0
        self.winner = None
        self.muzzle = []

    def nearest(self, b):
        best, bd = None, 1e9
        for o in self.balls:
            if o is b or not o[6]:
                continue
            d = math.hypot(o[0] - b[0], o[1] - b[1])
            if d < bd:
                best, bd = o, d
        return best

    def physics(self, dt):
        if self.winner is not None:
            self.shots = []
            return
        nal = sum(1 for b in self.balls if b[6])
        if self.t > self.SHRINK_AT:
            self.R = max(self.RMIN, self.R - (self.SHRINK if nal > 3 else self.SHRINK * 3) * dt)
        r = self.RB
        bl = [b for b in self.balls if b[6]]
        for b in bl:
            b[0] += b[2] * dt
            b[1] += b[3] * dt
            b[7] = max(0.0, b[7] - dt)
            dx, dy = b[0] - self.CX, b[1] - self.CY
            dd = math.hypot(dx, dy) or 1e-9
            if dd > self.R - r:
                nx, ny = dx / dd, dy / dd
                b[0], b[1] = self.CX + nx * (self.R - r), self.CY + ny * (self.R - r)
                if b[2] * nx + b[3] * ny > 0:
                    b[2], b[3] = reflect(b[2], b[3], nx, ny)
                    da = self.rng.uniform(-0.2, 0.2)
                    c, sn = math.cos(da), math.sin(da)
                    b[2], b[3] = b[2] * c - b[3] * sn, b[2] * sn + b[3] * c
                    if b[2] * nx + b[3] * ny > 0:
                        b[2], b[3] = reflect(b[2], b[3], nx, ny)
            # turret: turn toward the nearest enemy, fire on cooldown
            tgt = self.nearest(b)
            if tgt is not None:
                want = math.atan2(tgt[1] - b[1], tgt[0] - b[0])
                diff = (want - b[8] + math.pi) % (2 * math.pi) - math.pi
                b[8] += max(-6.0 * dt, min(6.0 * dt, diff))
                b[9] -= dt
                if b[9] <= 0 and abs(diff) < 0.35:
                    b[9] = self.FIRE * self.rng.uniform(0.8, 1.2)
                    a = b[8] + self.rng.uniform(-self.SPREAD, self.SPREAD)
                    mx, my = b[0] + math.cos(a) * (r + 32), b[1] + math.sin(a) * (r + 32)
                    self.shots.append([mx, my, math.cos(a) * self.BSPEED, math.sin(a) * self.BSPEED, b[4], 2.0])
                    self.muzzle.append([mx, my, 0.08])
                    self.ev("pop", (b[4] * 0.17) % 1)
        # ball contacts: bounce only
        for i in range(len(bl)):
            a = bl[i]
            for j in range(i + 1, len(bl)):
                b = bl[j]
                dx, dy = b[0] - a[0], b[1] - a[1]
                dd = math.hypot(dx, dy)
                if dd >= 2 * r or dd == 0:
                    continue
                nx, ny = dx / dd, dy / dd
                ov = (2 * r - dd) / 2
                a[0] -= nx * ov; a[1] -= ny * ov; b[0] += nx * ov; b[1] += ny * ov
                rel = (a[2] - b[2]) * nx + (a[3] - b[3]) * ny
                if rel > 0:
                    a[2] -= rel * nx; a[3] -= rel * ny; b[2] += rel * nx; b[3] += rel * ny
                    for q in (a, b):
                        s = math.hypot(q[2], q[3]) or 1
                        q[2], q[3] = q[2] / s * self.SPEED, q[3] / s * self.SPEED
        # bullets
        keep = []
        for s in self.shots:
            s[0] += s[2] * dt
            s[1] += s[3] * dt
            s[5] -= dt
            hit = None
            for b in self.balls:
                if b[6] and b[4] != s[4] and (s[0] - b[0]) ** 2 + (s[1] - b[1]) ** 2 < (r + 9) ** 2:
                    hit = b
                    break
            if hit is not None:
                hit[5] -= 1
                hit[7] = 0.12
                self.burst(s[0], s[1], (255, 230, 120), 7, 260, 0.3)
                self.ev("hit", (hit[4] * 0.11) % 1)
                if hit[5] <= 0:
                    hit[6] = False
                    self.removed += 1
                    k = self.balls[s[4]]
                    k[10] += 1
                    if k[6]:
                        k[5] = min(self.HP, k[5] + self.HEAL)
                    self.feed.append((self.t, s[4], hit[4]))
                    self.burst(hit[0], hit[1], TEAMCOL[self.TEAMS[hit[4]]], 36, 480, 0.9)
                    self.burst(hit[0], hit[1], (255, 255, 255), 14, 300, 0.5)
                    self.ev("boom", 0.6)
                continue
            if math.hypot(s[0] - self.CX, s[1] - self.CY) > self.R or s[5] <= 0:
                self.burst(s[0], s[1], TEAMCOL[self.TEAMS[s[4]]], 3, 120, 0.2)
                continue
            keep.append(s)
        self.shots = keep
        for m in self.muzzle:
            m[2] -= dt
        self.muzzle = [m for m in self.muzzle if m[2] > 0]
        alive = [b for b in self.balls if b[6]]
        if len(alive) <= 1 and self.winner is None:
            self.winner = alive[0][4] if alive else -1
        self.p = 1.0 if self.winner is not None else min(0.999, self.removed / max(1, self.total - 1))

    def audit_missed(self):
        bl = [b for b in self.balls if b[6]]
        m = sum(1 for i in range(len(bl)) for j in range(i + 1, len(bl))
                if math.hypot(bl[i][0] - bl[j][0], bl[i][1] - bl[j][1]) < 2 * self.RB * 0.7)
        for s in self.shots:                       # a bullet sitting inside an enemy = a skipped hit
            for b in bl:
                if b[4] != s[4] and math.hypot(s[0] - b[0], s[1] - b[1]) < self.RB * 0.6:
                    m += 1
        return m

    def leftovers(self):
        return 0

    def draw(self, d):
        img = d._image
        d.ellipse((self.CX - self.R0, self.CY - self.R0, self.CX + self.R0, self.CY + self.R0), outline=(36, 40, 56), width=2)
        d.ellipse((self.CX - self.R - 5, self.CY - self.R - 5, self.CX + self.R + 5, self.CY + self.R + 5), outline=(255, 255, 255), width=6)
        r = self.RB
        for s in self.shots:                       # glowing bullets with trails
            col = TEAMCOL[self.TEAMS[s[4]]]
            tx, ty = s[0] - s[2] * 0.06, s[1] - s[3] * 0.06
            d.line((tx, ty, s[0], s[1]), fill=tuple(int(c * .5) for c in col), width=10)
            d.line((s[0] - s[2] * 0.03, s[1] - s[3] * 0.03, s[0], s[1]), fill=col, width=8)
            d.ellipse((s[0] - 10, s[1] - 10, s[0] + 10, s[1] + 10), fill=col)
            d.ellipse((s[0] - 5, s[1] - 5, s[0] + 5, s[1] + 5), fill=(255, 255, 240))
        for b in self.balls:
            if not b[6]:
                continue
            a = b[8]
            ex, ey = b[0] + math.cos(a) * (r + 30), b[1] + math.sin(a) * (r + 30)
            d.line((b[0], b[1], ex, ey), fill=(20, 20, 26), width=26)
            d.line((b[0], b[1], ex, ey), fill=(150, 155, 170), width=16)
            d.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=(20, 20, 26))
            im = flag_ball(self.TEAMS[b[4]], r)
            img.paste(im, (int(b[0] - r), int(b[1] - r)), im)
            if b[7] > 0:
                d.ellipse((b[0] - r - 3, b[1] - r - 3, b[0] + r + 3, b[1] + r + 3), outline=(255, 60, 60), width=6)
            # hp bar under the ball
            w = 2 * r
            frac = max(0.0, b[5] / self.HP)
            d.rounded_rectangle((b[0] - w / 2, b[1] + r + 8, b[0] + w / 2, b[1] + r + 18), radius=5, fill=(40, 40, 48))
            col = (80, 220, 110) if frac > .5 else ((250, 200, 60) if frac > .25 else (240, 70, 70))
            if frac > 0:
                d.rounded_rectangle((b[0] - w / 2, b[1] + r + 8, b[0] - w / 2 + w * frac, b[1] + r + 18), radius=5, fill=col)
        for m in self.muzzle:
            k = m[2] / 0.08
            d.ellipse((m[0] - 22 * k, m[1] - 22 * k, m[0] + 22 * k, m[1] + 22 * k), fill=(255, 230, 120))

    def hud(self, d):
        ctext(d, self.TITLE, 110, font(112), (255, 255, 255))
        ctext(d, self.SUB, 242, font(38, ARIAL), (255, 220, 90))
        img = d._image
        # kill feed (last 3)
        fn = font(34)
        for k, (t, ki, vi) in enumerate(self.feed[-3:][::-1]):
            al = max(0.25, 1 - (self.t - t) / 6)
            y = 330 + k * 56
            a, b = NAMES[self.TEAMS[ki]], NAMES[self.TEAMS[vi]]
            mid = "  KNOCKED OUT  "
            wa, wm, wb = d.textlength(a, font=fn), d.textlength(mid, font=font(26)), d.textlength(b, font=fn)
            x = W / 2 - (wa + wm + wb + 80) / 2
            fa, fb = flag_ball(self.TEAMS[ki], 18), flag_ball(self.TEAMS[vi], 18)
            img.paste(fa, (int(x), y + 2), fa)
            d.text((x + 42, y), a, font=fn, fill=tuple(int(255 * al) for _ in range(3)))
            d.text((x + 42 + wa, y + 7), mid, font=font(26), fill=(int(240 * al), int(70 * al), int(70 * al)))
            img.paste(fb, (int(x + 46 + wa + wm), y + 2), fb)
            d.text((x + 88 + wa + wm, y), b, font=fn, fill=tuple(int(170 * al) for _ in range(3)))
        n = len(self.TEAMS)
        cols = min(8, n)
        cw = (W - 80) / cols
        for t, code in enumerate(self.TEAMS):
            alive = self.balls[t][6]
            inrow = min(cols, n - (t // cols) * cols)
            x0 = W / 2 + ((t % cols) - (inrow - 1) / 2) * cw
            y0 = 1510 + (t // cols) * 140
            im = flag_ball(code, 28)
            if not alive:
                im = im.convert("LA").convert("RGBA")
            img.paste(im, (int(x0 - 28), int(y0)), im)
            nm = NAMES[code]
            fn2 = font(22 if len(nm) <= 9 else 18)
            w = d.textlength(nm, font=fn2)
            d.text((x0 - w / 2, y0 + 60), nm, font=fn2, fill=(235, 235, 235) if alive else (90, 90, 90))
            if self.balls[t][10]:
                kt = f"{self.balls[t][10]} KO"
                w = d.textlength(kt, font=font(22))
                d.text((x0 - w / 2, y0 + 86), kt, font=font(22), fill=(255, 210, 80) if alive else (110, 100, 60))
            if not alive:
                d.line((x0 - 32, y0 - 4, x0 + 32, y0 + 60), fill=(220, 50, 50), width=5)
        left = sum(1 for b in self.balls if b[6])
        if self.winner is None:
            ctext(d, f"{left} COUNTRIES LEFT", 1820, font(46), (255, 255, 255))
        if self.done_at is not None and self.winner is not None and self.winner >= 0:
            code = self.TEAMS[self.winner]
            d.rectangle((0, 520, W, 1450), fill=(8, 10, 16))
            ctext(d, "WINNER", 600, font(120), (255, 224, 90))
            im = flag_ball(code, 130)
            img.paste(im, (W // 2 - 130, 760), im)
            ctext(d, NAMES[code], 1040, font(130), (255, 255, 255))
            ctext(d, f"{self.balls[self.winner][10]} KNOCKOUTS", 1190, font(60), (255, 120, 120))
            ctext(d, "COMMENT YOUR COUNTRY", 1300, font(56), (255, 224, 90))


BATCH_G.append(ShootingBattle)
