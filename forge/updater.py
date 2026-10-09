"""Self-update from the GitHub repo. The friend sees a banner when a newer VERSION is published and applies it with one click.
User data (data/, models/, output/, settings.json, .venv/) is never touched."""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import requests

from . import BRANCH, REPO, ROOT, VERSION

RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
KEEP = {".venv", "data", "models", "output", "settings.json", ".git", ".update_tmp", "pip_install.log"}
_state = {"checked": 0, "latest": VERSION, "notes": "", "available": False, "error": ""}


def _ver(v):
    out = []
    for p in v.strip().lstrip("v").split("."):
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    return tuple(out + [0] * (3 - len(out)))


def check(force=False) -> dict:
    if not force and time.time() - _state["checked"] < 1800:
        return dict(_state, current=VERSION)
    try:
        latest = requests.get(RAW + "/VERSION", timeout=6).text.strip()
        notes = ""
        try:
            notes = requests.get(RAW + "/CHANGELOG.md", timeout=6).text
            first = notes.split("\n## ")
            notes = ("## " + first[1] if len(first) > 1 else notes)[:900]
        except Exception:
            pass
        _state.update(checked=time.time(), latest=latest, notes=notes, available=_ver(latest) > _ver(VERSION), error="")
    except Exception as e:
        _state.update(checked=time.time(), error=str(e)[:120])
    return dict(_state, current=VERSION)


def apply() -> dict:
    """download the repo zip, copy changed app files over this folder, reinstall requirements if they changed"""
    url = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.zip"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    tmp = Path(tempfile.mkdtemp(prefix="forge_update_"))
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(tmp)
    src = next(p for p in tmp.iterdir() if p.is_dir())
    old_req = (ROOT / "requirements.txt").read_text() if (ROOT / "requirements.txt").exists() else ""
    n = 0
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        if rel.parts[0] in KEEP or p.is_dir():
            continue
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        n += 1
    new_req = (ROOT / "requirements.txt").read_text()
    if new_req != old_req:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")], cwd=ROOT)
    shutil.rmtree(tmp, ignore_errors=True)
    return {"files": n, "reinstalled": new_req != old_req}


def restart():
    """relaunch this process (the UI reloads itself once the server is back)"""
    os.execv(sys.executable, [sys.executable] + sys.argv)
