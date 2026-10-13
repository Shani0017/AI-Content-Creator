"""The four content generators. Each takes (params, out_dir, progress) and returns a list of finished video paths."""
import random
import re
import time
from pathlib import Path

from . import families, llm, paths, renderer, settings

SAFE = re.compile(r'[\\/:*?"<>|]')


def _name(s):
    return SAFE.sub("", s).strip()[:110] or "video"


def _out(out_dir: Path, title: str, ext=".mp4") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / (_name(title) + ext)
    k = 2
    while p.exists():
        p = out_dir / f"{_name(title)} ({k}){ext}"
        k += 1
    return p


# ------------------------------------------------------------------ catalog for the UI
def catalog():
    import sims_a, sims_b, sims_c, sims_d, sims_e, sims_f, sims_h, sims_i
    balls = []
    for mod in (sims_a, sims_b, sims_c, sims_d, sims_e, sims_f):
        for cls in getattr(mod, "BATCH_" + mod.__name__[-1].upper()):
            balls.append({"id": f"{mod.__name__}.{cls.__name__}", "name": getattr(cls, "TITLE", cls.__name__).title(), "sub": getattr(cls, "SUB", "")})
    return {
        "balls": balls,
        "songs": list(sims_i.SONGS),
        "scenes": [{"id": k, "name": v[1].split(" - ")[0].replace("{s}", "").strip()} for k, v in sims_i.CLASSES.items()],
        "math_families": [f.__name__[2:] for f in families.FAMILIES],
        "themes": list(renderer.THEMES),
    }


