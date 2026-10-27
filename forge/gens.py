"""The four content generators. Each takes (params, out_dir, progress) and returns a list of finished video paths."""
import json
import random
import re
import time
from pathlib import Path

from . import families, history, llm, paths, renderer, settings

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
        "ray_shapes": [x[0] for x in __import__("rays").SHAPES],
        "lineups": list(LINEUPS),
        "piano_songs": list(sims_h.SONGS),
        "story_series": json.loads((Path(__file__).with_name("story_series.json")).read_text(encoding="utf-8")),
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
    history_log = history.seen_list("balls")
    rng = random.Random(params.get("seed") or time.time())
    matched = _pick_sims(params.get("hint", ""), pool) if (not chosen and params.get("hint")) else []
    out = []
    for k in range(count):
        if matched:
            cls = matched[k % len(matched)]
        elif chosen:
            cls = pool[k % len(pool)]
        else:                                           # least-used simulation first (random among equals): batches and later runs do not repeat
            cnt = {c.__name__: history_log.count(c.__name__) for c in pool}
            low = min(cnt.values())
            cls = rng.choice([c for c in pool if cnt[c.__name__] == low])
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
        history.add_log("balls", cls.__name__)
        history_log.append(cls.__name__)
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
    made = history.seen("music")
    out = []
    for k in range(count):
        combos = [(sc, so) for sc in scenes for so in songs]
        fresh = [c for c in combos if f"{c[0]}:{c[1]}" not in made]
        kind, song = rng.choice(fresh or combos)       # a scene + song pair is never made twice until every pair has been
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
        history.add("music", f"{kind}:{song}")
        made.add(f"{kind}:{song}")
        out.append(p)
        progress((k + 1) / count, f"Finished {k + 1}/{count}")
    return out


# ------------------------------------------------------------------ look (different every time)
def _look(params, rng, k=0):
    """-> (theme, style). theme 'auto' (default) = a new palette and layout for every video; a named theme keeps that palette but still varies the layout"""
    name = params.get("theme", "auto")
    if params.get("palette"):
        th = renderer.theme_from_palette([tuple(c) for c in params["palette"]])
    elif name in renderer.THEMES:
        th = renderer.THEMES[name]
    else:
        th = renderer.random_theme(rng)
    return th, renderer.random_style(rng)


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
    rng = random.Random(params.get("seed") or time.time())
    done = history.seen("math")
    specs = []
    if source in ("templates", "mixed"):
        allspecs = families.all_specs(230)
        fam = params.get("families")
        if fam:
            allspecs = [x for x in allspecs if x["family"][2:] in fam]
        fresh = [x for x in allspecs if history.sig(x["beats"][0]["say"]) not in done]
        rng.shuffle(fresh)
        by = {}                                          # spread over families so a batch is not five versions of one puzzle
        for x in fresh:
            by.setdefault(x["family"], []).append(x)
        order = []
        while any(by.values()):
            for f_ in rng.sample(list(by), len(by)):
                if by[f_]:
                    order.append(by[f_].pop(0))
        want = count if source == "templates" else (count + 1) // 2
        specs += order[:want]
    if source in ("ai", "mixed"):
        progress(0.02, "Asking the AI for problems")
        try:
            for d in llm.math_problems(count - len(specs) + 2, params.get("topic", "")):
                sp_ = _ai_spec(d)
                sg = history.sig(sp_["beats"][0]["say"])
                if sg in done or any(history.sig(x["beats"][0]["say"]) == sg for x in specs):
                    continue                              # this one was already made
                specs.append(sp_)
                if len(specs) >= count:
                    break
        except Exception:
            pass
        if len(specs) < count:                            # AI answers failed the double-check: top up with templates not made yet
            rest = [x for x in families.all_specs(230) if history.sig(x["beats"][0]["say"]) not in done and x not in specs]
            rng.shuffle(rest)
            progress(0.03, f"AI gave {len(specs)} checked problems - adding {count - len(specs)} template ones")
            specs += rest[:count - len(specs)]
    if len(specs) < count:
        progress(0.04, f"Only {len(specs)} new puzzles were left - every other one was already made")
    out = []
    for k, sp in enumerate(specs[:count]):
        theme, style = _look(params, rng, k)
        sp = dict(sp, style=style)
        p = _out(out_dir, (sp.get("headline") or sp["title"]) + " #shorts")
        renderer.render(sp, p, theme=theme, voice=params.get("voice"), bpm=rng.randint(80, 112), key=rng.randint(0, 11),
                        progress=lambda f, m, k=k: progress((k + f) / max(1, len(specs[:count])), f"{k + 1}/{len(specs[:count])} - {m}"))
        history.add("math", history.sig(sp["beats"][0]["say"]))
        out.append(p)
    return out


