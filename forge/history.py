"""Remembers what this install has already made so it never makes the same video twice (kept in data/history.json)."""
import hashlib
import json
import re
import threading

from . import paths

FILE = paths.DATA / "history.json"
_LOCK = threading.Lock()


def sig(text: str) -> str:
    """stable fingerprint of a puzzle / script: lower-case words only, so number formatting and punctuation do not hide a repeat"""
    s = re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def _load() -> dict:
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def seen(kind: str) -> set:
    return set(_load().get(kind, []))


def add(kind: str, *sigs) -> None:
    with _LOCK:
        d = _load()
        cur = d.setdefault(kind, [])
        for s in sigs:
            if s not in cur:
                cur.append(s)
        FILE.parent.mkdir(parents=True, exist_ok=True)
        FILE.write_text(json.dumps(d), encoding="utf-8")


def forget(kind: str) -> None:
    with _LOCK:
        d = _load()
        d.pop(kind, None)
        FILE.write_text(json.dumps(d), encoding="utf-8")


def seen_list(kind: str) -> list:
    """ordered log (repeats allowed) - used to rotate through simulations evenly"""
    return list(_load().get("log_" + kind, []))


def add_log(kind: str, item: str) -> None:
    with _LOCK:
        d = _load()
        d.setdefault("log_" + kind, []).append(item)
        FILE.parent.mkdir(parents=True, exist_ok=True)
        FILE.write_text(json.dumps(d), encoding="utf-8")
