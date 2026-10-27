"""Interview Question reels - data-driven scene engine (fixed layout zones so text can never overlap).
A problem = hook beat + question beat + explanation beats + answer beat. Every beat has `parts` drawn in the illustration area.
Zones (illustration area x 60..1020, y 352..1015):  HEAD y=408 | BODY y 460..930 | FOOT y=975.
Part kinds: head, foot, big, row, bars, grid, nodes, tl, eq, pie, numline.   Each part: {"k":..., "at":0..1 (start in beat), ...}"""
import math
from forge import scenes
from forge.scenes import ease, back, clamp, DIM, TEXT, font, _tw

NL_ = chr(10)
HEAD_Y, FOOT_Y = 408, 975
BX0, BX1, BY0, BY1 = 80, 1000, 462, 935


SUB = {"Δ": "d", "Σ": "sum ", "⁹": "^9", "₀": "0", "₁": "1", "₂": "2", "≡": "=", "⊕": " xor ", "⌊": "floor(", "⌋": ")", "✓": "ok", "≈": "~"}


def clean(s):
    s = str(s)
    for k, v in SUB.items():
        s = s.replace(k, v)
    return s


def col(c, k, default=None):
    if isinstance(k, tuple):
        return k
    if k in ("w", None):
        return TEXT
    if k == "d":
        return DIM
    return c.th.get(k, default or TEXT)


def fit(c, s, size, maxw, bold=True):
    while size > 22 and _tw(c.d, s, font(size, bold)) > maxw:
        size -= 2
    return size


def stag(prog, i, n):
    """staggered reveal of item i of n for part progress prog (0..1) -> 0..1"""
    return clamp((prog * 1.25 - 0.9 * i / max(1, n)) / 0.35)


def box(c, x0, y0, x1, y1, fill, outline=None, a=1.0, r=16):
    f = tuple(fill[:3]) + (int(255 * a),)
    c.d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=f, outline=(tuple(outline[:3]) + (int(255 * a),)) if outline else None, width=3)


def text_c(c, s, x, y, size, color, a=1.0, maxw=None):
    s = clean(s)
    if maxw:
        size = fit(c, s, size, maxw)
    sh = int(size * 0.07)
    f = font(size)
    from forge.scenes import _rich
    if a < 0.99:
        # cheap fade: blend colour toward the panel background
        color = tuple(int(v * a + 22 * (1 - a)) for v in color)
    _rich(c.d, s, x, y, f, tuple(color), "mm", True)


# ---------------------------------------------------------------- parts
def p_head(c, P, p, u):
    text_c(c, P["text"], 540, HEAD_Y, P.get("size", 46), col(c, P.get("col", "y")), a=p, maxw=900)


def p_foot(c, P, p, u):
    s = P["text"]
    size = fit(c, s, P.get("size", 42), 880)
    cc = col(c, P.get("col", "g"))
    f = font(size)
    w = _tw(c.d, s, f) + 56
    y = FOOT_Y
    a = ease(p)
    c.d.rounded_rectangle((540 - w / 2, y - size * 0.85, 540 + w / 2, y + size * 0.85), radius=size, fill=(18, 24, 58, int(235 * a)),
                          outline=tuple(cc) + (int(255 * a),), width=3)
    text_c(c, s, 540, y, size, cc, a=a)


def p_big(c, P, p, u):
    lines = P["text"].split("\n")
    size = P.get("size", 92)
    size = min(fit(c, max(lines, key=len), size, 900), size)
    cc = col(c, P.get("col", "y"))
    y0 = P.get("y", 690) - (len(lines) - 1) * size * 0.62
    sc = 0.85 + 0.15 * back(p)
    for i, ln in enumerate(lines):
        text_c(c, ln, 540, y0 + i * size * 1.25, int(size * sc), cc if i == 0 or not P.get("col2") else col(c, P["col2"]), a=ease(p))
    if P.get("sub"):
        text_c(c, P["sub"], 540, y0 + len(lines) * size * 1.25 + 10, 40, DIM, a=ease(p), maxw=900)


