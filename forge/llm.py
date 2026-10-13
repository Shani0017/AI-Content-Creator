"""Ollama client: the local model writes problems, scripts and reference 'recipes'. Everything else (maths, rendering) is plain code."""
import json
import re

import requests

from . import settings


def base() -> str:
    return settings.get("ollama_url").rstrip("/")


def status() -> dict:
    try:
        r = requests.get(base() + "/api/tags", timeout=2.5)
        models = [m["name"] for m in r.json().get("models", [])]
        return {"up": True, "models": models}
    except Exception:
        return {"up": False, "models": []}


def pick_model() -> str:
    want = settings.get("ollama_model")
    st = status()
    if not st["up"]:
        raise RuntimeError("Ollama is not running. Start the Ollama app, then try again.")
    if want and want in st["models"]:
        return want
    if st["models"]:
        return st["models"][0]
    raise RuntimeError("No Ollama model installed. Open Settings and pull one (for example llama3.2:3b).")


def chat(prompt: str, system: str = "", json_mode: bool = False, temperature: float = 0.7, timeout: int = 300) -> str:
    model = pick_model()
    body = {
        "model": model,
        "stream": False,
        "options": {"temperature": temperature},
        "messages": ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}],
    }
    if json_mode:
        body["format"] = "json"
    r = requests.post(base() + "/api/chat", json=body, timeout=timeout)
    r.raise_for_status()
    return r.json()["message"]["content"]


def chat_json(prompt: str, system: str = "", temperature: float = 0.7, retries: int = 2):
    last = None
    for _ in range(retries + 1):
        txt = chat(prompt, system, json_mode=True, temperature=temperature)
        try:
            return json.loads(txt)
        except Exception:
            m = re.search(r"[\[{].*[\]}]", txt, re.S)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception as e:
                    last = e
            last = last or ValueError("model did not return JSON")
    raise last


def pull(model: str, on_progress=None):
    """download a model through Ollama (streams progress)"""
    with requests.post(base() + "/api/pull", json={"name": model, "stream": True}, stream=True, timeout=None) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            d = json.loads(line)
            if on_progress and d.get("total"):
                on_progress(d.get("completed", 0) / d["total"], d.get("status", ""))
            if d.get("error"):
                raise RuntimeError(d["error"])


# ------------------------------------------------------------------ prompts
def math_problems(n: int, topics: str = "", level: str = "easy to medium") -> list:
    """AI-written word problems. Each answer is double-checked by solving the problem again in a fresh call."""
    out = []
    tries = 0
    while len(out) < n and tries < n * 8:
        tries += 1
        data = chat_json(
            f"Write ONE original short word problem or logic puzzle for a viral 40-second video ({level}). {('Theme: ' + topics) if topics else ''}\n"
            "It must have a single numeric or short answer and a classic 'most people get it wrong' trap if possible.\n"
            'Return JSON: {"headline": "video title", "title": "2-4 word on-screen title", "subtitle": "short line with the key numbers", '
            '"question": "the problem written for a narrator, 1-2 sentences, numbers written in words", '
            '"trap": "the common wrong answer, one sentence", "working": ["step 1 sentence", "step 2 sentence", "step 3 sentence"], '
            '"answer": "final answer, short", "steps": ["short working-out line 1", "line 2", "line 3"]}',
            system="You write clear, correct puzzles. Double-check the arithmetic. Output JSON only.",
            temperature=0.9,
        )
        try:
            q, ans = data["question"], str(data["answer"])
            check = chat(f"Solve this and reply with ONLY the final answer, no words:\n{q}", temperature=0.0, timeout=120)
            norm = lambda s: re.sub(r"[^a-z0-9.]", "", s.lower())
            if norm(check) and (norm(ans) in norm(check) or norm(check) in norm(ans)):
                out.append(data)
        except Exception:
            continue
    return out


PLACEHOLDER_BITS = ("how it opens", "explaining something", "3 different", "three different", "6 words", "one or two words", "fast|medium|slow",
                    "how the title", "same style", "original topic", "ideas in", "topic idea")


def _real(v) -> bool:
    s = str(v or "").strip().lower()
    return len(s) > 3 and not any(b in s for b in PLACEHOLDER_BITS)


def valid_recipe(d) -> bool:
    return (isinstance(d, dict) and d.get("category") in ("balls", "music", "math", "story") and _real(d.get("topic"))
            and isinstance(d.get("new_topic_ideas"), list) and sum(_real(x) for x in d["new_topic_ideas"]) >= 2)


