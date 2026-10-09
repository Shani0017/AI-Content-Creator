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
    while len(out) < n and tries < n * 3:
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


def analyze_reference(transcript: str, stats: dict) -> dict:
    return chat_json(
        "You analyse a short-form video so someone can make a NEW, original video in the same style.\n"
        f"Stats: {json.dumps(stats)}\nTranscript:\n{transcript[:3500]}\n\n"
        'Return JSON: {"category": one of ["balls","music","math","story"], "topic": "what it is about in 6 words", '
        '"hook": "how it opens", "pacing": "fast|medium|slow", "tone": "one or two words", '
        '"new_topic_ideas": ["3 different original topics in the same style"], "title_style": "how the title is written"}\n'
        'Use "balls" for satisfying physics / ASMR loops, "music" for melody-played-by-objects, "math" for puzzles / word problems / riddles, '
        '"story" for facts, tips, explainers, stories or anything spoken.',
        system="Output JSON only.", temperature=0.3,
    )


def story_script(topic: str, style: dict, beats: int = 6) -> dict:
    return chat_json(
        f"Write an original 30-45 second voice-over script about: {topic}.\nStyle: {json.dumps(style)}\n"
        f"Exactly {beats} beats. Each beat is 1-2 short spoken sentences (numbers in words). Open with a hook, end with a call to action to follow.\n"
        'Return JSON: {"headline": "video title", "title": "2-4 word on-screen title", "subtitle": "one short line", '
        '"beats": [{"say": "spoken sentence(s)", "key": "1-4 word on-screen highlight", "bullets": ["optional short line", "optional short line"]}]}',
        system="You write punchy, accurate short-form scripts. Original wording only. Output JSON only.", temperature=0.8,
    )