# ------------------------------------------------------------------ story / explainer (also used for reference imitation)
def story(params, out_dir, progress):
    rng = random.Random(params.get("seed") or time.time())
    count = int(params.get("count", 1))
    topics = params.get("topics") or [params.get("topic") or "a surprising fact most people do not know"]
    style = params.get("style") or {}
    done = history.seen("story")
    titles = []
    out = []
    for k in range(count):
        topic = topics[k % len(topics)]
        progress(k / count, f"Writing the script ({topic})")
        beats_n = int(params.get("beats") or max(4, min(9, round((params.get("duration") or 36) / 6))))
        d = None
        for attempt in range(4):                          # a script whose headline or opening was already made is rewritten from a new angle
            d = llm.story_script(topic, style, beats=beats_n, avoid=titles, temperature=min(1.1, 0.8 + 0.1 * attempt))
            head = d.get("headline") or d.get("title") or topic
            sg = history.sig(head + " " + (d["beats"][0]["say"] if d.get("beats") else ""))
            h_sig = history.sig(head)
            if sg not in done and h_sig not in done:
                break
            titles.append(head)
        theme, st = _look(params, rng, k)
        beats = []
        for b in d["beats"]:
            beats.append(dict(say=b["say"], cards=[b["key"]] if b.get("key") else None, steps=[x for x in (b.get("bullets") or [])][:3]))
        beats[-1]["cta"] = False
        beats.append(dict(say="Follow for more.", cta=True))
        sp = dict(title=d.get("title", "Did You Know"), subtitle=d.get("subtitle", ""), tags=["STORY", "FACTS"], beats=beats, cta_tag="WATCH TILL THE END",
                  hook_tag="LISTEN CLOSELY", style=st)
        p = _out(out_dir, (d.get("headline") or d.get("title") or topic) + " #shorts")
        renderer.render(sp, p, theme=theme, voice=params.get("voice"), bpm=rng.randint(80, 112), key=rng.randint(0, 11),
                        progress=lambda f, m, k=k: progress((k + f) / count, f"{k + 1}/{count} - {m}"))
        history.add("story", sg, h_sig)
        titles.append(d.get("headline") or d.get("title") or topic)
        out.append(p)
    return out



# ------------------------------------------------------------------ rays (rays bouncing inside a vessel: 1 -> 100 rays)
def rays(params, out_dir, progress):
    import rays as R
    count = int(params.get("count", 1))
    shapes = params.get("shapes") or []
    rng = random.Random(params.get("seed") or time.time())
    done = history.seen("rays")
    out = []
    for k in range(count):
        for _ in range(50):
            v = R.variant(rng, rng.choice(shapes) if shapes else None)
            if R.key(v) not in done:
                break
        title = f"Rays Bouncing In A {v['name']} {v['title']} - Satisfying ASMR #shorts"
        p = _out(out_dir, title)
        progress((k + 0.1) / count, f"Tracing rays ({v['name']}, {v['title']})")
        R.render(v, p)
        history.add("rays", R.key(v))
        done.add(R.key(v))
        out.append(p)
        progress((k + 1) / count, f"Finished {k + 1}/{count}")
    return out


# ------------------------------------------------------------------ country battle (flag balls shoot it out, last country standing)
LINEUPS = {
    "world": ["MY", "ID", "PH", "TH", "VN", "SG", "BR", "US", "JP", "IN", "KR", "CN", "FR", "DE", "ES", "AR"],
    "asia": ["MY", "ID", "PH", "TH", "VN", "SG", "JP", "KR", "CN", "IN", "PK"],
    "sea": ["MY", "ID", "PH", "TH", "VN", "SG", "JP", "KR"],
    "football": ["BR", "AR", "FR", "DE", "ES", "IT", "US", "JP", "KR", "NG", "MY", "ID"],
}
BATTLE_TITLES = {
    "world": ["16 Countries Go To War Only One Survives", "Country War - Which Flag Survives", "Country Ball War - Comment Your Country",
              "16 Flags Shoot It Out - Who Wins", "World War Of Flags - Last Country Standing"],
    "asia": ["Asian Country War - Last Country Standing", "Which Asian Country Wins The War", "Malaysia vs Indonesia vs All Of Asia - Country War",
             "Asian Flag War - Comment Your Country"],
    "sea": ["Malaysia vs Indonesia vs Philippines vs Thailand - Country War", "Southeast Asia War - Who Wins", "SEA Country War - Who Survives",
            "Malaysia Indonesia Philippines - Flag War"],
    "football": ["Football Nations War - Brazil vs Argentina vs The World", "Which Football Nation Wins The War",
                 "World Cup Country War - Last Flag Standing", "Football Countries Shoot It Out - Comment Your Team"],
}


