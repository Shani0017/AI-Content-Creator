import os
"""Spec -> finished 1080x1920 video. Pure Pillow + ffmpeg (no browser needed), so it runs the same on any Windows PC.

spec = {
  "title", "subtitle", "tags": [..], "cta_tag",
  "beats": [ {"say": str, "steps": [html-ish lines], "stamp": (text, "#hex") | None, "answer": str | None, "cards": [str] | None} ... ]
}
Step lines may contain <span class="y|g|p|c|r">coloured</span> runs. Number cards pop in on the spoken number unless "cards" is given.
"""
import math
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import paths, scenes, speech

W, H, FPS = 1080, 1920, 30
HEAD, GAP, TAIL = 0.5, 0.28, 1.3
STAGE_TOP, STAGE_BOT = 335, 1285

THEMES = {
    "midnight": dict(bg1=(10, 14, 34), bg2=(40, 20, 62), y=(255, 216, 77), g=(125, 255, 138), p=(255, 92, 138), c=(95, 211, 255), r=(255, 92, 138)),
    "ocean": dict(bg1=(6, 22, 40), bg2=(10, 58, 74), y=(255, 226, 120), g=(110, 255, 190), p=(255, 140, 120), c=(100, 220, 255), r=(255, 110, 130)),
    "sunset": dict(bg1=(30, 12, 28), bg2=(74, 24, 38), y=(255, 200, 80), g=(150, 255, 150), p=(255, 110, 160), c=(120, 200, 255), r=(255, 90, 100)),
    "forest": dict(bg1=(8, 24, 18), bg2=(16, 50, 38), y=(250, 224, 100), g=(130, 255, 150), p=(255, 130, 150), c=(120, 220, 230), r=(255, 110, 110)),
}
DEFAULT_STYLE = dict(pattern="checker", cell=90, glow=(540, 820, 400), glow_col="y", glow_a=34, panel="round", head="center", chip="pill")


def random_theme(rng):
    """a fresh dark palette: random hue family, accent colours spread around the wheel"""
    import colorsys
    h = rng.random()
    rgb = lambda hh, ss, vv: tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hh % 1, ss, vv))
    sp = rng.choice([0.07, 0.1, 0.14])
    return dict(bg1=rgb(h, rng.uniform(.55, .85), rng.uniform(.10, .16)), bg2=rgb(h + sp, rng.uniform(.45, .8), rng.uniform(.22, .34)),
                y=rgb(h + rng.choice([0.5, 0.45, 0.55]), rng.uniform(.5, .75), 1.0), g=rgb(h + .33, .55, 1.0),
                p=rgb(h + .83, .6, 1.0), c=rgb(h + .6, .55, 1.0), r=rgb(h + .95, .65, 1.0))


def random_style(rng):
    return dict(pattern=rng.choice(["checker", "dots", "stripes", "grid", "rings", "none"]), cell=rng.choice([70, 90, 120, 150]),
                gx=rng.uniform(.2, .8), gy=rng.uniform(.25, .6),
                glow=(rng.randint(250, 830), rng.randint(520, 1100), rng.randint(280, 480)), glow_col=rng.choice(["y", "c", "p", "g"]),
                glow_a=rng.randint(26, 52), panel=rng.choice(["round", "sharp", "soft"]), panel_style=rng.choice(["fill", "outline"]),
                head=rng.choice(["center", "center", "left"]), chip=rng.choice(["pill", "square"]),
                bar=rng.random() < 0.4, bar_col=rng.choice(["y", "c", "p", "g"]))


CARD = (18, 24, 58)
TEXT = (255, 255, 255)
DIM = (150, 160, 200)
LABEL = (201, 210, 255)

_fonts = {}


def font(size, bold=True):
    k = (size, bold)
    if k not in _fonts:
        f = paths.FONTS / ("Poppins-ExtraBold.ttf" if bold else "Poppins-SemiBold.ttf")
        try:
            _fonts[k] = ImageFont.truetype(str(f), size)
        except Exception:
            _fonts[k] = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", size)
    return _fonts[k]