# ------------------------------------------------------------------ balls
def _pick_sims(hint: str, pool: list, k: int = 3) -> list:
    """rank the simulations by how well their name / one-line description matches the reference text"""
    import re
    syn = {"orb": "ball", "orbs": "ball", "pearl": "ball", "sphere": "ball", "bouncing": "bounce", "bounces": "bounce", "bouncy": "bounce",
           "marbles": "marble", "balls": "ball", "dominoes": "domino", "pendulums": "pendulum", "pegs": "peg", "bricks": "brick",
           "swirl": "swirl", "spiral": "spiral", "hexagon": "hexagon", "circle": "circle", "ring": "ring", "rings": "ring", "gravity": "gravity",
           "orbit": "orbit", "magnet": "magnet", "sand": "sand", "sort": "sort", "wave": "wave", "balls": "ball", "bubbles": "bubble", "heart": "heart"}
    toks = {syn.get(t, t) for t in re.findall(r"[a-z]+", hint.lower()) if len(t) > 2}
    scored = []
    for cls in pool:
        text = f"{cls.__name__} {getattr(cls, 'TITLE', '')} {getattr(cls, 'SUB', '')}".lower()
        words = {syn.get(t, t) for t in re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", text))}
        score = len(toks & words) + (2 if "bounce" in toks and ("bounc" in text) else 0) + (1 if "ball" in toks and "ball" in text else 0)
        if "bounce" in toks and words & {"circle", "hexagon", "ring", "walls", "wall", "inside"}:
            score += 3                                                    # bouncing inside a shape is the closest look
        if re.search(r"xylo|piano|music|melody|note", text) and not re.search(r"music|song|piano|xylo|melody|tune", hint.lower()):
            score -= 4                                                    # musical scenes only when the reference is musical
        if re.search(r"letters|word|smiley|heart|sunset|sort|string|rose|mandala|epicycle", text) and score < 5:
            score -= 2
        scored.append((score, cls))
    scored.sort(key=lambda x: -x[0])
    best = [c for sc, c in scored if sc > 0][:k]
    return best


def balls(params, out_dir, progress):
    import importlib
    import audit2, core
    import sims_a, sims_b, sims_c, sims_d, sims_e, sims_f  # noqa: F401
    count = int(params.get("count", 1))
    chosen = params.get("sims") or []
    pool = []
    for mod in ("sims_a", "sims_b", "sims_c", "sims_d", "sims_e", "sims_f"):
        m = importlib.import_module(mod)
        for cls in getattr(m, "BATCH_" + mod[-1].upper()):
            if not chosen or f"{mod}.{cls.__name__}" in chosen:
                pool.append(cls)
    rng = random.Random(params.get("seed") or time.time())
    matched = _pick_sims(params.get("hint", ""), pool) if (not chosen and params.get("hint")) else []
    out = []
    for k in range(count):
        cls = matched[k % len(matched)] if matched else (pool[k % len(pool)] if chosen else rng.choice(pool))
        for _ in range(12):
            seed = rng.randint(1, 10 ** 6)
            attrs = {"SEED": seed}
            if params.get("bg"):
                attrs["BG"] = tuple(int(v) for v in params["bg"])
            C = type(cls.__name__ + "_s", (cls,), attrs)
            progress((k + 0.1) / count, f"Checking physics ({cls.__name__})")
            name, length, issues, _ = audit2.audit(C)
            if not issues:
                break
        else:
            continue
        title = f"{getattr(cls, 'TITLE', cls.__name__).title()} - Satisfying ASMR #shorts"
        p = _out(out_dir, title)
        progress((k + 0.3) / count, f"Rendering {p.stem}")
        core.run(C, p)
        out.append(p)
        progress((k + 1) / count, f"Finished {k + 1}/{count}")
    return out


# ------------------------------------------------------------------ music
def music(params, out_dir, progress):
    import audit2, core, sims_i
    count = int(params.get("count", 1))
    songs = params.get("songs") or list(sims_i.SONGS)
    scenes = params.get("scenes")
    if not scenes:                                      # reference given: choose the scene that matches its description
        hint = f"{params.get('topic', '')} {(params.get('style') or {}).get('hook', '')}".lower()
        for key, sc in (("xylophone", "xylo"), ("piano", "xylo"), ("drum", "drum"), ("bell", "bell"), ("glass", "glass"),
                        ("brick", "brick"), ("bounc", "pads"), ("ball", "pads"), ("marble", "pads")):
            if key in hint:
                scenes = [sc]
                break
    scenes = scenes or list(sims_i.ORDER)
    rng = random.Random(params.get("seed") or time.time())
    theme_hue = params.get("hue")
    out = []
    for k in range(count):
        kind = scenes[k % len(scenes)] if len(scenes) > 1 else scenes[0]
        song = songs[(k * 5 + rng.randint(0, 7)) % len(songs)]
        C, title, th = sims_i.themed(kind, song, rng.randint(0, 9999))
        if theme_hue is not None:
            th["hue"] = float(theme_hue)
        if params.get("bg"):
            C.BG = tuple(int(v) for v in params["bg"])
        if params.get("duration"):
            C.TARGET = float(min(60, max(20, params["duration"])))
        if params.get("pace") == "fast":
            C.STEPS = [x * 0.85 for x in C.STEPS]
        elif params.get("pace") == "slow":
            C.STEPS = [x * 1.2 for x in C.STEPS]
        sims_i.activate(th)
        ok = False
        for seed in range(3, 12):
            C.SEED = seed
            progress((k + 0.1) / count, f"Checking physics ({song})")
            name, length, issues, _ = audit2.audit(C)
            if not issues:
                ok = True
                break
        if not ok:
            continue
        sims_i.activate(th)
        p = _out(out_dir, title)
        progress((k + 0.3) / count, f"Rendering {song}")
        core.run(C, p)
        out.append(p)
        progress((k + 1) / count, f"Finished {k + 1}/{count}")
    return out


# ------------------------------------------------------------------ math
def _ai_spec(d):
    """LLM problem -> renderer spec (steps are plain lines)"""
    working = d.get("working") or []
    steps = d.get("steps") or []
    beats = [dict(say=d["question"], steps=steps[:1]),
             dict(say=d.get("trap") or "Most people get this wrong.", stamp=("WRONG", "#ff5c8a"), steps=[])]
    for k, w in enumerate(working[:3]):
        beats.append(dict(say=w, steps=[steps[k + 1]] if k + 1 < len(steps) else []))
    beats.append(dict(say=f"The answer is {d['answer']}.", answer=str(d["answer"]), steps=[]))
    beats.append(dict(say="Follow for more brain teasers."))
    return dict(title=d.get("title", "Brain Teaser"), subtitle=d.get("subtitle", ""), tags=["WORD PROBLEM", "PUZZLE"], beats=beats,
                headline=d.get("headline") or d.get("title") or "Brain Teaser")


def math(params, out_dir, progress):
    count = int(params.get("count", 1))
    source = params.get("source", "templates")          # templates | ai | mixed
    theme = renderer.THEMES.get(params.get("theme", "midnight"), renderer.THEMES["midnight"])
    if params.get("palette"):
        theme = renderer.theme_from_palette([tuple(c) for c in params["palette"]])
    specs = []
    if source in ("templates", "mixed"):
        allspecs = families.all_specs(115)
        fam = params.get("families")
        if fam:
            allspecs = [s for s in allspecs if s["family"][2:] in fam]
        random.Random(params.get("seed") or time.time()).shuffle(allspecs)
        want = count if source == "templates" else (count + 1) // 2
        specs += allspecs[:want]
    if source in ("ai", "mixed"):
        want = count - len(specs)
        progress(0.02, "Asking the AI for problems")
        for d in llm.math_problems(want, params.get("topic", "")):
            specs.append(_ai_spec(d))
        if len(specs) < count:                          # the AI's answers failed the double-check: top up so the requested count is always made
            progress(0.03, f"AI gave {len(specs)} checked problems - adding {count - len(specs)} template ones")
            extra = families.all_specs(115)
            random.Random(params.get("seed") or time.time()).shuffle(extra)
            specs += extra[:count - len(specs)]
    out = []
    for k, sp in enumerate(specs[:count]):
        p = _out(out_dir, (sp.get("headline") or sp["title"]) + " #shorts")
        sp = dict(sp)
        renderer.render(sp, p, theme=theme, voice=params.get("voice"), bpm=84 + (k * 7) % 28, key=(k * 5) % 12,
                        progress=lambda f, m, k=k: progress((k + f) / max(1, len(specs[:count])), f"{k + 1}/{len(specs[:count])} - {m}"))
        out.append(p)
    return out


# ------------------------------------------------------------------ story / explainer (also used for reference imitation)
def story(params, out_dir, progress):
    theme = renderer.THEMES.get(params.get("theme", "midnight"), renderer.THEMES["midnight"])
    if params.get("palette"):
        theme = renderer.theme_from_palette([tuple(c) for c in params["palette"]])
    count = int(params.get("count", 1))
    topics = params.get("topics") or [params.get("topic") or "a surprising fact most people do not know"]
    style = params.get("style") or {}
    out = []
    for k in range(count):
        topic = topics[k % len(topics)]
        progress(k / count, f"Writing the script ({topic})")
        beats_n = int(params.get("beats") or max(4, min(9, round((params.get("duration") or 36) / 6))))
        d = llm.story_script(topic, style, beats=beats_n)
        beats = []
        for b in d["beats"]:
            beats.append(dict(say=b["say"], cards=[b["key"]] if b.get("key") else None, steps=[x for x in (b.get("bullets") or [])][:3]))
        beats[-1]["cta"] = False
        beats.append(dict(say="Follow for more.", cta=True))
        sp = dict(title=d.get("title", "Did You Know"), subtitle=d.get("subtitle", ""), tags=["STORY", "FACTS"], beats=beats, cta_tag="WATCH TILL THE END", hook_tag="LISTEN CLOSELY")
        p = _out(out_dir, (d.get("headline") or d.get("title") or topic) + " #shorts")
        renderer.render(sp, p, theme=theme, voice=params.get("voice"), bpm=88, key=(k * 3) % 12,
                        progress=lambda f, m, k=k: progress((k + f) / count, f"{k + 1}/{count} - {m}"))
        out.append(p)
    return out


GENERATORS = {"balls": balls, "music": music, "math": math, "story": story}
