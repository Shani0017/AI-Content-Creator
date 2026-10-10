"""Publish finished videos to a Facebook Page (native scheduling) and Instagram (via a tiny poster on a VPS).
Everything the user needs is entered in the app: IDs and tokens. Secrets live only in data/publish.json (never committed)."""
import base64
import datetime as dt
import hashlib
import io
import json
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

import requests

from . import jobs, paths

GRAPH = "v21.0"
CFG = paths.DATA / "publish.json"
PUBLISHED = paths.DATA / "published.json"
PLAN = paths.DATA / "plan.json"
DEFAULT = {"ig_user_id": "", "ig_token": "", "fb_page_id": "", "fb_page_token": "", "github_repo": "", "github_token": "", "brand": "", "handle": "",
           "slots": "08:30,10:30,12:30,14:30,16:30,19:00,20:30,22:30", "delete_after": True}
SECRET = ("ig_token", "fb_page_token", "github_token")

HOOKS = {"math": ["Can you solve it before the answer?", "Don't say the first answer that comes to mind...", "Most people get this one wrong. Do you?",
                  "Pause and think. Then watch the answer.", "Looks easy. It isn't."],
         "music": ["Guess the song! Comment the title below", "Turn the sound on. This one is so satisfying", "Every bounce plays a note. Do you know the tune?"],
         "balls": ["Watch till the end. So satisfying", "Turn the sound on for this one", "Relax and watch every collision"],
         "story": ["Wait for the ending", "Did you know this?", "Save this for later"],
         "reference": ["Wait for the ending", "Did you know this?"]}
ASK = {"math": "Comment your answer before you check", "music": "Which song is it? Comment your guess", "balls": "What should we simulate next? Tell us below",
       "story": "What do you think? Comment below", "reference": "What do you think? Comment below"}
TAGS = {"math": ["#brainteaser", "#mathpuzzle", "#riddles", "#iqtest", "#logicpuzzle"], "music": ["#satisfying", "#asmr", "#oddlysatisfying", "#relaxing", "#musicvideo"],
        "balls": ["#satisfying", "#asmr", "#oddlysatisfying", "#relaxing", "#physics"], "story": ["#didyouknow", "#facts", "#learn", "#shorts", "#reels"],
        "reference": ["#didyouknow", "#facts", "#learn", "#shorts", "#reels"]}


def load() -> dict:
    d = dict(DEFAULT)
    try:
        d.update(json.loads(CFG.read_text(encoding="utf-8")))
    except Exception:
        pass
    return d


def save(patch: dict) -> dict:
    d = load()
    for k, v in patch.items():
        if k in DEFAULT and not (k in SECRET and v in ("", None, "********")):
            d[k] = v
    CFG.write_text(json.dumps(d, indent=1), encoding="utf-8")
    return public()


def public() -> dict:
    d = load()
    out = {k: ("********" if k in SECRET and d[k] else "") if k in SECRET else d[k] for k in DEFAULT}
    out["ready"] = {"instagram": bool(d["ig_user_id"] and d["ig_token"]), "facebook": bool(d["fb_page_id"] and d["fb_page_token"]),
                    "hosting": bool(d["github_repo"] and d["github_token"])}
    return out


def posted() -> set:
    try:
        return set(json.loads(PUBLISHED.read_text()))
    except Exception:
        return set()


# ------------------------------------------------------------------ plan
def caption(item: dict, cfg: dict) -> str:
    kind = item.get("kind", "story")
    name = item["name"].replace(" #shorts", "").replace(" - Satisfying ASMR", "").strip()
    k = sum(map(ord, item["name"]))
    hooks = HOOKS.get(kind, HOOKS["story"])
    who = cfg.get("brand") or "us"
    tags = list(dict.fromkeys(TAGS.get(kind, TAGS["story"])))[:5]
    cta = f"Follow {who} for a new video every day"
    return f"{name}\n\n{hooks[k % len(hooks)]}\n{ASK.get(kind, ASK['story'])}\n{cta}\n\n" + " ".join(tags)


