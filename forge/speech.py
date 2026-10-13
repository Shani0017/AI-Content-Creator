import os
"""Text-to-speech (Kokoro, offline) and word timings (faster-whisper, offline), plus a few synthesised sound effects."""
import math
import threading
import urllib.request

import numpy as np

from . import paths, settings

SR = 44100
_tts = None
_asr = None
_lock = threading.Lock()


def models_ready() -> dict:
    return {"tts": paths.KOKORO_MODEL.exists() and paths.KOKORO_VOICES.exists()}


def download_models(on_progress=None):
    """fetch the Kokoro voice files (about 340 MB) into models/"""
    items = list(paths.KOKORO_URLS.items())
    for i, (dest, url) in enumerate(items):
        if dest.exists():
            continue
        tmp = dest.with_suffix(dest.suffix + ".part")
        with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length", 0))
            got = 0
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
                if on_progress and total:
                    on_progress((i + got / total) / len(items), f"Downloading {dest.name}")
        tmp.replace(dest)


def _kokoro():
    global _tts
    with _lock:
        if _tts is None:
            from kokoro_onnx import Kokoro
            if not models_ready()["tts"]:
                raise RuntimeError("Voice model missing. Open Settings > Setup and download the voice files.")
            _tts = Kokoro(str(paths.KOKORO_MODEL), str(paths.KOKORO_VOICES))
        return _tts


def _whisper():
    global _asr
    with _lock:
        if _asr is None:
            from faster_whisper import WhisperModel
            _asr = WhisperModel(settings.get("whisper_model"), device="cpu", compute_type="int8", download_root=str(paths.MODELS / "whisper"))
        return _asr


def speak(text: str, voice: str = None, speed: float = 1.04):
    """-> (float32 mono array at 24 kHz, sample rate)"""
    k = _kokoro()
    s, sr = k.create(text, voice=voice or settings.get("voice"), speed=speed, lang="en-us")
    return np.asarray(s, np.float32), sr


def words(wav: np.ndarray, sr: int, text: str):
    """word timestamps for an audio array. Falls back to even spacing if whisper is not available."""
    import soundfile as sf
    try:
        tmp = paths.CACHE / f"_asr_{os.getpid()}.wav"
        sf.write(tmp, wav, sr)
        segs, _ = _whisper().transcribe(str(tmp), word_timestamps=True, language="en", beam_size=5)
        out = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for sg in segs for w in sg.words]
        if out:
            return out
    except Exception:
        pass
    toks = text.split()
    dur = len(wav) / sr
    tot = sum(len(t) + 1 for t in toks)
    t, out = 0.0, []
    for tk in toks:
        d = dur * (len(tk) + 1) / tot
        out.append({"w": tk, "s": round(t, 3), "e": round(t + d, 3)})
        t += d
    return out


def transcribe_file(path: str) -> str:
    segs, _ = _whisper().transcribe(str(path), language=None, beam_size=3)
    return " ".join(s.text.strip() for s in segs)


# ------------------------------------------------------------------ sound effects
def _env(n, decay):
    t = np.arange(n) / SR
    return np.exp(-t * decay)


def sfx(kind: str) -> np.ndarray:
    n = int(0.28 * SR)
    t = np.arange(n) / SR
    if kind == "pop":
        s = np.sin(2 * np.pi * (480 + 900 * np.exp(-t * 40)) * t) * _env(n, 24)
    elif kind == "hit":
        s = np.sin(2 * np.pi * (70 + 120 * np.exp(-t * 30)) * t) * _env(n, 14) + (np.random.default_rng(3).random(n) * 2 - 1) * _env(n, 60) * 0.3
    elif kind == "buzz":
        n = int(0.4 * SR)
        t = np.arange(n) / SR
        s = np.sign(np.sin(2 * np.pi * 110 * t)) * 0.35 * _env(n, 5) + np.sin(2 * np.pi * 165 * t) * 0.2 * _env(n, 5)
    elif kind == "chime":
        n = int(0.9 * SR)
        t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * t) * _env(n, 4 + i) * a for i, (f, a) in enumerate(((784, 0.5), (1175, 0.35), (1568, 0.25))))
    else:
        s = np.zeros(n)
    return (s * 0.5).astype(np.float32)


def music_bed(seconds: float, bpm: int = 92, key: int = 0, vol: float = 0.05) -> np.ndarray:
    """soft looping pad + plucks so the voice-over is not bare"""
    n = int(seconds * SR)
    out = np.zeros(n, np.float32)
    beat = 60.0 / bpm
    prog = [(0, 4, 7), (9, 0, 4), (5, 9, 0), (7, 11, 2)]
    t = np.arange(n) / SR
    for bar in range(int(seconds / (beat * 4)) + 1):
        chord = prog[bar % 4]
        a, b = int(bar * beat * 4 * SR), min(n, int((bar + 1) * beat * 4 * SR))
        if a >= n:
            break
        seg = np.zeros(b - a)
        tt = t[a:b]
        for semi in chord:
            f = 261.63 * 2 ** ((semi + key) / 12) / 2
            seg += np.sin(2 * np.pi * f * tt) * 0.5 + np.sin(2 * np.pi * f * 2 * tt) * 0.15
        fade = np.minimum(1, np.minimum((tt - tt[0]) / 0.3, (tt[-1] - tt) / 0.3))
        out[a:b] += (seg * fade * vol / 3).astype(np.float32)
        for k in range(8):                                        # eighth-note plucks
            i0 = a + int(k * beat / 2 * SR)
            f = 261.63 * 2 ** ((chord[k % 3] + key) / 12) * 2
            L = int(0.35 * SR)
            if i0 + L < n:
                tp = np.arange(L) / SR
                out[i0:i0 + L] += (np.sin(2 * np.pi * f * tp) * np.exp(-tp * 9) * vol * 0.9).astype(np.float32)
    return out