def p_row(c, P, p, u):
    items = [str(x) for x in P["items"]]
    n = len(items)
    per = P.get("per", min(n, 10))
    w = min(P.get("w", 96), 900 / per - 8)
    h = P.get("h", 86)
    rows = [items[i:i + per] for i in range(0, n, per)]
    y0 = P.get("y", 650) + 40 - (len(rows) - 1) * (h + 18) / 2
    hl = set(P.get("hl", []))
    cmap = P.get("cols", {})
    k = 0
    for r, ri in enumerate(rows):
        x0 = 540 - (len(ri) * (w + 8) - 8) / 2
        for j, s in enumerate(ri):
            a = stag(p, k, n)
            cx, cy = x0 + j * (w + 8) + w / 2, y0 + r * (h + 18)
            if a > 0:
                cc = col(c, cmap.get(k, "y" if k in hl else None), None) if (k in hl or k in cmap) else (70, 82, 140)
                fillc = cc if (k in hl or k in cmap) else (40, 50, 104)
                sc = 0.6 + 0.4 * back(a)
                box(c, cx - w / 2 * sc, cy - h / 2 * sc, cx + w / 2 * sc, cy + h / 2 * sc, tuple(int(v * 0.35 + 8) for v in fillc) if (k in hl or k in cmap) else fillc,
                    cc if (k in hl or k in cmap) else (110, 130, 210), a=a)
                tc = cc if (k in hl or k in cmap) else TEXT
                if NL_ in s:
                    parts_ = s.split(NL_)
                    sz = min(P.get("size", 42), max(fit(c, q_, 42, w - 10) for q_ in parts_))
                    for li, q_ in enumerate(parts_):
                        text_c(c, q_, cx, cy + (li - (len(parts_) - 1) / 2) * sz * 1.15, int(sz * 0.9), tc, a=a, maxw=w - 8)
                else:
                    text_c(c, s, cx, cy, min(P.get("size", 42), fit(c, s, 42, w - 10)), tc, a=a)
            k += 1
    for (idx, label, cname) in P.get("marks", []):
        r, j = divmod(idx, per)
        ri = rows[r]
        x0 = 540 - (len(ri) * (w + 8) - 8) / 2
        cx, cy = x0 + j * (w + 8) + w / 2, y0 + r * (h + 18) + h / 2 + 30
        cc = col(c, cname)
        a = ease(clamp(p * 1.4 - 0.3))
        if a > 0:
            c.d.polygon([(cx, cy - 18), (cx - 14, cy + 6), (cx + 14, cy + 6)], fill=tuple(cc) + (int(255 * a),))
            text_c(c, label, cx, cy + 38, 30, cc, a=a, maxw=w * 2.2)


def p_bars(c, P, p, u):
    vals = P["vals"]
    n = len(vals)
    mx = P.get("max") or max(vals) or 1
    base = P.get("base", 900)
    maxh = P.get("maxh", 330)
    w = min(120, 880 / n - 10)
    x0 = 540 - (n * (w + 10) - 10) / 2
    hl = set(P.get("hl", []))
    labels = P.get("labels")
    cmap = P.get("cols", {})
    for i, v in enumerate(vals):
        a = stag(p, i, n)
        if a <= 0:
            continue
        h = maxh * (v / mx) * ease(a)
        x = x0 + i * (w + 10)
        cc = col(c, cmap.get(i, "y" if i in hl else "c"))
        box(c, x, base - h, x + w, base, tuple(int(q * 0.5) for q in cc), cc, r=10)
        text_c(c, str(P.get("fmt", "{}")).format(v) if not isinstance(P.get("fmt"), type(None)) else str(v), x + w / 2, base - h - 26, min(34, int(w * 0.5)), TEXT, a=a)
        if labels:
            text_c(c, str(labels[i]), x + w / 2, base + 30, min(28, int(w * 0.42)), DIM, a=a, maxw=w + 8)


