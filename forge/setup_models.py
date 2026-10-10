"""python -m forge.setup_models  -> downloads the Kokoro voice files into models/ with a simple progress line"""
import sys

from . import paths, speech


def main():
    if speech.models_ready()["tts"]:
        print("Voice files already present.")
        return 0
    last = [-1]

    def prog(frac, msg):
        pct = int(frac * 100)
        if pct != last[0]:
            last[0] = pct
            print(f"\r{msg}: {pct}%", end="", flush=True)

    speech.download_models(prog)
    print("\nVoice files ready:", paths.MODELS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