def theme_from_palette(colors):
    """colors: list of (r,g,b) sampled from a reference video -> theme dict"""
    import colorsys
    if not colors:
        return THEMES["midnight"]
    hsv = [colorsys.rgb_to_hsv(*(c / 255 for c in col)) for col in colors]
    dark = min(hsv, key=lambda h: h[2])
    acc = max(hsv, key=lambda h: h[1] * 0.7 + h[2] * 0.3)
    h0 = acc[0]
    rgb = lambda h, s, v: tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h % 1, s, v))
    return dict(bg1=rgb(dark[0], min(.8, dark[1] + .2), .13), bg2=rgb(dark[0] + .07, .6, .26), y=rgb(h0, .7, 1.0), g=rgb(h0 + .33, .55, 1.0),
                p=rgb(h0 + .83, .6, 1.0), c=rgb(h0 + .5, .55, 1.0), r=rgb(h0 + .92, .65, 1.0))


# ------------------------------------------------------------------ html-ish runs
RUN = re.compile(r'<span class="(\w+)">(.*?)</span>', re.S)


def runs(html, theme):
    out, pos = [], 0
    for m in RUN.finditer(html):
        if m.start() > pos:
            out.append((_plain(html[pos:m.start()]), TEXT))
        col = theme.get(m.group(1), TEXT) if m.group(1) in theme else (DIM if m.group(1) == "dim" else (theme["g"] if m.group(1) == "gg" else TEXT))
        out.append((_plain(m.group(2)), col))
        pos = m.end()
    if pos < len(html):
        out.append((_plain(html[pos:]), TEXT))
    return [r for r in out if r[0]]


_GLYPH = {"â†’": "->", "â†": "<-", "â‰ ": "!=", "â‰ˆ": "~", "âœ“": "", "âœ—": "x", "â‰¥": ">=", "â‰¤": "<=", "âˆ’": "-", "â€¦": "...", "Â·": "-", "âˆž": "inf", "â‡„": "<->"}


def _plain(s):
    s = re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return "".join(_GLYPH.get(c, c) for c in s)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ sprites
def text_w(d, s, f):
    return d.textlength(s, font=f)


def shadowed(d, xy, s, f, fill, off=3):
    d.text((xy[0] + off, xy[1] + off), s, font=f, fill=(0, 0, 0, 200))
    d.text(xy, s, font=f, fill=fill)


def fit_font(d, s, size, maxw, bold=True):
    while size > 30 and text_w(d, s, font(size, bold)) > maxw:
        size -= 6
    return font(size, bold)


def card_sprite(text, label, col, size=100, maxw=860):
    text, label = _plain(text), _plain(label)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    f = fit_font(tmp, text, size, maxw - 120)
    lf = font(max(34, int(f.size * 0.42)), False)
    tw = text_w(tmp, text, f)
    lw = text_w(tmp, " " + label, lf) if label else 0
    w = int(tw + lw + 90)
    h = int(f.size * 1.5 + 30)
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((12, 24, w + 12, h + 24), radius=36, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle((12, 12, w + 12, h + 12), radius=36, fill=CARD + (240,), outline=(255, 255, 255, 40), width=5)
    cy = 12 + h / 2
    d.text((12 + 45, cy), text, font=f, fill=col, anchor="lm")
    if label:
        d.text((12 + 45 + tw, cy + 4), " " + label, font=lf, fill=LABEL, anchor="lm")
    return im


def big_sprite(text, col, size=190, maxw=1000):
    text = _plain(text)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    f = fit_font(tmp, text, size, maxw)
    w = int(text_w(tmp, text, f)) + 40
    h = int(f.size * 1.35)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    shadowed(d, (20, 4), text, f, col, off=5)
    return im


def stamp_sprite(text, col):
    text = _plain(text)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    f = font(110)
    w = int(text_w(tmp, text, f)) + 100
    h = 170
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, w + 20, h + 20), radius=26, fill=(11, 16, 36, 190), outline=col, width=10)
    d.text((20 + w / 2, 20 + h / 2 + 4), text, font=f, fill=col, anchor="mm")
    return im.rotate(6, expand=True, resample=Image.BICUBIC)


def pill_sprite(text, theme):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    f = font(52)
    w = int(text_w(tmp, text, f)) + 90
    im = Image.new("RGBA", (w, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 95), radius=48, fill=theme["y"])
    d.text((w / 2, 50), text, font=f, fill=(16, 23, 58), anchor="mm")
    return im


