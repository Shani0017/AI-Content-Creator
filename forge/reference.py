"""Reference link -> analysis -> recipe. The reference is only studied (pacing, palette, topic, tone). The new video is original."""
import colorsys
import json
import re
import subprocess

from . import llm, paths, speech


def download(url: str, progress=None) -> str:
    import yt_dlp
    out = paths.CACHE / "reference"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("ref.*"):
        old.unlink(missing_ok=True)
    opts = {"outtmpl": str(out / "ref.%(ext)s"), "format": "best[height<=720]/best", "quiet": True, "noplaylist": True,
            "ffmpeg_location": str(paths.FFMPEG.rsplit("\\", 1)[0]) if "\\" in paths.FFMPEG else None,
            "progress_hooks": [lambda d: progress and d.get("total_bytes") and progress(d["downloaded_bytes"] / d["total_bytes"], "Downloading reference")]}
    opts = {k: v for k, v in opts.items() if v is not None}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    files = sorted(out.glob("ref.*"))
    if not files:
        raise RuntimeError("Could not download that link. Try a direct video link.")
    return str(files[0]), {"title": info.get("title", "") or "", "uploader": info.get("uploader", ""), "description": (info.get("description") or "")[:600]}


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def stats(path: str) -> dict:
    r = _run([paths.FFMPEG, "-hide_banner", "-i", path])
    txt = r.stderr
    dur = 0.0
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", txt)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    m = re.search(r"(\d{3,5})x(\d{3,5})", txt)
    wh = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    # scene cuts -> pacing
    r = _run([paths.FFMPEG, "-hide_banner", "-i", path, "-vf", "select='gt(scene,0.28)',showinfo", "-an", "-f", "null", "-"])
    cuts = len(re.findall(r"pts_time:", r.stderr))
    avg = dur / (cuts + 1) if dur else 0
    return {"duration_s": round(dur, 1), "width": wh[0], "height": wh[1], "cuts": cuts, "avg_shot_s": round(avg, 1),
            "pacing": "fast" if avg < 2.5 else ("medium" if avg < 5 else "slow")}


def palette(path: str, n=5):
    """dominant colours from a few evenly spaced frames"""
    from PIL import Image
    pics = []
    d = stats_duration(path)
    for i in range(1, 7):
        out = paths.CACHE / f"ref_f{i}.jpg"
        _run([paths.FFMPEG, "-v", "error", "-y", "-ss", f"{d * i / 7:.2f}", "-i", path, "-frames:v", "1", "-vf", "scale=160:-1", str(out)])
        if out.exists():
            pics.append(Image.open(out).convert("RGB"))
    if not pics:
        return []
    w = sum(p.width for p in pics)
    sheet = Image.new("RGB", (w, pics[0].height))
    x = 0
    for p in pics:
        sheet.paste(p, (x, 0))
        x += p.width
    q = sheet.quantize(colors=n, method=Image.MEDIANCUT)
    pal = q.getpalette()[:n * 3]
    return [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]


def stats_duration(path):
    return stats_cache.get(path, 30.0)


stats_cache = {}


def analyze(url: str, progress=None) -> dict:
    p = progress or (lambda f, m: None)
    p(0.05, "Downloading the reference")
    path, meta = download(url, lambda f, m: p(0.05 + 0.25 * f, m))
    p(0.32, "Measuring pacing")
    st = stats(path)
    stats_cache[path] = st["duration_s"] or 30.0
    p(0.4, "Reading the colours")
    pal = palette(path)
    p(0.5, "Transcribing the audio")
    wav = paths.CACHE / "ref_audio.wav"
    _run([paths.FFMPEG, "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    try:
        transcript = speech.transcribe_file(str(wav)) if wav.exists() else ""
    except Exception:
        transcript = ""
    p(0.75, "Asking the AI to study it")
    try:
        recipe = llm.analyze_reference(transcript, st, meta.get("title", ""), meta.get("description", ""))
    except Exception:                                   # no model installed / Ollama off: still give a useful recipe from the measurements
        recipe = llm.heuristic_recipe(transcript, meta.get("title", ""), meta.get("description", ""), st)
    recipe.update({"stats": st, "palette": [list(c) for c in pal], "transcript": transcript[:1500], "source_title": meta.get("title", ""),
                   "has_speech": len(transcript.split()) >= 8})
    p(1.0, "Analysis ready")
    return recipe