def p_grid(c, P, p, u):
    R, C = P["rows"], P["cols"]
    cell = min(P.get("cell", 74), 880 / C, 450 / R)
    x0, y0 = 540 - C * cell / 2, P.get("y", 700) - R * cell / 2
    fill = P.get("fill", {})
    txt = P.get("text", {})
    n = R * C
    for r in range(R):
        for q in range(C):
            i = r * C + q
            a = stag(p, i, n) if P.get("reveal", True) else 1.0
            if a <= 0:
                continue
            key = f"{r},{q}"
            base = (36, 46, 100) if (r + q) % 2 == 0 or not P.get("checker", False) else (28, 36, 84)
            cc = col(c, fill[key]) if key in fill else None
            c.d.rounded_rectangle((x0 + q * cell + 2, y0 + r * cell + 2, x0 + (q + 1) * cell - 2, y0 + (r + 1) * cell - 2), radius=int(cell * 0.18),
                                  fill=(tuple(int(v * 0.55) for v in cc) + (int(255 * a),)) if cc else tuple(base) + (int(255 * a),),
                                  outline=(tuple(cc) + (int(255 * a),)) if cc else (90, 110, 190, int(255 * a)), width=2)
            if key in txt:
                text_c(c, str(txt[key]), x0 + (q + 0.5) * cell, y0 + (r + 0.5) * cell, int(cell * 0.42), TEXT, a=a, maxw=cell - 6)


def p_nodes(c, P, p, u):
    labels = [str(x) for x in P["labels"]]
    n = len(labels)
    layout = P.get("layout", "row")
    xy = P.get("xy")
    pos = []
    for i in range(n):
        if xy:
            pos.append((BX0 + xy[i][0] * (BX1 - BX0), BY0 + xy[i][1] * (BY1 - BY0)))
        elif layout == "circle":
            a = -math.pi / 2 + 2 * math.pi * i / n
            rr = min(230, 80 + 22 * n)
            pos.append((540 + rr * math.cos(a), 700 + rr * 0.9 * math.sin(a)))
        else:
            per = P.get("per", n)
            r, j = divmod(i, per)
            m = min(per, n - r * per)
            sp = min(150, 860 / max(1, per))
            pos.append((540 - (m - 1) * sp / 2 + j * sp, P.get("y", 640) + 40 + r * 150))
    rad = P.get("r", 36 if n <= 8 else 28)
    hl = set(P.get("hl", []))
    cmap = P.get("cols", {})
    for (a_, b_, *lab) in P.get("edges", []):
        al = ease(clamp(p * 1.6 - 0.2))
        if al <= 0:
            continue
        x1, y1 = pos[a_]
        x2, y2 = pos[b_]
        d = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / d, (y2 - y1) / d
        s_, e_ = (x1 + ux * rad, y1 + uy * rad), (x2 - ux * (rad + 4), y2 - uy * (rad + 4))
        ec = col(c, P.get("ecol", "c"))
        c.d.line([s_, (s_[0] + (e_[0] - s_[0]) * al, s_[1] + (e_[1] - s_[1]) * al)], fill=tuple(ec) + (220,), width=5)
        if al > 0.9:
            ang = math.atan2(uy, ux)
            for sgn in (2.7, -2.7):
                c.d.line([e_, (e_[0] + 20 * math.cos(ang + sgn), e_[1] + 20 * math.sin(ang + sgn))], fill=tuple(ec) + (220,), width=5)
        if lab and al > 0.9:
            text_c(c, str(lab[0]), (x1 + x2) / 2, (y1 + y2) / 2 - 22, 28, DIM)
    for i, (x, y) in enumerate(pos):
        a = stag(p, i, n)
        if a <= 0:
            continue
        cc = col(c, cmap.get(i, "y" if i in hl else None)) if (i in hl or i in cmap) else (110, 130, 210)
        rr = rad * (0.6 + 0.4 * back(a))
        c.d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=tuple(int(v * 0.35 + 10) for v in cc) + (255,), outline=tuple(cc) + (255,), width=4)
        text_c(c, labels[i], x, y, int(rad * 0.9), TEXT, a=a, maxw=rad * 1.7)


