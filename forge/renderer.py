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

from . import paths, speech

W, H, FPS = 1080, 1920, 30
HEAD, GAP, TAIL = 0.5, 0.28, 1.3

THEMES = {
    "midnight": dict(bg1=(10, 14, 34), bg2=(40, 20, 62), y=(255, 216, 77), g=(125, 255, 138), p=(255, 92, 138), c=(95, 211, 255), r=(255, 92, 138)),
    "ocean": dict(bg1=(6, 22, 40), bg2=(10, 58, 74), y=(255, 226, 120), g=(110, 255, 190), p=(255, 140, 120), c=(100, 220, 255), r=(255, 110, 130)),
    "sunset": dict(bg1=(30, 12, 28), bg2=(74, 24, 38), y=(255, 200, 80), g=(150, 255, 150), p=(255, 110, 160), c=(120, 200, 255), r=(255, 90, 100)),
    "forest": dict(bg1=(8, 24, 18), bg2=(16, 50, 38), y=(250, 224, 100), g=(130, 255, 150), p=(255, 130, 150), c=(120, 220, 230), r=(255, 110, 110)),
}
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


_GLYPH = {"→": "->", "←": "<-", "≠": "!=", "≈": "~", "✓": "", "✗": "x", "≥": ">=", "≤": "<=", "−": "-", "…": "...", "·": "-", "∞": "inf", "⇄": "<->"}


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
    lf = font(42, False)
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
def ease_out_back(x, s=2.2):
    x = max(0.0, min(1.0, x)) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


STOP = {"a", "an", "the", "of", "is", "are", "and", "to", "in", "on", "per", "for", "it", "that", "so", "if", "then", "each", "every", "than", "but",
        "or", "at", "with", "from", "by", "as", "you", "he", "she", "they", "we", "i", "was", "were", "be", "not", "no", "now", "back", "more"}


def number_cards(words):
    ws = []
    for w in words:
        if ws and w["w"].startswith(".") and ws[-1]["w"][-1:].isdigit():
            ws[-1] = {"w": ws[-1]["w"] + w["w"], "s": ws[-1]["s"], "e": w["e"]}
        else:
            ws.append(dict(w))
    out, seen = [], set()
    for i, w in enumerate(ws):
        if not re.search(r"\d", w["w"]):
            continue
        txt = w["w"].strip(".,!?;:")
        if not txt or txt in seen:
            continue
        seen.add(txt)
        label = ""
        if i + 1 < len(ws) and not w["w"].endswith((".", ",", "?", "!")):
            nxt = ws[i + 1]["w"].strip(".,!?;:").lower()
            if nxt.isalpha() and nxt not in STOP:
                label = nxt
        out.append((w["s"], txt, label))
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
    for p in plans:
        i, t0, dur, words = p["i"], p["t0"], p["dur"], p["words"]
        sb = beats[i]
        t1 = t0 + dur + 0.18
        if i == last and sb.get("cta", True):
            els.append(dict(img=pill_sprite(spec.get("cta_tag", "BRAIN TEASER"), th), cx=540, y=650, t0=t0, t1=total, fx="pop"))
            els.append(dict(img=two_line_sprite("Follow for more", "brain teasers", th["y"]), cx=540, y=820, t0=t0 + 0.4, t1=total, fx="up"))
            sfx_ev += [(t0, "pop"), (t0 + 0.4, "pop")]
        else:
            has_ans = bool(sb.get("answer"))
            ys = [380, 585] if has_ans else [380, 585, 790]
            cards = sb.get("cards")
            items = [(t0 + 0.25 + 0.5 * k, c, "") for k, c in enumerate(cards or [])] if cards else [(t0 + s, tx, lb) for s, tx, lb in number_cards(words)]
            for k, (tt, tx, lb) in enumerate(items[:len(ys)]):
                size = 100 if len(tx) <= 6 else (80 if len(tx) <= 9 else 62)
                els.append(dict(img=card_sprite(tx, lb, th["y"], size), cx=540, y=ys[k], t0=max(t0, tt - 0.06), t1=t1, fx=("left", "right", "up")[k % 3]))
                sfx_ev.append((tt, "pop"))
            if i == 0:
                els.append(dict(img=pill_sprite(spec.get("hook_tag", "CAN YOU SOLVE IT?"), th), cx=540, y=1110, t0=t0 + 0.5, t1=t1, fx="pop"))
            if sb.get("stamp"):
                tx, col = sb["stamp"]
                els.append(dict(img=stamp_sprite(tx, hexrgb(col) if isinstance(col, str) else col), cx=540, y=900, t0=t0 + dur * 0.35, t1=t1, fx="slam"))
                sfx_ev.append((t0 + dur * 0.35, "buzz" if tx == "WRONG" else "hit"))
            if has_ans:
                els.append(dict(img=big_sprite(sb["answer"], th["g"], 190 if len(sb["answer"]) <= 6 else 140), cx=540, y=905, t0=t0 + dur * 0.45, t1=t1, fx="pop"))
                els.append(dict(img=check_sprite(th["g"]), cx=540, y=1140, t0=t0 + dur * 0.45 + 0.25, t1=t1, fx="pop"))
                sfx_ev.append((t0 + dur * 0.45, "chime"))
            for k, line in enumerate(sb.get("steps") or []):
                steps.append((t0 + 0.3 + k * max(0.6, (dur - 0.6) / max(1, len(sb["steps"]))), runs(line, th), k == 0))
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
    wav_path = paths.CACHE / "_mix.wav"
    sf.write(wav_path, buf, SR)

    # 4) static background + header
    bg = Image.new("RGB", (W, H))
    px = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    px[:] = np.array(th["bg1"], np.float32) * (1 - yy) + np.array(th["bg2"], np.float32) * yy
    xx = np.arange(W)[None, :, None]
    px += 6 * (((xx // 90) + (np.arange(H)[:, None, None] // 90)) % 2)         # faint checker texture
    bg = Image.fromarray(np.clip(px, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(bg, "RGBA")
    f = fit_font(d, spec.get("title", ""), 70, 960)
    shadowed(d, ((W - text_w(d, spec.get("title", ""), f)) / 2, 96), spec.get("title", ""), f, TEXT)
    sf_ = fit_font(d, spec.get("subtitle", ""), 36, 980, False)
    d.text((W / 2, 205), spec.get("subtitle", ""), font=sf_, fill=LABEL, anchor="mm")
    tags = spec.get("tags") or []
    tf = font(26, False)
    tw = [text_w(d, tg, tf) + 40 for tg in tags]
    x = (W - (sum(tw) + 14 * max(0, len(tw) - 1))) / 2
    for tg, wd in zip(tags, tw):
        d.rounded_rectangle((x, 250, x + wd, 292), radius=21, fill=(255, 255, 255, 28), outline=(255, 255, 255, 60), width=2)
        d.text((x + wd / 2, 272), tg, font=tf, fill=LABEL, anchor="mm")
        x += wd + 14
    d.rounded_rectangle((30, 1448, W - 30, 1766), radius=34, fill=(11, 16, 36, 235), outline=(255, 255, 255, 36), width=3)
    line_cache = {}

    def step_sprite(rn, dim):
        k = (id(rn), dim)
        if k not in line_cache:
            f2 = font(48, False)
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

    # 5) frames -> ffmpeg
    say(0.35, "Rendering frames")
    nframes = int(total * FPS)
    tmp_v = paths.CACHE / "_frames.mp4"
    ff = subprocess.Popen([paths.FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(tmp_v)], stdin=subprocess.PIPE)
    for fi in range(nframes):
        now = fi / FPS
        fr = bg.copy()
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