def check_sprite(col, size=140):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((6, 6, size - 6, size - 6), outline=col, width=9)
    d.line([(size * .27, size * .53), (size * .43, size * .69), (size * .76, size * .32)], fill=col, width=11, joint="curve")
    return im


def board_text_sprite(rn, size=84, maxw=900, max_lines=3):
    """big centred text in the middle of the stage, wrapped to fit. rn = [(text, colour)]; digits are highlighted when colour is plain"""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    toks = []
    for t, col in rn:
        for w_ in t.split():
            toks.append((w_, col))
    while True:
        f = font(size)
        sp = text_w(tmp, " ", f)
        lines, cur, cw = [], [], 0.0
        for w_, col in toks:
            ww = text_w(tmp, w_, f)
            if cur and cw + sp + ww > maxw:
                lines.append(cur); cur, cw = [], 0.0
            cur.append((w_, col, ww))
            cw += (sp if len(cur) > 1 else 0) + ww
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines or size <= 44:
            break
        size -= 6
    lh = int(size * 1.32)
    im = Image.new("RGBA", (maxw + 80, lh * len(lines) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for li, ln in enumerate(lines):
        tw = sum(w[2] for w in ln) + sp * (len(ln) - 1)
        x = (im.width - tw) / 2
        for w_, col, ww in ln:
            c = col
            shadowed(d, (x, 8 + li * lh), w_, f, c, off=4)
            x += ww + sp
    return im


def two_line_sprite(l1, l2, c2):
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    f = font(92)
    w = int(max(text_w(tmp, l1, f), text_w(tmp, l2, f))) + 50
    im = Image.new("RGBA", (w, 230), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    shadowed(d, (w / 2 - text_w(d, l1, f) / 2, 6), l1, f, TEXT)
    shadowed(d, (w / 2 - text_w(d, l2, f) / 2, 112), l2, f, c2)
    return im


# ------------------------------------------------------------------ easing
def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out_back(x, s=2.2):
    x = max(0.0, min(1.0, x)) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


STOP = {"a", "an", "the", "of", "is", "are", "and", "to", "in", "on", "per", "for", "it", "that", "so", "if", "then", "each", "every", "than", "but",
        "or", "at", "with", "from", "by", "as", "you", "he", "she", "they", "we", "i", "was", "were", "be", "not", "no", "now", "back", "more"}


def b_say(s):
    return _plain(s).strip()


OPS = {"times": "Ã—", "plus": "+", "minus": "-", "over": "/"}
EQ = {"is", "equals", "makes", "gives"}


def number_cards(words):
    """[(time, text, label)]: spoken numbers become cards; 'three times nine is twenty-seven' becomes one '3 Ã— 9 = 27' card"""
    ws = []
    for w in words:
        if ws and w["w"].startswith(".") and ws[-1]["w"][-1:].isdigit():
            ws[-1] = {"w": ws[-1]["w"] + w["w"], "s": ws[-1]["s"], "e": w["e"]}
        else:
            ws.append(dict(w))
    bare = lambda x: x["w"].strip(".,!?;:")
    isnum = lambda x: bool(re.search(r"\d", x["w"]))
    out, seen, i = [], set(), 0
    while i < len(ws):
        w = ws[i]
        if not isnum(w):
            i += 1
            continue
        txt, j = bare(w), i
        while True:                                   # chain: num (op num)* (is num)?
            nxt = ws[j + 1] if j + 1 < len(ws) else None
            nxt2 = ws[j + 2] if j + 2 < len(ws) else None
            nxt3 = ws[j + 3] if j + 3 < len(ws) else None
            if nxt and bare(nxt).lower() in OPS and nxt2 and isnum(nxt2) and not ws[j]["w"].endswith((".", "?", "!")):
                txt += f" {OPS[bare(nxt).lower()]} {bare(nxt2)}"; j += 2; continue
            if nxt and bare(nxt).lower() == "divided" and nxt2 and bare(nxt2).lower() == "by" and nxt3 and isnum(nxt3):
                txt += f" Ã· {bare(nxt3)}"; j += 3; continue
            if nxt and bare(nxt).lower() in EQ and nxt2 and isnum(nxt2) and not ws[j]["w"].endswith((".", "?", "!")):
                txt += f" = {bare(nxt2)}"; j += 2; continue
            break
        label = ""
        if j == i and j + 1 < len(ws) and not ws[j]["w"].endswith((".", ",", "?", "!")):
            nx = bare(ws[j + 1]).lower()
            if nx.isalpha() and nx not in STOP:
                label = nx
        if txt not in seen:
            seen.add(txt)
            out.append((w["s"], txt, label))
        i = j + 1
    return out


# ------------------------------------------------------------------ main
def render(spec, out_path, theme=None, voice=None, speed=1.04, progress=None, bpm=92, key=0):
    import soundfile as sf
    say = lambda p, m: progress(p, m) if progress else None
    th = theme or THEMES["midnight"]
    beats = spec["beats"]
    n = len(beats)

    # 1) voice-over + word timings
    track, t, plans = [], HEAD, []
    for i, b in enumerate(beats):
        say(0.02 + 0.28 * i / n, f"Voice-over {i + 1}/{n}")
        wav, sr = speech.speak(b["say"], voice, speed)
        wav = np.concatenate([np.zeros(int(0.04 * sr), np.float32), wav, np.zeros(int(0.08 * sr), np.float32)])
        words = speech.words(wav, sr, b["say"])
        words = [dict(w, s=w["s"], e=w["e"]) for w in words]
        dur = len(wav) / sr
        plans.append(dict(i=i, t0=t, dur=dur, words=words, wav=wav, sr=sr))
        t += dur + GAP
    total = t - GAP + TAIL

    # 2) elements
    els = []        # dict(img, cx, y, t0, t1, fx)
    sfx_ev = []     # (time, kind)
    steps = []      # (time, runs, clear)
    caps = []       # chunks: (t0, t1, [(word, s, e)])
    last = n - 1

    scene = spec.get("scene")
    sparams = spec.get("params") or {}

    def row(items):
        """illustrated reels: key numbers / stamp / answer sit in one row under the illustration"""
        gap, W_AV, H_AV = 22, 940, 215
        k = 1.0
        for it in items:
            k = min(k, H_AV / it["img"].height)
        tw = sum(it["img"].width * k for it in items) + gap * (len(items) - 1)
        if tw > W_AV:
            k *= W_AV / tw
        for it in items:
            if k < 0.999:
                it["img"] = it["img"].resize((max(2, int(it["img"].width * k)), max(2, int(it["img"].height * k))), Image.LANCZOS)
        tw = sum(it["img"].width for it in items) + gap * (len(items) - 1)
        x = 540 - tw / 2
        cyr = 1160
        for it in items:
            it["cx"], it["y"] = int(x + it["img"].width / 2), int(cyr - it["img"].height / 2)
            x += it["img"].width + gap
            els.append(it)

    def stack(items):
        """items: [dict(img, t0, t1, fx)] -> vertically centred inside the board; scaled down if they would not fit"""
        if scene:
            return row(items)
        gap = 30
        avail = STAGE_BOT - STAGE_TOP - 40
        tot = sum(it["img"].height for it in items) + gap * (len(items) - 1)
        if tot > avail:
            k = avail / tot
            for it in items:
                it["img"] = it["img"].resize((max(2, int(it["img"].width * k)), max(2, int(it["img"].height * k))), Image.LANCZOS)
            tot = sum(it["img"].height for it in items) + gap * (len(items) - 1)
        y = (STAGE_TOP + STAGE_BOT) / 2 - tot / 2
        for it in items:
            it["cx"], it["y"] = 540, int(y)
            y += it["img"].height + gap
            els.append(it)

    for p in plans:
        i, t0, dur, words = p["i"], p["t0"], p["dur"], p["words"]
        sb = beats[i]
        t1 = t0 + dur + 0.18
        items = []
        if i == last and sb.get("cta", True):
            cta = [dict(img=pill_sprite(spec.get("cta_tag", "BRAIN TEASER"), th), t0=t0, t1=total, fx="pop"),
                   dict(img=two_line_sprite("Follow for more", "brain teasers", th["y"]), t0=t0 + 0.4, t1=total, fx="up")]
            gy = 650
            for it in cta:                      # centred on the board even for illustrated reels
                it["cx"], it["y"] = 540, gy
                gy += it["img"].height + 40
                els.append(it)
            sfx_ev += [(t0, "pop"), (t0 + 0.4, "pop")]
            cta_start = t0
        else:
            has_ans = bool(sb.get("answer"))
            cards = sb.get("cards")
            found = [] if sb.get("nocards") else ([(t0 + 0.25 + 0.5 * k, c, "") for k, c in enumerate(cards or [])] if cards else [(t0 + s, tx, lb) for s, tx, lb in number_cards(words)])
            maxc = 2 if (has_ans or sb.get("stamp")) else 3
            for k, (tt, tx, lb) in enumerate(found[:maxc]):
                size = (84 if len(tx) <= 5 else 70) if scene else (128 if len(tx) <= 5 else (100 if len(tx) <= 8 else 78))
                items.append(dict(img=card_sprite(tx, lb, th["y"], size, maxw=900), t0=max(t0, tt - 0.06), t1=t1, fx=("left", "right", "up")[k % 3]))
                sfx_ev.append((tt, "pop"))
            if sb.get("stamp"):
                tx, col = sb["stamp"]
                items.append(dict(img=stamp_sprite(tx, hexrgb(col) if isinstance(col, str) else col), t0=t0 + dur * 0.35, t1=t1, fx="slam"))
                sfx_ev.append((t0 + dur * 0.35, "buzz" if tx == "WRONG" else "hit"))
            if has_ans:
                items.append(dict(img=big_sprite(sb["answer"], th["g"], 190 if len(sb["answer"]) <= 6 else 140), t0=t0 + dur * 0.45, t1=t1, fx="pop"))
                items.append(dict(img=check_sprite(th["g"], 120), t0=t0 + dur * 0.45 + 0.25, t1=t1, fx="pop"))
                sfx_ev.append((t0 + dur * 0.45, "chime"))
            if scene:
                pass
            elif len(items) < 2 and sb.get("steps") and not has_ans:
                lines = [runs(x, th) for x in sb["steps"]]
                items.append(dict(img=board_text_sprite(lines[-1]), t0=t0 + 0.12, t1=t1, fx="up"))
            elif not items and not has_ans and not scene:
                first = re.split(r"(?<=[.!?])\s", b_say(sb["say"]))[0]
                if len(first) > 90:
                    first = first[:90].rsplit(" ", 1)[0]
                items.append(dict(img=board_text_sprite([(first.rstrip(".,"), th["y"])]), t0=t0 + 0.35, t1=t1, fx="up"))
            if i == 0 and not items:
                items.append(dict(img=pill_sprite(spec.get("hook_tag", "CAN YOU SOLVE IT?"), th), t0=t0 + 0.4, t1=t1, fx="pop"))
            elif i == 0 and not scene:
                items.append(dict(img=pill_sprite(spec.get("hook_tag", "CAN YOU SOLVE IT?"), th), t0=t0 + 0.5, t1=t1, fx="pop"))
            for k, line in enumerate(sb.get("steps") or []):
                steps.append((t0 + 0.3 + k * max(0.6, (dur - 0.6) / max(1, len(sb["steps"]))), runs(line, th), k == 0))
        if items:
            stack(items)
        cur = []                                                    # caption chunks of up to 3 words
        for w in words:
            cur.append((w["w"], t0 + w["s"], t0 + w["e"]))
            if len(cur) >= 3 or w["w"].endswith((".", "?", "!", ",")):
                caps.append((cur[0][1], t0 + dur + 0.1 if w is words[-1] else cur[-1][2] + 0.25, cur))
                cur = []
        if cur:
            caps.append((cur[0][1], t0 + dur + 0.1, cur))

    # 3) audio
    say(0.32, "Mixing audio")
    SR = speech.SR
    buf = np.zeros(int((total + 1) * SR), np.float32)
    buf += speech.music_bed(total + 1, bpm, key)[:len(buf)]
    for p in plans:
        w = p["wav"]
        if p["sr"] != SR:
            w = np.interp(np.linspace(0, len(w) - 1, int(len(w) * SR / p["sr"])), np.arange(len(w)), w).astype(np.float32)
        a = int(p["t0"] * SR)
        buf[a:a + len(w)] += w * 0.95
    cache = {}
    for tt, kind in sfx_ev:
        s = cache.setdefault(kind, speech.sfx(kind))
        a = int(tt * SR)
        if a + len(s) < len(buf):
            buf[a:a + len(s)] += s * 0.55
    buf /= max(1.0, float(np.abs(buf).max()) / 0.92)
    wav_path = paths.CACHE / f"_mix_{os.getpid()}.wav"
    sf.write(wav_path, buf, SR)

    # 4) static background + header (look comes from spec["style"]: every video gets its own pattern / layout / palette)
    st = spec.get("style") or DEFAULT_STYLE
    yy = np.linspace(0, 1, H)[:, None, None]
    px = np.zeros((H, W, 3), np.float32)
    px[:] = np.array(th["bg1"], np.float32) * (1 - yy) + np.array(th["bg2"], np.float32) * yy
    gx, gy = np.meshgrid(np.arange(W), np.arange(H))
    pat, cell = st.get("pattern", "checker"), st.get("cell", 90)
    if pat == "checker":
        px += 6 * (((gx // cell) + (gy // cell)) % 2)[..., None]
    elif pat == "dots":
        px += 14 * (((gx % cell - cell / 2) ** 2 + (gy % cell - cell / 2) ** 2) < (cell * 0.12) ** 2)[..., None]
    elif pat == "stripes":
        px += 7 * ((((gx + gy) // (cell // 2)) % 2))[..., None]
    elif pat == "grid":
        px += 12 * (((gx % cell) < 2) | ((gy % cell) < 2))[..., None]
    elif pat == "rings":
        r = np.hypot(gx - W * st.get("gx", 0.5), gy - H * st.get("gy", 0.4))
        px += 9 * ((r // (cell * 1.2)) % 2)[..., None]
    bg = Image.fromarray(np.clip(px, 0, 255).astype(np.uint8), "RGB")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gcx, gcy, gr = st.get("glow", (540, 820, 400))
    ImageDraw.Draw(glow).ellipse((gcx - gr, gcy - gr, gcx + gr, gcy + gr), fill=th[st.get("glow_col", "y")] + (st.get("glow_a", 34),))
    bg = Image.alpha_composite(bg.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(120))).convert("RGB")
    d = ImageDraw.Draw(bg, "RGBA")
    rad = {"round": 44, "sharp": 8, "soft": 70}.get(st.get("panel", "round"), 44)
    fill_a = 0 if st.get("panel_style") == "outline" else 12
    d.rounded_rectangle((45, STAGE_TOP - 15, W - 45, STAGE_BOT + 5), radius=rad, fill=(255, 255, 255, fill_a), outline=(255, 255, 255, 60 if fill_a == 0 else 34), width=3)
    left = st.get("head") == "left"
    f = fit_font(d, spec.get("title", ""), 76, 960)
    tx0 = 60 if left else (W - text_w(d, spec.get("title", ""), f)) / 2
    shadowed(d, (tx0, 96), spec.get("title", ""), f, TEXT)
    sub = _plain(spec.get("subtitle", ""))
    sf_ = fit_font(d, sub, 36, 980, False)
    if left:
        d.text((60, 205), sub, font=sf_, fill=LABEL, anchor="lm")
    else:
        d.text((W / 2, 205), sub, font=sf_, fill=LABEL, anchor="mm")
    if st.get("bar"):
        d.rectangle((0, 0, W, 14), fill=th[st.get("bar_col", "y")] + (255,))
    tags = spec.get("tags") or []
    tf = font(26, False)
    tw = [text_w(d, tg, tf) + 40 for tg in tags]
    x = 60 if left else (W - (sum(tw) + 14 * max(0, len(tw) - 1))) / 2
    crad = 21 if st.get("chip", "pill") == "pill" else 6
    for tg, wd in zip(tags, tw):
        d.rounded_rectangle((x, 250, x + wd, 292), radius=crad, fill=(255, 255, 255, 28), outline=(255, 255, 255, 60), width=2)
        d.text((x + wd / 2, 272), tg, font=tf, fill=LABEL, anchor="mm")
        x += wd + 14
    d.rounded_rectangle((30, 1448, W - 30, 1766), radius=34, fill=(11, 16, 36, 235), outline=(255, 255, 255, 36), width=3)
    line_cache = {}

    def step_sprite(rn, dim):
        k = (id(rn), dim)
        if k not in line_cache:
            f2 = font(50, False)
            tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
            total_w = sum(text_w(tmp, s, f2) for s, _ in rn)
            im = Image.new("RGBA", (int(total_w) + 20, 64), (0, 0, 0, 0))
            dd = ImageDraw.Draw(im)
            xx2 = 6
            for s, col in rn:
                dd.text((xx2, 4), s, font=f2, fill=(tuple(int(c * 0.55) for c in col) if dim else col))
                xx2 += text_w(dd, s, f2)
            line_cache[k] = im
        return line_cache[k]

    cap_cache = {}

    def caption(ch, now):
        act = max((i for i, (_, s, _) in enumerate(ch) if s <= now + 0.02), default=0)
        key_ = (id(ch), act)
        if key_ not in cap_cache:
            f3 = font(66)
            tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
            ws = [c[0] for c in ch]
            widths = [text_w(tmp, w_ + " ", f3) for w_ in ws]
            im = Image.new("RGBA", (int(sum(widths)) + 30, 120), (0, 0, 0, 0))
            dd = ImageDraw.Draw(im)
            xx2 = 12
            for i, w_ in enumerate(ws):
                shadowed(dd, (xx2, 8), w_, f3, th["y"] if i == act else TEXT, off=4)
                xx2 += widths[i]
            cap_cache[key_] = im
        return cap_cache[key_]

    cta_t = cta_start if (beats[-1].get('cta', True) and scene) else 1e9

    # 5) frames -> ffmpeg
    say(0.35, "Rendering frames")
    nframes = int(total * FPS)
    tmp_v = paths.CACHE / f"_frames_{os.getpid()}.mp4"
    ff = subprocess.Popen([paths.FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(tmp_v)], stdin=subprocess.PIPE)
    for fi in range(nframes):
        now = fi / FPS
        fr = bg.copy()
        if scene and now < cta_t:
            bi = max((q["i"] for q in plans if q["t0"] <= now), default=0)
            q = plans[bi]
            Tq = bi + clamp01((now - q["t0"]) / (q["dur"] + GAP))
            scenes.draw(fr, scene, Tq, th, sparams)
        for e in els:
            if not (e["t0"] <= now < e["t1"]):
                continue
            age = now - e["t0"]
            img, cx, y, a = e["img"], e["cx"], e["y"], 1.0
            fx = e["fx"]
            if fx == "pop":
                s = 0.55 + 0.45 * ease_out_back(age / 0.42)
            elif fx == "slam":
                s = 1 + 1.6 * (1 - ease_out(age / 0.2))
            else:
                s = 1.0
            if fx == "up":
                y += 70 * (1 - ease_out(age / 0.42))
            if fx == "left":
                cx -= 160 * (1 - ease_out(age / 0.42))
            if fx == "right":
                cx += 160 * (1 - ease_out(age / 0.42))
            a = min(1.0, age / 0.12)
            if e["t1"] - now < 0.22:
                a = min(a, max(0.0, (e["t1"] - now) / 0.22))
            if s != 1.0:
                img = img.resize((max(2, int(img.width * s)), max(2, int(img.height * s))), Image.BILINEAR)
            if a < 1.0:
                img = img.copy()
                img.putalpha(img.getchannel("A").point(lambda v, a=a: int(v * a)))
            fr.paste(img, (int(cx - img.width / 2), int(y + (e["img"].height - img.height) / 2)), img)
        # working-out panel
        slot, vis = 0, []
        for (ts, rn, clr) in steps:
            if ts > now:
                break
            if clr or slot >= 4:
                vis, slot = [], 0
            vis.append(rn)
            slot += 1
        for k, rn in enumerate(vis):
            spr = step_sprite(rn, k < len(vis) - 1)
            fr.paste(spr, (60, 1478 + k * 70), spr)
        for (c0, c1, ch) in caps:
            if c0 - 0.02 <= now < c1:
                spr = caption(ch, now)
                fr.paste(spr, (int((W - spr.width) / 2), 1318), spr)
                break
        ff.stdin.write(fr.tobytes())
        if fi % 60 == 0:
            say(0.35 + 0.6 * fi / nframes, f"Rendering {fi}/{nframes}")
    ff.stdin.close()
    ff.wait()
    say(0.97, "Finishing")
    subprocess.run([paths.FFMPEG, "-v", "error", "-y", "-i", str(tmp_v), "-i", str(wav_path), "-c:v", "copy", "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out_path)], check=True)
    say(1.0, "Done")
    return total

