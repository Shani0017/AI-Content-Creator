"""One background worker runs queued jobs one at a time (rendering is heavy), with progress the UI can poll."""
import json
import queue
import subprocess
import threading
import time
import traceback
import uuid
from pathlib import Path

from . import gens, llm, paths, reference, settings, speech

JOBS: dict = {}
_Q: "queue.Queue" = queue.Queue()
_LOCK = threading.Lock()
LIB = paths.DATA / "library.json"


def _library() -> list:
    try:
        return json.loads(LIB.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_library(items):
    LIB.write_text(json.dumps(items, indent=1), encoding="utf-8")


def poster(video: Path) -> str:
    img = video.with_suffix(".jpg")
    if not img.exists():
        subprocess.run([paths.FFMPEG, "-v", "error", "-y", "-ss", "1.5", "-i", str(video), "-frames:v", "1", "-vf", "scale=360:-1", str(img)])
    return img.name


def submit(kind: str, params: dict) -> dict:
    jid = uuid.uuid4().hex[:8]
    job = {"id": jid, "kind": kind, "params": params, "state": "queued", "progress": 0.0, "message": "Waiting in queue", "files": [], "error": "",
           "created": time.time(), "log": []}
    with _LOCK:
        JOBS[jid] = job
    _Q.put(jid)
    return job


def _progress(job):
    def cb(frac, msg=""):
        job["progress"] = round(max(0.0, min(1.0, float(frac))), 3)
        if msg:
            job["message"] = msg
    return cb


def _run(job):
    kind, params = job["kind"], job["params"]
    cb = _progress(job)
    out_dir = paths.OUTPUT / {"balls": "Balls", "music": "Music", "math": "Math", "story": "Stories", "reference": "Reference", "rays": "Rays", "battle": "Country Battles", "piano": "Piano Balls", "interview": "Interview Questions"}.get(kind, "Other")
    if kind == "setup":
        speech.download_models(cb)
        return []
    if kind == "pull":
        llm.pull(params["model"], cb)
        return []
    if kind == "publish":
        from . import publisher
        plan = publisher.build_plan(int(params.get("per_day", 8)), int(params.get("days", 3)), params.get("start", ""))
        r = publisher.run_plan(plan, cb)
        job["message"] = f"Scheduled {r['scheduled']} videos"
        return []
    if kind == "youtube":
        from . import youtube
        r = youtube.run(params, cb)
        job["message"] = f"Scheduled {r['scheduled']} videos on YouTube"
        return []
    if kind == "reference":
        recipe = reference.analyze(params["url"], cb)
        job["recipe"] = recipe
        job["message"] = "Analysis ready - choose what to make"
        return []
    return gens.GENERATORS[kind](params, out_dir, cb)


def worker():
    while True:
        jid = _Q.get()
        job = JOBS.get(jid)
        if not job or job["state"] == "cancelled":
            continue
        job["state"] = "running"
        job["started"] = time.time()
        try:
            files = _run(job)
            job["files"] = [str(f) for f in files]
            lib = _library()
            for f in files:
                f = Path(f)
                lib.insert(0, {"name": f.stem, "path": str(f.relative_to(paths.OUTPUT)).replace("\\", "/"), "poster": poster(f), "kind": job["kind"],
                               "created": time.time(), "size": f.stat().st_size})
            if files:
                _save_library(lib)
            job["state"] = "done"
            job["progress"] = 1.0
            if not job.get("recipe"):
                job["message"] = f"Finished - {len(files)} video{'s' if len(files) != 1 else ''}" if files else "Finished"
        except Exception as e:
            job["state"] = "error"
            job["error"] = str(e)[:400]
            job["message"] = "Failed"
            job["log"].append(traceback.format_exc()[-1200:])


def start():
    t = threading.Thread(target=worker, daemon=True)
    t.start()


def listing():
    with _LOCK:
        return sorted((dict(j, params=None) for j in JOBS.values()), key=lambda j: -j["created"])[:30]


def library():
    lib = [x for x in _library() if (paths.OUTPUT / x["path"]).exists()]
    return lib