def p_tl(c, P, p, u):
    items = P["items"]            # (label, t0, t1, colname)
    total = P.get("total") or max(i[2] for i in items)
    x0, x1 = 230, 980
    rows = len(items)
    rh = min(70, 430 / rows)
    y0 = P.get("y", 690) - rows * rh / 2
    for q in range(0, int(total) + 1, P.get("step", 1)):
        x = x0 + (x1 - x0) * q / total
        c.d.line((x, y0 - 10, x, y0 + rows * rh + 6), fill=(90, 110, 190, 90), width=1)
        text_c(c, str(q), x, y0 + rows * rh + 28, 24, DIM)
    for i, (label, t0, t1, cname) in enumerate(items):
        a = stag(p, i, rows)
        if a <= 0:
            continue
        cc = col(c, cname)
        xa, xb = x0 + (x1 - x0) * t0 / total, x0 + (x1 - x0) * (t0 + (t1 - t0) * ease(a)) / total
        y = y0 + i * rh + rh / 2
        box(c, xa, y - rh * 0.36, max(xb, xa + 6), y + rh * 0.36, tuple(int(v * 0.5) for v in cc), cc, r=10)
        text_c(c, label, 135, y, 28, TEXT, a=a, maxw=190)


def p_eq(c, P, p, u):
    lines = P["lines"]
    n = len(lines)
    size = P.get("size", 54)
    gap = min(110, 440 / max(1, n))
    y0 = P.get("y", 690) - (n - 1) * gap / 2
    cm = P.get("cols", [])
    for i, s in enumerate(lines):
        a = stag(p, i, n)
        if a <= 0:
            continue
        cc = col(c, cm[i] if i < len(cm) else ("g" if i == n - 1 else "w"))
        text_c(c, s, 540, y0 + i * gap + 14 * (1 - a), size, cc, a=a, maxw=900)


def p_pie(c, P, p, u):
    fr = P["fracs"]
    cols = P.get("cols", ["g", "r", "c", "y", "p"])
    cx, cy, r = 540, P.get("y", 690), P.get("r", 190)
    a0 = -90.0
    prog = ease(p)
    for i, f in enumerate(fr):
        sw = 360 * f * prog
        c.d.pieslice((cx - r, cy - r, cx + r, cy + r), a0, a0 + sw, fill=tuple(col(c, cols[i % len(cols)])) + (255,), outline=(20, 24, 58, 255), width=3)
        if P.get("labels") and prog > 0.9:
            mid = math.radians(a0 + sw / 2)
            text_c(c, P["labels"][i], cx + (r * 0.58) * math.cos(mid), cy + (r * 0.58) * math.sin(mid), 34, (20, 24, 58))
        a0 += sw


def p_numline(c, P, p, u):
    lo, hi = P["min"], P["max"]
    x0, x1, y = 130, 950, P.get("y", 690)
    c.d.line((x0, y, x1, y), fill=(190, 200, 240, 255), width=6)
    for v in P.get("ticks", []):
        x = x0 + (x1 - x0) * (v - lo) / (hi - lo)
        c.d.line((x, y - 14, x, y + 14), fill=(190, 200, 240, 255), width=4)
        text_c(c, str(v), x, y + 44, 30, DIM)
    marks = P.get("marks", [])
    for i, (v, label, cname) in enumerate(marks):
        a = stag(p, i, len(marks))
        if a <= 0:
            continue
        x = x0 + (x1 - x0) * (v - lo) / (hi - lo)
        cc = col(c, cname)
        c.d.ellipse((x - 14, y - 14 - 60 * (1 - a), x + 14, y + 14 - 60 * (1 - a)), fill=tuple(cc) + (255,))
        text_c(c, label, x, y - 56 - (i % 2) * 44, 32, cc, a=a, maxw=300)


KINDS = {"head": p_head, "foot": p_foot, "big": p_big, "row": p_row, "bars": p_bars, "grid": p_grid, "nodes": p_nodes, "tl": p_tl, "eq": p_eq,
         "pie": p_pie, "numline": p_numline}


def dsl(c):
    beats = c.P["beats"]
    bi = min(int(c.T), len(beats) - 1)
    u = c.T - int(c.T)
    for P in beats[bi]:
        at = P.get("at", 0.0)
        dur = P.get("dur", 0.28)
        if u < at:
            continue
        p = clamp((u - at) / dur)
        KINDS[P["k"]](c, P, p, u)


def register():
    scenes.SCENES["dsl"] = dsl