def build_plan(per_day: int, days: int, start: str = "", offset_hours=None) -> list:
    cfg = load()
    slots = [s.strip() for s in cfg["slots"].split(",") if s.strip()][:per_day]
    tz = dt.timezone(dt.timedelta(hours=offset_hours)) if offset_hours is not None else dt.datetime.now().astimezone().tzinfo
    day0 = dt.date.fromisoformat(start) if start else dt.date.today() + dt.timedelta(days=1)
    done = posted()
    pool = [v for v in jobs.library() if v["path"] not in done]
    by = {}
    for v in pool:
        by.setdefault(v["kind"], []).append(v)
    order, n = [], per_day * days
    kinds = [k for k in ("math", "balls", "music", "story", "reference") if by.get(k)]
    i = 0
    while len(order) < n and any(by.values()):
        k = kinds[i % len(kinds)]
        i += 1
        if by.get(k):
            order.append(by[k].pop(0))
    plan = []
    for j, v in enumerate(order):
        t = dt.datetime.combine(day0 + dt.timedelta(days=j // len(slots)), dt.time.fromisoformat(slots[j % len(slots)]), tzinfo=tz)
        plan.append({"n": j + 1, "time": t.isoformat(), "unix": int(t.timestamp()), "type": v["kind"], "file": v["path"], "name": v["name"],
                     "caption": caption(v, cfg)})
    return plan


# ------------------------------------------------------------------ hosting + Facebook
def _gh(cfg, method, path, **kw):
    h = {"Authorization": f"Bearer {cfg['github_token']}", "Accept": "application/vnd.github+json"}
    return requests.request(method, f"https://api.github.com/repos/{cfg['github_repo']}/{path}", headers=h, timeout=120, **kw)


def host(cfg, path: Path):
    name = hashlib.md5(str(path).encode()).hexdigest()[:12] + ".mp4"
    tmp = Path(tempfile.gettempdir()) / name
    subprocess.run([paths.FFMPEG, "-v", "error", "-y", "-i", str(path), "-c", "copy", "-movflags", "+faststart", str(tmp)], check=True)
    body = {"message": "tmp", "content": base64.b64encode(tmp.read_bytes()).decode()}
    old = _gh(cfg, "GET", f"contents/{name}")
    if old.ok:
        body["sha"] = old.json()["sha"]
    r = _gh(cfg, "PUT", f"contents/{name}", json=body)
    tmp.unlink(missing_ok=True)
    if not r.ok:
        raise RuntimeError(f"GitHub upload failed: {r.text[:160]}")
    return f"https://raw.githubusercontent.com/{cfg['github_repo']}/main/{name}", name, r.json()["content"]["sha"]


def fb_schedule(cfg, path: Path, caption_: str, when: int) -> str:
    tok, base = cfg["fb_page_token"], f"https://graph.facebook.com/{GRAPH}/{cfg['fb_page_id']}/video_reels"
    s = requests.post(base, data={"upload_phase": "start", "access_token": tok}, timeout=60).json()
    if "video_id" not in s:
        raise RuntimeError(f"Facebook start: {s.get('error', {}).get('message', s)}")
    data = path.read_bytes()
    u = requests.post(s["upload_url"], headers={"Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data))}, data=data, timeout=900)
    if not u.ok:
        raise RuntimeError(f"Facebook upload: {u.text[:160]}")
    f = requests.post(base, data={"upload_phase": "finish", "video_id": s["video_id"], "video_state": "SCHEDULED", "scheduled_publish_time": str(when),
                                  "description": caption_, "access_token": tok}, timeout=60).json()
    if not f.get("success", False):
        raise RuntimeError(f"Facebook finish: {f.get('error', {}).get('message', f)}")
    return s["video_id"]


def recycle(path: Path):
    ps = ("Add-Type -AssemblyName Microsoft.VisualBasic;[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('"
          + str(path).replace("'", "''") + "','OnlyErrorDialogs','SendToRecycleBin')")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps])


def run_plan(plan: list, progress=lambda f, m: None) -> dict:
    """host every video, schedule it on Facebook, publish plan.json for the Instagram poster, then clean up"""
    cfg = load()
    pub = public()["ready"]
    if not pub["hosting"]:
        raise RuntimeError("Add the GitHub repo and token in Publish > Accounts first.")
    done, out = posted(), []
    for i, it in enumerate(plan):
        progress(i / len(plan), f"{i + 1}/{len(plan)}: {it['name'][:50]}")
        p = paths.OUTPUT / it["file"]
        if not p.exists():
            continue
        url, name, sha = host(cfg, p)
        row = dict(it, video_url=url, repo_name=name, repo_sha=sha)
        if pub["facebook"]:
            row["fb_video_id"] = fb_schedule(cfg, p, it["caption"], it["unix"])
        out.append(row)
        done.add(it["file"])
        PUBLISHED.write_text(json.dumps(sorted(done)))
        if cfg.get("delete_after"):
            recycle(p)
    PLAN.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    public_rows = [{k: r[k] for k in ("n", "time", "unix", "video_url", "caption", "type", "file") if k in r} for r in out]
    body = {"message": "plan", "content": base64.b64encode(json.dumps(public_rows, indent=1, ensure_ascii=False).encode()).decode()}
    old = _gh(cfg, "GET", "contents/plan.json")
    if old.ok:
        body["sha"] = old.json()["sha"]
    _gh(cfg, "PUT", "contents/plan.json", json=body)
    progress(1.0, "Plan published")
    return {"scheduled": len(out)}


def verify() -> list:
    cfg, rows = load(), []
    try:
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
    except Exception:
        return rows
    for it in plan:
        r = {"n": it["n"], "time": it["time"][5:16].replace("T", " "), "name": it["name"][:48], "facebook": "-", "link": "-"}
        try:
            if it.get("fb_video_id"):
                v = requests.get(f"https://graph.facebook.com/{GRAPH}/{it['fb_video_id']}", params={"fields": "scheduled_publish_time,description,status",
                                                                                                    "access_token": cfg["fb_page_token"]}, timeout=30).json()
                sp = v.get("scheduled_publish_time")
                want = dt.datetime.fromisoformat(it["time"])
                got = dt.datetime.fromisoformat(sp.replace("Z", "+00:00")) if isinstance(sp, str) else None
                same = got is not None and abs((got - want).total_seconds()) < 90 and (v.get("description") or "").strip() == it["caption"].strip()
                r["facebook"] = "ok" if same else "CHECK"
            r["link"] = "ok" if requests.head(it["video_url"], timeout=20).status_code == 200 else "MISSING"
        except Exception as e:
            r["facebook"] = "error"
        rows.append(r)
    return rows


# ------------------------------------------------------------------ VPS package
def vps_package() -> bytes:
    cfg = load()
    src = (Path(__file__).parent / "vps_poster.py").read_text(encoding="utf-8")
    url = f"https://raw.githubusercontent.com/{cfg['github_repo'] or 'OWNER/REPO'}/main/plan.json"
    src = src.replace("https://raw.githubusercontent.com/Shani0017/fragspree-media/main/plan.json", url)
    readme = ("VPS setup, step by step\n=======================\n"
              "(The same steps are in the app: Guide > 4e.)\n\n"
              "WINDOWS VPS\n"
              "1. Copy this whole folder to the VPS, for example to C:\\poster\n"
              "2. Open PowerShell as administrator. Check Python:  python --version\n"
              "   If it is not recognized, install Python 3.11 (python.org, tick 'Add to PATH'), then reopen PowerShell.\n"
              "3. cd C:\\poster   then   python -m pip install requests\n"
              "4. notepad C:\\poster\\.env   and write two lines:  IG_USER_ID=...   IG_TOKEN=...\n"
              "5. Test:  python vps_poster.py --dry     (should print: started (dry run))\n"
              "6. Start it so it survives restarts - run in PowerShell:\n"
              "   $py = (Get-Command python).Source\n"
              "   $a = New-ScheduledTaskAction -Execute $py -Argument \"C:\\poster\\vps_poster.py\" -WorkingDirectory \"C:\\poster\"\n"
              "   $t = New-ScheduledTaskTrigger -AtStartup\n"
              "   Register-ScheduledTask -TaskName Poster -Action $a -Trigger $t -RunLevel Highest -User SYSTEM -Force\n"
              "   Start-ScheduledTask -TaskName Poster\n\n"
              "LINUX VPS\n"
              "1. Copy this folder to ~/poster      2. cd ~/poster && python3 -m pip install --user requests\n"
              "3. Create .env with IG_USER_ID and IG_TOKEN (copy .env.template), then chmod 600 .env\n"
              "4. python3 vps_poster.py --dry   then   nohup python3 vps_poster.py > /dev/null 2>&1 &\n\n"
              "WHAT IT DOES\n"
              "It reads the plan from your GitHub repo, prepares each reel 10 minutes before its time and publishes it at the time.\n"
              "A new plan is picked up automatically. Look at vps_poster.log to see what happened.\n")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("vps_poster.py", src)
        z.writestr(".env.template", "IG_USER_ID=\nIG_TOKEN=\n")
        z.writestr("README.txt", readme)
    return buf.getvalue()


def make_permanent(app_id: str, app_secret: str, user_token: str) -> dict:
    """short-lived User token + app id/secret -> never-expiring Page token, saved in the config (secrets are not stored)"""
    cfg = load()
    if not cfg["fb_page_id"]:
        raise RuntimeError("Enter the Facebook Page ID first (Accounts), then press Save.")
    r = requests.get(f"https://graph.facebook.com/{GRAPH}/oauth/access_token", params={
        "grant_type": "fb_exchange_token", "client_id": app_id, "client_secret": app_secret, "fb_exchange_token": user_token}, timeout=30).json()
    if "access_token" not in r:
        raise RuntimeError("Facebook said: " + str(r.get("error", {}).get("message", r)))
    p = requests.get(f"https://graph.facebook.com/{GRAPH}/{cfg['fb_page_id']}", params={"fields": "name,access_token", "access_token": r["access_token"]}, timeout=30).json()
    if "access_token" not in p:
        raise RuntimeError("Could not get the Page token: " + str(p.get("error", {}).get("message", p)))
    d = requests.get("https://graph.facebook.com/debug_token", params={"input_token": p["access_token"], "access_token": p["access_token"]}, timeout=30).json().get("data", {})
    save({"fb_page_token": p["access_token"]})
    exp = d.get("expires_at", 0)
    return {"page": p.get("name", ""), "expires": "never" if not exp else f"in {round((exp - time.time()) / 86400)} days"}
