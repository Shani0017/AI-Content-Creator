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
    if not force and time.time() - _state["checked"] < 600:
        return dict(_state, current=VERSION)
    try:
        def fetch(path):
            """GitHub's API is always current (the raw link can lag by minutes); fall back to raw"""
            try:
                r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{path}", params={"ref": BRANCH},
                                 headers={"Accept": "application/vnd.github.raw"}, timeout=8)
                if r.ok:
                    return r.text
            except Exception:
                pass
            return requests.get(f"{RAW}/{path}", params={"t": int(time.time())}, headers={"Cache-Control": "no-cache"}, timeout=8).text

        latest = fetch("VERSION").strip()
        notes = ""
        try:
            notes = fetch("CHANGELOG.md")
            first = notes.split("\n## ")
            notes = ("## " + first[1] if len(first) > 1 else notes)[:900]
        except Exception:
            pass
        _state.update(checked=time.time(), latest=latest, notes=notes, available=_ver(latest) > _ver(VERSION), error="")
    except Exception as e:
        _state.update(checked=time.time(), error="Could not reach GitHub (" + str(e)[:80] + "). Check the internet connection.")
    return dict(_state, current=VERSION)


def apply() -> dict:
    """download the repo zip, copy changed app files over this folder, reinstall requirements if they changed.
    Files that cannot be replaced (locked by antivirus / another program) are skipped and reported instead of failing the whole update."""
    url = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.zip"
    r = None
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=180)
            r.raise_for_status()
            break
        except Exception as e:
            if attempt == 2:
                raise RuntimeError("Could not download the update from GitHub (" + str(e)[:120] + "). Check the internet connection and try again.")
            time.sleep(2)
    tmp = Path(tempfile.mkdtemp(prefix="fu_"))
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(tmp)
    src = next(p for p in tmp.iterdir() if p.is_dir())
    req = ROOT / "requirements.txt"
    old_req = req.read_text(encoding="utf-8", errors="ignore") if req.exists() else ""
    n, skipped = 0, []
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        if rel.parts[0] in KEEP or p.is_dir():
            continue
        dst = ROOT / rel
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                try:
                    os.chmod(dst, 0o666)
                except Exception:
                    pass
            shutil.copy2(p, dst)
            n += 1
        except Exception as e:
            skipped.append(f"{rel}: {str(e)[:60]}")
    new_req = req.read_text(encoding="utf-8", errors="ignore") if req.exists() else ""
    if new_req != old_req:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)], cwd=ROOT, timeout=900)
        except Exception:
            pass
    shutil.rmtree(tmp, ignore_errors=True)
    return {"files": n, "reinstalled": new_req != old_req, "skipped": skipped[:5]}


def restart():
    """start a fresh copy that waits for this one to release the port, then stop this one.
    (os.execv does not replace the process on Windows, which left nothing running after an update)"""
    env = dict(os.environ, FORGE_NO_BROWSER="1", FORGE_WAIT_PORT="1")      # the open browser tab reloads itself
    flags = (0x00000008 | 0x08000000) if os.name == "nt" else 0            # DETACHED_PROCESS | CREATE_NO_WINDOW
    subprocess.Popen([sys.executable, str(ROOT / "app.py")], env=env, cwd=str(ROOT), creationflags=flags, close_fds=True)
    time.sleep(0.3)
    os._exit(0)
