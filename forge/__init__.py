"""AI Content Creator - make short vertical videos (balls, music, math, story) from your own machine."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else "0.0.0"
REPO = "Shani0017/AI-Content-Creator"
BRANCH = "main"