def heuristic_recipe(transcript: str, title: str, desc: str, stats: dict) -> dict:
    """no AI needed: category and topic from the words, hashtags and measured pacing"""
    import re
    text = f"{title} {desc} {transcript}".lower()
    words = re.findall(r"[a-z']+", transcript.lower())
    if re.search(r"#(math|mathpuzzle|riddle|brainteaser|iq)|\b(how many|calculate|solve|equation|percent|riddle|puzzle|plus|minus|times)\b", text):
        cat = "math"
    elif re.search(r"#(asmr|satisfying|oddlysatisfying|physics)|\b(asmr|satisfying|marble|balls?)\b", text) and len(words) < 25:
        cat = "balls"
    elif re.search(r"#(piano|xylophone|musicvideo|melody)|\b(piano|xylophone|melody|guess the song)\b", text) and len(words) < 25:
        cat = "music"
    elif len(words) >= 25:
        cat = "story"
    else:
        cat = "balls"
    base = re.sub(r"#\w+|https?://\S+", "", title or "").strip() or " ".join(words[:8]) or "a short video"
    topic = " ".join(base.split()[:9])
    ideas = {"math": ["a speed and distance word problem", "a percentage trick question", "a counting puzzle with a surprising answer"],
             "balls": ["balls dropping through pegs", "marbles filling a shape", "a collision chain reaction"],
             "music": ["a classic lullaby on bells", "a nursery rhyme on a xylophone", "a famous march on drums"],
             "story": [f"a surprising fact related to {topic[:40]}", f"three myths about {topic[:40]}", f"how {topic[:40]} really works"]}[cat]
    return {"category": cat, "topic": topic, "hook": "opens straight on the subject" if len(words) else "opens on the visual", "pacing": stats.get("pacing", "medium"),
            "tone": "informative" if cat in ("story", "math") else "calm", "new_topic_ideas": ideas, "title_style": "short and direct", "from": "heuristic"}


EXAMPLE = {"category": "story", "topic": "why cats purr when they are happy", "hook": "opens with a surprising question",
           "pacing": "fast", "tone": "playful", "new_topic_ideas": ["why dogs tilt their heads", "how birds sleep while flying", "why we yawn when others yawn"],
           "title_style": "a short question"}


def analyze_reference(transcript: str, stats: dict, title: str = "", desc: str = "") -> dict:
    """AI recipe, checked: placeholder answers (a small model echoing the instructions) are rejected, then retried, then replaced by a rule-based recipe"""
    ctx = (f"Title: {title[:200]}\nDescription / hashtags: {desc[:400]}\nMeasured: {json.dumps(stats)}\n"
           f"Spoken words: {transcript[:2500] or '(no speech)'}")
    prompts = [
        "Study this short video and describe it so a NEW original video can be made in the same style.\n" + ctx +
        "\n\nReply with ONE JSON object with exactly these keys: category, topic, hook, pacing, tone, new_topic_ideas, title_style.\n"
        'category must be one of "balls" (satisfying physics / ASMR), "music" (melody played by objects), "math" (puzzles, riddles), "story" (facts, tips, explainers, anything spoken).\n'
        "Fill every value with REAL content about THIS video. Example of a correctly filled answer for a different video:\n" + json.dumps(EXAMPLE),
        "Give a JSON object describing this video. Be specific, no placeholders.\n" + ctx + "\nExample format (different video):\n" + json.dumps(EXAMPLE),
    ]
    for pr in prompts:
        try:
            d = chat_json(pr, system="You output only a JSON object with real, specific values.", temperature=0.4, retries=0)
            if valid_recipe(d):
                d["from"] = "ai"
                d.setdefault("pacing", stats.get("pacing", "medium"))
                return d
        except Exception:
            pass
    return heuristic_recipe(transcript, title, desc, stats)


def story_script(topic: str, style: dict, beats: int = 6) -> dict:
    return chat_json(
        f"Write an original 30-45 second voice-over script about: {topic}.\nStyle: {json.dumps(style)}\n"
        f"Exactly {beats} beats. Each beat is 1-2 short spoken sentences (numbers in words). Open with a hook, end with a call to action to follow.\n"
        'Return JSON: {"headline": "video title", "title": "2-4 word on-screen title", "subtitle": "one short line", '
        '"beats": [{"say": "spoken sentence(s)", "key": "1-4 word on-screen highlight", "bullets": ["optional short line", "optional short line"]}]}',
        system="You write punchy, accurate short-form scripts. Original wording only. Output JSON only.", temperature=0.8,
    )
