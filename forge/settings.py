import json
import threading

from . import ROOT

_FILE = ROOT / "settings.json"
_LOCK = threading.Lock()
DEFAULTS = {
    "ollama_url": "http://127.0.0.1:11434",
    "ollama_model": "",
    "voice": "af_heart",
    "whisper_model": "small.en",
    "auto_update_check": True,
}


def load() -> dict:
    with _LOCK:
        data = dict(DEFAULTS)
        try:
            data.update(json.loads(_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
        return data


def save(patch: dict) -> dict:
    with _LOCK:
        data = dict(DEFAULTS)
        try:
            data.update(json.loads(_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
        data.update({k: v for k, v in patch.items() if k in DEFAULTS})
        _FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data


def get(key):
    return load().get(key)