def battle(params, out_dir, progress):
    import audit2, core, sims_g
    count = int(params.get("count", 1))
    kinds = params.get("lineups") or list(LINEUPS)
    rng = random.Random(params.get("seed") or time.time())
    used = history.seen("battle")
    out = []
    for k in range(count):
        kind = kinds[k % len(kinds)]
        teams = LINEUPS[kind][:]
        rng.shuffle(teams)
        for _ in range(30):
            C = type("ShootingBattle", (sims_g.ShootingBattle,), {"TEAMS": teams, "SEED": rng.randint(1, 10 ** 6)})
            progress((k + 0.1) / count, f"Checking the battle ({kind})")
            name, length, issues, _ = audit2.audit(C)
            if not issues:
                break
        else:
            continue
        pool = [t for t in BATTLE_TITLES[kind] if history.sig(t) not in used] or [f"{rng.choice(BATTLE_TITLES[kind])} {rng.randint(2, 99)}"]
        title = rng.choice(pool)
        p = _out(out_dir, f"{title} - Satisfying ASMR #shorts")
        progress((k + 0.3) / count, f"Rendering {title}")
        core.run(C, p)
        history.add("battle", history.sig(title), f"{kind}:{C.SEED}")
        used.add(history.sig(title))
        out.append(p)
        progress((k + 1) / count, f"Finished {k + 1}/{count}")
    return out


# ------------------------------------------------------------------ piano balls (every note is a ball that lands on its key)
def piano(params, out_dir, progress):
    import audit2, core, sims_h
    count = int(params.get("count", 1))
    songs = params.get("songs") or list(sims_h.SONGS)
    rng = random.Random(params.get("seed") or time.time())
    made = history.seen("piano")
    out = []
    for k in range(count):
        fresh = [x for x in songs if x not in made] or songs
        name = rng.choice(fresh)
        for seed in (3, 4, 5, 6, 7):
            C = sims_h.song(name, seed)
            progress((k + 0.1) / count, f"Checking timing ({name})")
            _, length, issues, _ = audit2.audit(C)
            if not issues:
                break
        else:
            continue
        p = _out(out_dir, f"Guess The Song - {name} Played By Falling Balls #shorts")
        progress((k + 0.3) / count, f"Rendering {name}")
        core.run(C, p)
        history.add("piano", name)
        made.add(name)
        out.append(p)
        progress((k + 1) / count, f"Finished {k + 1}/{count}")
    return out


# ------------------------------------------------------------------ interview questions (300 hand-checked problems with animated working-out)
def _iq_problems():
    import importlib, sys
    d = str(Path(__file__).resolve().parent / "iq")
    if d not in sys.path:
        sys.path.insert(0, d)
    import iq_engine
    iq_engine.register()
    probs = []
    for f in sorted(Path(d).glob("iq_problems_*.py")):
        probs += importlib.import_module(f.stem).PROBLEMS
    return iq_engine, [x for x in probs if "qparts" in x and "steps" in x]


def _iq_spec(E, pr):
    beats, parts = [], []
    hook = [{"k": "big", "text": pr["hook_text"], "col": "y", "size": 104, "y": 650, "dur": 0.2}]
    if pr.get("hook_sub"):
        hook[0]["sub"] = pr["hook_sub"]
    beats.append(dict(say=pr["hook_say"], nocards=True)); parts.append(hook)
    beats.append(dict(say=pr["q"], nocards=True, steps=[E.clean(x) for x in pr.get("qsteps", [])])); parts.append(pr["qparts"])
    for st in pr["steps"]:
        b = dict(say=st["say"], nocards=True)
        if st.get("steps"):
            b["steps"] = [E.clean(x) for x in st["steps"]]
        if st.get("stamp"):
            b["stamp"] = ("WRONG", "#ff5c8a") if st["stamp"] == "WRONG" else (st["stamp"], "#ffd24d")
        beats.append(b); parts.append(st["parts"])
    beats.append(dict(say=pr["ans_say"], answer=pr["ans"], nocards=True)); parts.append(pr.get("aparts", []))
    beats.append(dict(say="Follow for more interview questions.", nocards=True)); parts.append([])
    return dict(title=f"{pr['org']} Interview Question", subtitle=pr["sub"], tags=(pr["tag"], "INTERVIEW QUESTION"), headline=pr["title"],
                scene="dsl", params={"beats": parts}, cta_tag="INTERVIEW QUESTION", hook_tag="CAN YOU SOLVE IT?", beats=beats)


def interview(params, out_dir, progress):
    E, probs = _iq_problems()
    count = int(params.get("count", 1))
    rng = random.Random(params.get("seed") or time.time())
    done = history.seen("interview")
    fresh = [x for x in probs if history.sig(x["title"]) not in done]
    rng.shuffle(fresh)
    out = []
    for k, pr in enumerate(fresh[:count]):
        p = _out(out_dir, f"{pr['title']} - Interview Question")
        renderer.render(_iq_spec(E, pr), p, theme=renderer.THEMES["midnight"], voice="am_adam",
                        progress=lambda f, m, k=k: progress((k + f) / count, m))
        history.add("interview", history.sig(pr["title"]))
        out.append(p)
        progress((k + 1) / count, f"Finished {k + 1}/{count}")
    if not fresh:
        raise RuntimeError("All 300 interview questions have been made already.")
    return out


GENERATORS = {"balls": balls, "music": music, "math": math, "story": story, "rays": rays, "battle": battle, "piano": piano, "interview": interview}
