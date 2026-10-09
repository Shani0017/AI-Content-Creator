"""Folders and tool locations. Everything the user generates lives under data/ (never touched by updates)."""
import os
import shutil
import sys
from pathlib import Path

from . import ROOT

DATA = ROOT / "data"
MODELS = ROOT / "models"
OUTPUT = ROOT / "output"
CACHE = DATA / "cache"
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
ENGINE = ROOT / "forge" / "engine"
for d in (DATA, MODELS, OUTPUT, CACHE):
    d.mkdir(parents=True, exist_ok=True)


def ffmpeg() -> str:
    """bundled ffmpeg (imageio-ffmpeg ships a static build); falls back to PATH"""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return shutil.which("ffmpeg") or "ffmpeg"


FFMPEG = ffmpeg()
os.environ["FORGE_FFMPEG"] = FFMPEG                       # the physics engine reads this
os.environ["PATH"] = str(Path(FFMPEG).parent) + os.pathsep + os.environ.get("PATH", "")
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

KOKORO_MODEL = MODELS / "kokoro-v1.0.onnx"
KOKORO_VOICES = MODELS / "voices-v1.0.bin"
KOKORO_URLS = {
    KOKORO_MODEL: "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    KOKORO_VOICES: "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}
