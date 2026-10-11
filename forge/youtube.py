"""YouTube scheduling: you upload the videos in YouTube Studio as Private (any number, in batches), the app then writes the title, description,
tags and the publish time of each one, using the same post times as Facebook / Instagram.
Sign-in is Google's standard OAuth for desktop apps; the token stays in data/youtube.json on this computer."""
import datetime as dt
import json
import re
import threading
import time
import urllib.parse

import requests

from . import jobs, paths, publisher

CFG = paths.DATA / "youtube.json"
SCOPE = "https://www.googleapis.com/auth/youtube"
API = "https://www.googleapis.com/youtube/v3"
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
_cache = {"tok": "", "exp": 0.0}
_lock = threading.Lock()


def load() -> dict:
    try:
        return json.loads(CFG.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write(d: dict):
    CFG.write_text(json.dumps(d, indent=1), encoding="utf-8")


def public() -> dict:
    d = load()
    return {"client_id": d.get("client_id", ""), "client_secret": "********" if d.get("client_secret") else "",
            "has_client": bool(d.get("client_id") and d.get("client_secret")), "signed_in": bool(d.get("refresh_token")), "channel": d.get("channel", "")}


def save_client(client_id: str, client_secret: str) -> dict:
    d = load()
    if client_id:
        d["client_id"] = client_id.strip()
    if client_secret and client_secret != "********":
        d["client_secret"] = client_secret.strip()
    _write(d)
    return public()


# ------------------------------------------------------------------ sign-in
def auth_url(redirect: str) -> str:
    d = load()
    if not (d.get("client_id") and d.get("client_secret")):
        raise RuntimeError("Enter the Client ID and Client secret first, then press Save.")
    return AUTH_URI + "?" + urllib.parse.urlencode({"client_id": d["client_id"], "redirect_uri": redirect, "response_type": "code", "scope": SCOPE,
                                                    "access_type": "offline", "prompt": "consent"})


def finish_auth(code: str, redirect: str) -> str:
    d = load()
    r = requests.post(TOKEN_URI, data={"code": code, "client_id": d["client_id"], "client_secret": d["client_secret"], "redirect_uri": redirect,
                                       "grant_type": "authorization_code"}, timeout=30).json()
    if "refresh_token" not in r:
        raise RuntimeError("Google did not give a sign-in key: " + str(r.get("error_description") or r.get("error") or r))
    d["refresh_token"] = r["refresh_token"]
    _cache.update(tok=r.get("access_token", ""), exp=time.time() + int(r.get("expires_in", 3000)) - 120)
    try:
        ch = requests.get(f"{API}/channels", params={"part": "snippet", "mine": "true"}, headers={"Authorization": f"Bearer {r['access_token']}"},
                          timeout=30).json()["items"][0]["snippet"]["title"]
        d["channel"] = ch
    except Exception:
        pass
    _write(d)
    return d.get("channel", "")


def sign_out():
    d = load()
    d.pop("refresh_token", None)
    d.pop("channel", None)
    _write(d)
    _cache.update(tok="", exp=0.0)


def _token() -> str:
    with _lock:
        if _cache["tok"] and time.time() < _cache["exp"]:
            return _cache["tok"]
        d = load()
        if not d.get("refresh_token"):
            raise RuntimeError("Not signed in to YouTube yet. Open Publish > YouTube and press Sign in.")
        r = requests.post(TOKEN_URI, data={"client_id": d["client_id"], "client_secret": d["client_secret"], "refresh_token": d["refresh_token"],
                                           "grant_type": "refresh_token"}, timeout=30).json()
        if "access_token" not in r:
            raise RuntimeError("YouTube sign-in expired. Press Sign in again. (" + str(r.get("error_description") or r.get("error")) + ")")
        _cache.update(tok=r["access_token"], exp=time.time() + int(r.get("expires_in", 3000)) - 120)
        return _cache["tok"]


def _get(path, **params):
    r = requests.get(f"{API}/{path}", params=params, headers={"Authorization": f"Bearer {_token()}"}, timeout=30)
    if not r.ok:
        raise RuntimeError("YouTube said: " + r.json().get("error", {}).get("message", r.text[:200]))
    return r.json()


# ------------------------------------------------------------------ videos + schedule
def my_videos() -> list:
    up = _get("channels", part="contentDetails", mine="true")["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        r = _get("playlistItems", part="contentDetails", playlistId=up, maxResults=50, **({"pageToken": tok} if tok else {}))
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    out = []
    for i in range(0, len(ids), 50):
        out += _get("videos", part="snippet,status", id=",".join(ids[i:i + 50]))["items"]
    return out


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower().replace("#shorts", "")).strip()


def _lookup(table: dict, n: str):
    return table.get(n) or next((v for k, v in table.items() if k and n and (k.startswith(n) or n.startswith(k))), None)


def _texts(title: str, caption: str, tags_from: str):
    base = re.sub(r"\s*#shorts\s*$", "", title, flags=re.I).strip()
    yt_title = base[:92] + " #Shorts"
    cap = re.sub(r"Follow (.+?) for", r"Subscribe to \1 for", caption)
    desc = cap.strip() + "\n\n#Shorts"
    tags = re.findall(r"#(\w+)", tags_from) + ["shorts"]
    return yt_title, desc, list(dict.fromkeys(tags))[:15]


def build_schedule(per_day: int = 8, start: str = "") -> list:
    """private, not-yet-scheduled videos -> [{video, when, title, desc, tags, kind, source}]
    videos that are already in the Facebook / Instagram plan keep the plan's time and wording; the rest continue after it"""
    cfg = publisher.load()
    slots = [s.strip() for s in cfg["slots"].split(",") if s.strip()][:per_day]
    tz = dt.datetime.now().astimezone().tzinfo
    try:
        plan = json.loads(publisher.PLAN.read_text(encoding="utf-8"))
    except Exception:
        plan = []
    plan_by = {norm(p["name"]): p for p in plan}
    lib_by = {norm(v["name"]): v for v in jobs.library()}
    ours, rest = [], []
    for v in my_videos():
        st = v["status"]
        if st["privacyStatus"] != "private" or st.get("publishAt"):
            continue
        title = v["snippet"]["title"]
        n = norm(title)
        p, lib = _lookup(plan_by, n), _lookup(lib_by, n)
        if p:
            t, d, g = _texts(title, p["caption"], p["caption"])
            ours.append(dict(video=v, when=dt.datetime.fromisoformat(p["time"]), title=t, desc=d, tags=g, kind=p.get("type", ""), source="same time as the Facebook/Instagram plan"))
        else:
            kind = lib["kind"] if lib else "other"
            cap = publisher.caption({"kind": kind if kind in publisher.HOOKS else "story", "name": lib["name"] if lib else title}, cfg)
            t, d, g = _texts(title, cap, cap)
            rest.append(dict(video=v, title=t, desc=d, tags=g, kind=kind, source="next free slot"))
    last = max((o["when"] for o in ours), default=None)
    day0 = (last.date() + dt.timedelta(days=1)) if last else (dt.date.fromisoformat(start) if start else dt.date.today() + dt.timedelta(days=1))
    by = {}
    for r in sorted(rest, key=lambda r: r["title"]):
        by.setdefault(r["kind"], []).append(r)
    mixed = []
    while any(by.values()):
        for k in list(by):
            if by[k]:
                mixed.append(by[k].pop(0))
    for i, r in enumerate(mixed):
        d = day0 + dt.timedelta(days=i // len(slots))
        r["when"] = dt.datetime.combine(d, dt.time.fromisoformat(slots[i % len(slots)]), tzinfo=tz)
    return sorted(ours + mixed, key=lambda r: r["when"])


def preview(per_day: int = 8, start: str = "") -> list:
    return [{"n": i + 1, "time": r["when"].strftime("%a %d %b %H:%M"), "type": r["kind"], "title": r["title"], "how": r["source"]}
            for i, r in enumerate(build_schedule(per_day, start))]


def run(params: dict, progress=lambda f, m: None) -> dict:
    sched = build_schedule(int(params.get("per_day", 8)), params.get("start", ""))
    if not sched:
        raise RuntimeError("No private videos waiting. Upload videos to YouTube Studio as Private first (Guide, step 5).")
    done = 0
    for i, r in enumerate(sched):
        progress(i / len(sched), f"{i + 1}/{len(sched)}: {r['title'][:50]}")
        v = r["video"]
        body = {"id": v["id"],
                "snippet": {"title": r["title"], "description": r["desc"], "tags": r["tags"], "categoryId": v["snippet"].get("categoryId", "24")},
                "status": {"privacyStatus": "private", "publishAt": r["when"].astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "selfDeclaredMadeForKids": False}}
        resp = requests.put(f"{API}/videos", params={"part": "snippet,status"}, json=body, headers={"Authorization": f"Bearer {_token()}"}, timeout=60)
        if resp.ok:
            done += 1
        elif resp.status_code in (401, 403):
            raise RuntimeError("YouTube refused: " + resp.json().get("error", {}).get("message", "")[:200])
        time.sleep(0.3)
    progress(1.0, f"Scheduled {done} on YouTube")
    return {"scheduled": done}
